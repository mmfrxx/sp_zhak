FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add --virtual build-deps gcc python3-dev musl-dev && apk add postgresql-dev
RUN mkdir /cds
WORKDIR /cds
ADD requirements.txt /cds/
RUN pip install -r requirements.txt
ADD ./ /cds/
EXPOSE 8000
CMD ["python", "./manage.py", "runserver", "0.0.0.0:8000"]

