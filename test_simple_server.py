from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/test")
async def test():
    return {"success": True, "message": "Test API working"}

if __name__ == "__main__":
    print("Starting simple test server on port 8004...")
    uvicorn.run(app, host="localhost", port=8004, log_level="info")
