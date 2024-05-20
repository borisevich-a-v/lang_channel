FROM python:3.11

ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install --yes libraqm-dev apt-utils

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY .env .env
COPY service_account.json /root/.config/gspread/service_account.json

COPY src/ src/
WORKDIR /app/src/

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "50051"]
