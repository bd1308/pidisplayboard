# Dockerfile for Dockerizing push_images. Downloading/Displaying can't run in Docker, due to fb limitations
FROM ubuntu:16.04

RUN apt-get update && apt-get install -y python-pip xvfb python-pygame git openssh-server supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN git clone https://github.com/brittondodd/pidisplayboard.git
WORKDIR /pidisplayboard
RUN pip install -r requirements.txt

EXPOSE 22
CMD ["/usr/bin/supervisord"]


