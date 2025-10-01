from fastapi import FastAPI
import psutil, datetime
import uvicorn

app = FastAPI()

@app.get("/metrics")
def get_metrics():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "timestamp": datetime.datetime.now().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)