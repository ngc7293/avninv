FROM python:slim-buster

COPY requirements.txt /opt/avninv/requirements.txt
COPY BUILD.sh /opt/avninv/BUILD.sh

WORKDIR /opt/avninv
RUN pip install -r requirements.txt

COPY avninv /opt/avninv/avninv
COPY google /opt/avninv/google
COPY config.docker.yaml /opt/avninv/config.docker.yaml
RUN ./BUILD.sh

WORKDIR /opt/avninv
EXPOSE 9320
ENTRYPOINT [ "python", "-m", "avninv.catalog", "-c", "config.docker.yaml" ]
