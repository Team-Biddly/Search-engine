# fastapi 동작 테스트
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}

# uvicorn main:app --reload

# localhost:8000 -> Hello World
# localhost:8000/docs -> Swagger UI