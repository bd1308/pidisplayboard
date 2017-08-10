# Dockerfile for Dockerizing push_images. Downloading/Displaying can't run in Docker, due to fb limitations
FROM ubuntu:16.04

RUN apt-get update && apt-get install -y python-pip xvfb python-pygame git openssh-server supervisor firefox nodejs npm
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
WORKDIR /pidisplayboard
COPY config.ini /pidisplayboard/
COPY push_images.py /pidisplayboard/
COPY url_list /pidisplayboard/
COPY requirements.txt /pidisplayboard/
RUN pip install -r requirements.txt
ADD https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz /opt/
ADD https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 /opt/
RUN tar -xvf /opt/phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /opt
RUN tar -xvf /opt/geckodriver-v0.18.0-linux64.tar.gz -C /opt
RUN ln -s /opt/geckodriver /usr/bin/geckodriver 
RUN ln -s /opt/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/bin/phantomjs


EXPOSE 22
CMD ["/usr/bin/supervisord"]
#RUN python /pidisplayboard/push_images.py


