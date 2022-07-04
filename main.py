import shutil
import uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from extract_pdf import *
import os

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract_references/")
async def create_file(file: UploadFile = File(...)):
  if not file:
    return {"message": "No file sent"}
  else:
    sFile = file.filename.split(".")
    extension = sFile[len(sFile)-1]
    newName = str(uuid.uuid4()) + "." + extension

    with open("resi/"+newName, "wb") as pdf:
      shutil.copyfileobj(file.file, pdf)

    path = str("resi/"+newName)

    data = extract_pdf(path)
    os.remove(path)
    return {
      "status": 200,
      "error": None,
      "message": "Success extract file.",
      "data": data
    }