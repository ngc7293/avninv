FROM python:slim-buster

ARG config_file

COPY requirements.txt /app/avninv/requirements.txt
COPY BUILD.sh /app/avninv/BUILD.sh

WORKDIR /app/avninv
RUN pip install -r requirements.txt

COPY avninv /app/avninv/avninv
COPY google /app/avninv/google
COPY $config_file /app/avninv/config.yaml
RUN ./BUILD.sh

WORKDIR /app/avninv
EXPOSE 9320
ENTRYPOINT [ "python", "-m", "avninv.catalog", "-c", "config.yaml" ]
