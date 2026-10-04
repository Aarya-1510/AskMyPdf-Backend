from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.upload import router as upload_router
from app.routers.chat import router as chat_router
from app.routers.summary import router as summary_router
from app.routers.questions import router as questions_router

app = FastAPI(title="AskMyPDF AI")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(summary_router, prefix="/api")
app.include_router(questions_router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "AskMyPDF AI Backend is running!"
    }