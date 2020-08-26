FROM python:3.8.2-slim

WORKDIR /usr/src/app
RUN mkdir static

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# RUN apk update && apk add postgresql-dev gcc make python3-dev musl-dev libffi-dev git
RUN apt-get update && apt-get install -y git netcat

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .

COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]