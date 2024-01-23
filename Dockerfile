FROM python:3.12-rc-slim

RUN apt-get update && apt-get install -y build-essential

RUN adduser --disabled-password -u 1001 pythonuser

USER pythonuser

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip; pip install -r requirements.txt