# 베이스 이미지: Python 3.9 이상
FROM python:3.11-slim

# ffmpeg 설치
RUN apt-get update && apt-get install -y ffmpeg libglib2.0-0 libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify imports (Debug step)
RUN python -c "import cv2; import fastapi; import uvicorn; import requests; import numpy"

# 소스 코드 복사 (패키지 구조 유지를 위해 backend 폴더 자체를 복사)
COPY backend/ ./backend/
COPY assets/ ./assets/

# PYTHONPATH 설정 (루트 /app 에서 backend 패키지를 찾을 수 있게 함)
ENV PYTHONPATH=/app

# 컨테이너 실행 시 기본 명령어 (예: FastAPI 서버 실행)
# 기본 실행은 FastAPI 서버 
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]