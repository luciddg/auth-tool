FROM python:2.7
MAINTAINER Lucid Operations <ops@luciddg.com>

RUN apt-get update \
 && apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev

ADD . /opt/auth-tool

RUN pip install -r /opt/auth-tool/requirements.txt

VOLUME ["/opt/auth-tool/conf/"]

EXPOSE 8080
WORKDIR /opt/auth-tool
CMD ["python", "serve.py"]
