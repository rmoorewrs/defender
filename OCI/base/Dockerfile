FROM windriver/wrlx-image:full@sha256:6259a1477a12e815966d76b613666054d52b5226645f687307555ca042ab71d4

ENV HOME_DIR /home/wruser
ENV UID=1000
ENV GID=1000
ENV DEFENDER_GIT_REPO=https://github.com/rmoorewrs/defender.git

RUN dnf -y install python3 python3-pip git curl sudo 
RUN pip3 install flask flask_restful flask_cors requests
RUN groupadd -g ${GID} wruser
RUN useradd -m -u ${UID} -g wruser wruser
RUN usermod -aG sudo wruser
RUN echo 'wruser:wruser' |chpasswd

USER wruser
WORKDIR ${HOME_DIR}
RUN git clone ${DEFENDER_GIT_REPO}

ENV LANG=en_US.UTF-8
ENTRYPOINT ["/bin/bash"]