FROM python:3.10.5-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY run.py run.py
COPY src/ src/
COPY .env .env
COPY service_account.json /root/.config/gspread/service_account.json

CMD [ "python3", "run.py"]
