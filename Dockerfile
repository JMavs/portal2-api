FROM python:3.10-slim-buster

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "gunicorn", "--workers=4" , "--bind=0.0.0.0:5000", "--log-level=debug", "app:app"]
