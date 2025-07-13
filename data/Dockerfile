FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir  -r requirements.txt

COPY . .

RUN apt update

RUN  apt install -y ffmpeg

CMD ["fastapi", "run", "app.py", "--port", "8888"]
