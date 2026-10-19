import os
import threading
import subprocess
import sys
import psycopg2
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/kafka_evaluation", tags=["Kafka Evaluation"])

state = {
    "active": False,
    "eval_id": None,
    "status": "stopped",
    "threads": []
}


class StartReq(BaseModel):
    speed: Optional[float] = 1.0
    mode: Optional[str] = "standard"


def run_script(script_path):
    try:
        python_exe = sys.executable
        subprocess.run([python_exe, script_path], check=False)
    except Exception as e:
        print(f"[ERROR] Failed to run {script_path}: {e}")


def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "digikala_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgrespassword"),
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", 5432))
    )


@router.post("/start")
def start_eval(req: StartReq = None):
    if state["active"]:
        return {"eval_id": state["eval_id"], "status": "running", "message": "Already running"}

    state["active"] = True
    state["eval_id"] = 1
    state["status"] = "running"

    threads = [
        threading.Thread(target=run_script, args=("src/kafka/sentiment_consumer.py",), daemon=True),
        threading.Thread(target=run_script, args=("src/kafka/clustering_consumer.py",), daemon=True),
        threading.Thread(target=run_script, args=("src/kafka/stream_producer.py",), daemon=True)
    ]

    state["threads"] = threads
    for t in threads:
        t.start()

    return {"eval_id": 1, "status": "running"}


@router.post("/reset")
def reset_eval():
    state["active"] = False
    state["eval_id"] = None
    state["status"] = "stopped"
    state["threads"] = []
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE kafka_sentiment_results, kafka_clustering_results, kafka_evaluation_runs RESTART IDENTITY CASCADE;")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[WARN] Could not truncate Kafka simulation tables in DB: {e}")

    return {"status": "success"}


@router.get("/active")
def get_active():
    return {
        "active": state["active"],
        "eval_id": state["eval_id"],
        "status": "running" if state["active"] else "stopped"
    }


@router.get("/status/{eval_id}")
def get_status(eval_id: int):
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    cluster_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT sentiment, count(*) FROM kafka_sentiment_results GROUP BY sentiment;")
        for row in cur.fetchall():
            sent, cnt = row
            sent_key = str(sent).lower()
            if sent_key in sentiment_counts:
                sentiment_counts[sent_key] = cnt

        cur.execute("SELECT cluster_label, count(*) FROM kafka_clustering_results GROUP BY cluster_label;")
        for row in cur.fetchall():
            lbl, cnt = row
            try:
                if isinstance(lbl, str) and "_" in lbl:
                    c_idx = int(lbl.split("_")[-1])
                else:
                    c_idx = int(lbl)
                if c_idx in cluster_counts:
                    cluster_counts[c_idx] = cnt
            except Exception:
                pass

        cur.close()
        conn.close()
    except Exception as e:
        print(f"[WARN] Could not fetch real metrics from DB: {e}")

    sentiment_distribution = [
        {"sentiment": "positive", "count": sentiment_counts["positive"]},
        {"sentiment": "neutral", "count": sentiment_counts["neutral"]},
        {"sentiment": "negative", "count": sentiment_counts["negative"]},
    ]

    clustering_distribution = [
        {"cluster": 0, "count": cluster_counts[0]},
        {"cluster": 1, "count": cluster_counts[1]},
        {"cluster": 2, "count": cluster_counts[2]},
        {"cluster": 3, "count": cluster_counts[3]},
        {"cluster": 4, "count": cluster_counts[4]},
        {"cluster": 5, "count": cluster_counts[5]},
    ]

    sentiment_messages = sum(sentiment_counts.values())
    clustering_messages = sum(cluster_counts.values())

    return {
        "eval_id": eval_id,
        "status": "running" if state["active"] else "stopped",
        "sentiment_distribution": sentiment_distribution,
        "clustering_distribution": clustering_distribution,
        "sentiment_stats": {
            "messages": sentiment_messages
        },
        "clustering_stats": {
            "messages": clustering_messages
        }
    }


@router.post("/stop/{eval_id}")
def stop_eval(eval_id: int):
    state["active"] = False
    state["status"] = "stopped"
    return {"status": "success", "eval_id": eval_id}
