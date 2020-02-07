FROM python:3.6.4-alpine3.7
MAINTAINER David Chappell <David.Chappell@trincoll.edu>
RUN apk add --no-cache git
RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt && \
    pip install --no-cache-dir lxml>=3.5.0 && \
    apk del .build-deps
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 5000 5000/udp
CMD ["python", "start.py"]
