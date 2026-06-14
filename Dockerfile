FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ffmpeg aria2 curl gnupg nodejs npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash", "start"]
