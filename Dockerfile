FROM python:3.11-slim

WORKDIR /workdir
#COPY . /workdir
COPY ./requirements.txt .
RUN useradd -m bot 
RUN pip install -r requirements.txt

#RUN apt update && apt install -y jq

USER bot
CMD ["python", "/workdir/run_parse.sh"]
