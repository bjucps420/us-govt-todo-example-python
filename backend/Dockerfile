FROM python:3.9.7

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

CMD python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000