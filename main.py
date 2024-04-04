from fastapi import FastAPI
from routes.authentication import router as auth_router
from routes.users import router as users_router
from routes.scores import router as scores_router
from dotenv import load_dotenv
from config.db import engine
from config.models import Base

app = FastAPI()

load_dotenv()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(scores_router)


@app.on_event("startup")
def start_server():
    Base.metadata.create_all(bind=engine)

    print(f"Server is now running on PsORT: 3000")


@app.get("/")
async def root():
    return {"message": "Server is running.!."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=3000, log_level="info")
