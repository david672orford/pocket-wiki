FROM python:3.8.0-alpine3.10
MAINTAINER David Chappell <David.Chappell@trincoll.edu>
ARG uid
COPY requirements.txt /tmp/requirements.txt
RUN apk add --no-cache git \
	&& pip3 install -r /tmp/requirements.txt \
    && apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev \
    && apk add --no-cache libxslt \
    && pip install --no-cache-dir lxml>=3.5.0 \
    && apk del .build-deps \
	&& adduser -u $uid -G users -D app
WORKDIR /app
COPY . .
EXPOSE 5000
USER app
CMD ["python", "start.py"]
