import os
import signal
import subprocess
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter

# تنظیم پیشوند مسیرها مستقیماً روی روتر
router = APIRouter(prefix="/api/kafka_evaluation", tags=["kafka_evaluation"])

ACTIVE_PROCESSES = {}

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "digikala_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432)
    )

@router.get("/active")
def get_active_simulation():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, status FROM kafka_evaluation_runs WHERE status = 'running' ORDER BY started_at DESC LIMIT 1;")
    run = cur.fetchone()
    cur.close()
    conn.close()
    if run:
        return {"eval_id": run["id"], "status": "running"}
    return {"eval_id": None, "status": "idle"}

@router.post("/start")
def start_simulation():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id FROM kafka_evaluation_runs WHERE status = 'running' ORDER BY started_at DESC LIMIT 1;")
    existing = cur.fetchone()
    
    if existing:
        eval_id = existing["id"]
        cur.close()
        conn.close()
        return {"eval_id": eval_id, "status": "already_running"}

    cur.execute("INSERT INTO kafka_evaluation_runs (status) VALUES ('running') RETURNING id;")
    eval_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()

    try:
        p_sent = subprocess.Popen(
            ["python3", "src/kafka/sentiment_consumer.py"],
            preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        p_clust = subprocess.Popen(
            ["python3", "src/kafka/clustering_consumer.py"],
            preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        p_prod = subprocess.Popen(
            ["python3", "src/kafka/stream_producer.py", "--batch-size", "5"],
            preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        ACTIVE_PROCESSES[eval_id] = [p_sent, p_clust, p_prod]
    except Exception as e:
        print(f"Subprocess start error: {e}")

    return {"eval_id": eval_id, "status": "started"}

@router.post("/stop/{eval_id}")
def stop_simulation(eval_id: int):
    procs = ACTIVE_PROCESSES.pop(eval_id, [])
    for p in procs:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except Exception:
            pass

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE kafka_evaluation_runs SET status = 'stopped', completed_at = NOW() WHERE id = %s;", (eval_id,))
    conn.commit()
    cur.close()
    conn.close()

    return {"eval_id": eval_id, "status": "stopped"}

@router.get("/status/{eval_id}")
def get_simulation_status(eval_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT status FROM kafka_evaluation_runs WHERE id = %s;", (eval_id,))
    run_row = cur.fetchone()
    current_status = run_row["status"] if run_row else "unknown"

    cur.execute("SELECT sentiment, COUNT(*) as count FROM kafka_sentiment_results GROUP BY sentiment;")
    sentiment_rows = cur.fetchall()

    cur.execute("SELECT cluster_label as cluster, COUNT(*) as count FROM kafka_clustering_results GROUP BY cluster_label;")
    cluster_rows = cur.fetchall()

    total_sentiment_msgs = sum(r["count"] for r in sentiment_rows)
    total_cluster_msgs = sum(r["count"] for r in cluster_rows)
    total_processed = total_sentiment_msgs + total_cluster_msgs

    # سایز بچ نقدها 10 و خوشه‌بندی 5
    sentiment_batches = (total_sentiment_msgs + 9) // 10 if total_sentiment_msgs > 0 else 0
    clustering_batches = (total_cluster_msgs + 4) // 5 if total_cluster_msgs > 0 else 0

    cur.close()
    conn.close()

    return {
        "status": current_status,
        "processed_count": total_processed,
        "sentiment_stats": {
            "messages": total_sentiment_msgs,
            "batches": sentiment_batches
        },
        "clustering_stats": {
            "messages": total_cluster_msgs,
            "batches": clustering_batches
        },
        "sentiment_distribution": sentiment_rows,
        "clustering_distribution": cluster_rows
    }
