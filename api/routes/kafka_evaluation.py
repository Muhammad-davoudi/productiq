import os
import subprocess
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter

router = APIRouter(prefix="/api/kafka_evaluation", tags=["kafka_evaluation"])

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5433")),
        database=os.getenv("DB_NAME", "digikala_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )

@router.get("/active")
def get_active_simulation():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id as eval_id, status FROM kafka_evaluation_runs WHERE status = 'RUNNING' ORDER BY started_at DESC LIMIT 1;")
        run = cur.fetchone()
        cur.close()
        conn.close()
        if run:
            return {"eval_id": run["eval_id"], "status": "running"}
        return {"eval_id": None, "status": "idle"}
    except Exception:
        return {"eval_id": None, "status": "idle"}

@router.post("/start")
def start_simulation():
    try:
        subprocess.run(["pkill", "-f", "stream_producer.py"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "sentiment_consumer.py"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "clustering_consumer.py"], stderr=subprocess.DEVNULL)

        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        subprocess.Popen(["python", "src/kafka/stream_producer.py"], env=env)
        subprocess.Popen(["python", "src/kafka/sentiment_consumer.py"], env=env)
        subprocess.Popen(["python", "src/kafka/clustering_consumer.py"], env=env)

        run_id = 1
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO kafka_evaluation_runs (status, started_at) VALUES ('RUNNING', NOW()) RETURNING id;")
            res = cur.fetchone()
            if res:
                run_id = res[0]
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass

        return {"status": "started", "eval_id": run_id}
    except Exception:
        return {"status": "started", "eval_id": 1}

@router.post("/stop/{eval_id}")
def stop_simulation(eval_id: int):
    try:
        subprocess.run(["pkill", "-f", "stream_producer.py"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "sentiment_consumer.py"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "clustering_consumer.py"], stderr=subprocess.DEVNULL)

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE kafka_evaluation_runs SET status = 'STOPPED', ended_at = NOW() WHERE id = %s;", (eval_id,))
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass

        return {"status": "stopped", "eval_id": eval_id}
    except Exception:
        return {"status": "stopped", "eval_id": eval_id}

@router.get("/status/{eval_id}")
def get_simulation_status(eval_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Sentiment distribution
        cur.execute("SELECT sentiment, COUNT(*) as count FROM kafka_sentiment_results GROUP BY sentiment;")
        sentiment_dist = cur.fetchall()

        # Clustering distribution
        cur.execute("SELECT cluster_label as cluster, COUNT(*) as count FROM kafka_clustering_results GROUP BY cluster_label;")
        clustering_dist = cur.fetchall()

        # Total counts
        cur.execute("SELECT COUNT(*) as cnt FROM kafka_sentiment_results;")
        sent_count = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) as cnt FROM kafka_clustering_results;")
        clust_count = cur.fetchone()["cnt"]

        cur.close()
        conn.close()

        return {
            "eval_id": eval_id,
            "status": "running",
            "sentiment_distribution": sentiment_dist,
            "clustering_distribution": clustering_dist,
            "sentiment_stats": {"messages": sent_count},
            "clustering_stats": {"messages": clust_count}
        }
    except Exception:
        return {
            "eval_id": eval_id,
            "status": "running",
            "sentiment_distribution": [],
            "clustering_distribution": [],
            "sentiment_stats": {"messages": 0},
            "clustering_stats": {"messages": 0}
        }

@router.post("/reset")
def reset_simulation():
    try:
        subprocess.run(["pkill", "-f", "stream_producer.py"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "sentiment_consumer.py"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "clustering_consumer.py"], stderr=subprocess.DEVNULL)

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("TRUNCATE TABLE kafka_sentiment_results, kafka_clustering_results, kafka_evaluation_runs RESTART IDENTITY CASCADE;")
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass

        return {"status": "reset_successful"}
    except Exception:
        return {"status": "reset_successful"}
