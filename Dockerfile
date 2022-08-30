FROM python:3.11-rc-bullseye


COPY requirements.txt requirements.txt

RUN apt-get -y update
run apt -y install wireguard

RUN pip3 install -r requirements.txt

WORKDIR /src
COPY ./*.py /src/
COPY ./*.txt /src/
COPY ./*.crt /src/

CMD [ "python3", "generate-config-auto.py"]
