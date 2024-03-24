FROM python:3.10.13
WORKDIR /usr/src/oldk
COPY . .
RUN pip install -r requirements.txt