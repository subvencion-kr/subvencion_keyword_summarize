FROM python:3.12-slim

# 기본 패키지 및 Java 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    g++ \
    default-jdk \
    curl \
    wget \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# KoNLPy 실행을 위한 환경변수 설정
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH=$PATH:$JAVA_HOME/bin

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사
COPY requirements.txt .

# 가상환경 생성, 활성화 및 패키지 설치
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 설정
EXPOSE 8000

# 가상환경 활성화 후 FastAPI 애플리케이션 실행
CMD ["sh", "-c", "python3 main.py"]