from fastapi import FastAPI
import psutil, datetime

app = FastAPI()

@app.get("/metrics")
def get_metrics():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "timestamp": datetime.datetime.now().isoformat()
    }
