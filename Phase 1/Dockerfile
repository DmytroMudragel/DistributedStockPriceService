FROM python:3.10-slim-buster
RUN apt-get update
RUN apt-get upgrade -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
CMD ["/bin/bash", "-c", "while true; do bash -l; done"]