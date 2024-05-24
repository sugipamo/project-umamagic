FROM python:3.8-alpine

COPY main.py /

RUN apk update
RUN apk add curl

CMD ["python", "main.py"]