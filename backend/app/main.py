from fastapi import FastAPI

app = FastAPI(
    title="Pit Wall AI Backend",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "status": "backend running",
        "service": "Pit Wall AI"
    }

@app.get("/health")
def health():
    return {
        "healthy": True
    }