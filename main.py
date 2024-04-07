from fastapi import FastAPI
from routes.authentication import router as auth_router
from routes.users import router as users_router
from routes.scores import router as scores_router
from routes.competitions import router as competitions_router
from dotenv import load_dotenv
from config.db import engine
from config.models import Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from utils.exceptions import decode_error_message
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(scores_router)
app.include_router(competitions_router)


# app.me

@app.on_event("startup")
def start_server():
    Base.metadata.create_all(bind=engine)
    print(f"Server is now running on PsORT: 3000")



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_type, field, required = (exc.errors()[0].get("type"),
                                   exc.errors()[0].get("loc")[1],
                                   exc.errors()[0].get("ctx", {}).values())
    print(error_type)
    message = decode_error_message(error_type, field, list(required))
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"detail": message}),
    )


@app.get("/")
async def root():
    return {"message": "Server is running.!."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=3000, log_level="info")
