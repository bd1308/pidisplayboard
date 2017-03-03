# Dockerfile for Dockerizing push_images. Downloading/Displaying can't run in Docker, due to fb limitations
FROM ubuntu:16.04

RUN apt-get update && apt-get install -y python-pip Xvfb python-pygame git openssh-server supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN git clone https://github.com/brittondodd/pidisplayboard.git
RUN pip install -r requirements.txt
WORKDIR /pidisplayboard

EXPOSE 22
CMD ["/usr/bin/supervisord"]


