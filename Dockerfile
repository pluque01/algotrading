FROM python:3.12-rc-slim

RUN apt-get update && apt-get install -y build-essential curl

RUN curl -L https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz/download?use_mirror=deac-ams -o ta-lib.tar.gz \
  && tar -xvzf ta-lib.tar.gz \
  && cd ta-lib \
  && ./configure --prefix=/usr \
  && make \
  && make install \
  && cd .. \
  && rm -rf /app/ta-lib /app/ta-lib.tar.gz

RUN curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 \
  && chmod +x tailwindcss-linux-x64 \
  && mv tailwindcss-linux-x64 /usr/local/bin/tailwindcss

WORKDIR /app

# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --upgrade pip; pip install --no-cache-dir -r requirements.txt
