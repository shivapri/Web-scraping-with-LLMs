FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip install -r requirements.txt

COPY . /usr/src/app/

CMD [ "python3.10", "main.py"]