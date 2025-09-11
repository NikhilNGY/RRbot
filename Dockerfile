FROM python:3.10.8-slim-bullseye

RUN apt update && apt upgrade -y && apt install git -y

COPY requirements.txt /requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade -r /requirements.txt

WORKDIR /RRbot
COPY start.sh /start.sh

# Ensure start.sh is executable
RUN chmod +x /start.sh

CMD ["/bin/bash", "/start.sh"]
