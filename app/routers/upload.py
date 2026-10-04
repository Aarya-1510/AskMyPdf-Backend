from fastapi import APIRouter, UploadFile, File, HTTPException
import pymupdf
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are allowed"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = ""

    if file.filename.lower().endswith(".pdf"):
        pdf = pymupdf.open(file_path)

        for page in pdf:
            text += page.get_text()

        pdf.close()

    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "text": text
    }