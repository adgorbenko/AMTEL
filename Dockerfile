FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN psql -U postgres -c "CREATE DATABASE file_storage"
RUN psql -U postgres -d file_storage -c "CREATE TABLE file_info (uid VARCHAR(255) PRIMARY KEY, filename VARCHAR(255) NOT NULL, upload_date TIMESTAMP NOT NULL)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]