FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
  && apk add openssl git \
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add linux-headers

RUN addgroup -S hap \
    && adduser -S -G hap hap

RUN pip install gunicorn
RUN pip install hug
RUN pip install git+https://github.com/digitalhurricane-io/haproxyadmin.git

RUN mkdir /app
COPY . /app

RUN mkdir /socket_dir && chown hap /socket_dir


RUN chown -R hap /app
RUN chmod +x /app/entrypoint

#USER hap

WORKDIR /app

ENTRYPOINT ["/app/entrypoint"]