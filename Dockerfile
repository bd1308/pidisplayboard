# Dockerfile for Dockerizing push_images. Downloading/Displaying can't run in Docker, due to fb limitations
FROM ubuntu:16.04

RUN apt-get update && apt-get install -y python-pip xvfb python-pygame git openssh-server supervisor iceweasel
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN git clone https://github.com/brittondodd/pidisplayboard.git
WORKDIR /pidisplayboard
COPY config.ini /pidisplayboard
COPY push_images.py /pidisplayboard
COPY url_list /pidisplayboard
RUN pip install -r requirements.txt
ADD https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz /opt/
RUN ln -s /opt/geckodriver /usr/bin/geckodriver 

EXPOSE 22
CMD ["/usr/bin/supervisord"]
#RUN python /pidisplayboard/push_images.py

