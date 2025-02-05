
FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# ✅ requests를 직접 설치
RUN pip install requests

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
