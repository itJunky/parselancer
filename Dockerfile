FROM python:3.11-slim

WORKDIR /workdir
#COPY . /workdir
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get -y install busybox openssh-client gosu \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash", "-c", "sleep 100001"]
