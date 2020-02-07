FROM python:3.6.4-alpine3.7
MAINTAINER David Chappell <David.Chappell@trincoll.edu>
#RUN apk add --no-cache git
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 5000 5000/udp
CMD ["python", "start.py"]
