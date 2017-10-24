FROM jenkins:2.46.3
MAINTAINER Ilya Shupta <funn17@gmail.com>

USER root
RUN apt-get update \
      && apt-get install -y sudo \
      && rm -rf /var/lib/apt/lists/*
RUN echo "jenkins ALL=NOPASSWD: /usr/local/bin/docker" >> /etc/sudoers

USER jenkins
#COPY plugins.txt /usr/share/jenkins/plugins.txt
#RUN /usr/local/bin/plugins.sh /usr/share/jenkins/plugins.txt
