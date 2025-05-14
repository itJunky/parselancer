FROM python:3.11-slim

WORKDIR /workdir
#COPY . /workdir
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN useradd -u 1001 -m bot 
RUN apt-get update && apt-get -y install busybox
#RUN apt-get update && apt-get -y install cron && \
#    touch /var/log/cron.log && touch /var/run/crond.pid && chown bot /var/run/crond.pid

USER bot
CMD ["python", "/workdir/run_parse.sh"]
