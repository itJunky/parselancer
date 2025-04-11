FROM python:3.11-slim

WORKDIR /workdir
#COPY . /workdir
COPY ./requirements.txt .
RUN useradd -u 1001 -m bot 
RUN pip install -r requirements.txt

USER bot
CMD ["python", "/workdir/run_parse.sh"]
