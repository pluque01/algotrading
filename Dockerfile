FROM python:3.12-rc-slim

RUN apt-get update && apt-get install -y build-essential

RUN apt-get update && apt-get install -y curl

RUN curl -L https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz/download?use_mirror=deac-ams -o ta-lib.tar.gz \
  && tar -xvzf ta-lib.tar.gz \
  && cd ta-lib \
  && ./configure --prefix=/usr \
  && make \
  && make install \
  && cd .. \
  && rm -rf /app/ta-lib /app/ta-lib.tar.gz

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip; pip install -r requirements.txt

RUN pip install TA-Lib

