FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .dlt/ ./.dlt/
COPY src/ ./src/

CMD ["sh", "-c", "python src/generate_data.py && python src/ingest_to_bq.py"]