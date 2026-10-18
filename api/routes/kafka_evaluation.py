import os
import subprocess
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/kafka_evaluation", tags=["kafka_evaluation"])

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgrespassword@db:5432/digikala_db")
TARGET_SCRIPTS = ["stream_producer.py", "sentiment_consumer.py", "clustering_consumer.py"]

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

def kill_kafka_processes():
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
            if any(any(script in arg for script in TARGET_SCRIPTS) for arg in cmdline):
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

@router.post("/start")
def start_kafka_simulation():
    try:
        kill_kafka_processes()
        
        # Run in background detached from uvicorn process group
        subprocess.Popen(["nohup", "python", "/app/src/kafka/sentiment_consumer.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
        subprocess.Popen(["nohup", "python", "/app/src/kafka/clustering_consumer.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
        subprocess.Popen(["nohup", "python", "/app/src/kafka/stream_producer.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO kafka_evaluation_runs (status) VALUES ('RUNNING') RETURNING id;")
        run_id = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "eval_id": str(run_id), "message": "Simulation started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
def reset_kafka_simulation():
    try:
        kill_kafka_processes()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE kafka_evaluation_runs SET status = 'STOPPED' WHERE status = 'RUNNING';")
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Simulation reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active")
def get_active_simulation():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, status, created_at FROM kafka_evaluation_runs ORDER BY id DESC LIMIT 1;")
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {"active": row["status"] == "RUNNING", "eval_id": str(row["id"])}
        return {"active": False, "eval_id": None}
    except Exception as e:
        return {"active": False, "eval_id": None}
