# Nicholas J Uhlhorn
# November 2025
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app 

CMD ["python", "app.py"]

