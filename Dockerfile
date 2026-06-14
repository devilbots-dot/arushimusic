FROM nikolaik/python-nodejs:python3.11-nodejs19

RUN apt-get update && \
    apt-get install -y ffmpeg aria2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD bash start
