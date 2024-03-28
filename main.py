from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Подключение к базе данных
engine = create_engine("postgresql://postgres:postgres@localhost:5432/file_storage")
Session = sessionmaker(bind=engine)
Base = declarative_base()


class FileInfo(Base):
    __tablename__ = "file_info"

    uid = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    upload_date = Column(DateTime, nullable=False)


app = FastAPI()


@app.get("/v1/find")
async def find_files(filename: str = None, date: str = None, UUID: str = None):
    session = Session()

    query = session.query(FileInfo)

    if filename:
        query = query.filter(FileInfo.filename.contains(filename))
    if date:
        query = query.filter(FileInfo.upload_date == date)
    if UUID:
        query = query.filter(FileInfo.uid == UUID)

    return [{"uid": file.uid, "filename": file.filename, "date": file.upload_date} for file in query.all()]


@app.post("/v2/upload")
async def upload_file(file: UploadFile = File(...)):
    session = Session()
    new_file_info = FileInfo(
        uid=str(uuid4()),
        filename=file.filename,
        upload_date=datetime.now()
    )
    session.add(new_file_info)
    session.commit()

    with open(new_file_info.uid, "wb") as f:
        f.write(await file.read())

    return {"uid": new_file_info.uid}


@app.get("/v1/download")
async def download_file(UUID: str):
    try:
        file_path = UUID
        return FileResponse(file_path, media_type='application/octet-stream', filename=UUID)
    except FileNotFoundError:
        raise HTTPException(404)