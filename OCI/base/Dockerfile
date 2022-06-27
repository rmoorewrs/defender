FROM windriver/wrlx-image:full@sha256:6259a1477a12e815966d76b613666054d52b5226645f687307555ca042ab71d4

ENV HOME_DIR /home/wruser
ENV UID=1000
ENV GID=1000
ENV PS1=\h:base-\w$ 

EXPOSE 5000-5010

RUN dnf -y install python3 python3-pip git curl sudo vim locale-base-en-us 
RUN pip3 install flask flask_restful flask_cors requests numpy euclid
RUN groupadd -g ${GID} wruser
RUN useradd -m -u ${UID} -g wruser wruser
RUN usermod -aG sudo wruser
RUN echo 'wruser:wruser' |chpasswd
RUN echo "wruser ALL=(ALL) ALL" >> /etc/sudoers

USER wruser
ENV PATH=$PATH:/home/wruser/.local/.bin
WORKDIR ${HOME_DIR}
RUN echo 'export PS1="\h:base\w\$ "' > ${HOME_DIR}/.bashrc
# moved git clone defender to the derived images

ENV LANG=en_US.UTF-8
CMD ["/bin/bash"]
