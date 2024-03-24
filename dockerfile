FROM python:3.10.6-alpine

WORKDIR /usr/src/oldk

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod a+x ./*.py

RUN chmod a+x+r+w ./config/*.json

ENTRYPOINT ["python", "-u", "./main.py" ]