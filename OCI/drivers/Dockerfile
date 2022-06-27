FROM defender-base

EXPOSE 5000-5010

ENV HOME_DIR /home/wruser
ENV LANG=en_US.UTF-8
ENV DEFENDER_GIT_REPO=https://github.com/rmoorewrs/defender.git
ENV SERVER_IP=172.17.0.3
ENV SERVER_PORT=5000
ENV CONFIG_FILE=config/attacker01
ENV PATH_TYPE=simple



USER wruser
WORKDIR ${HOME_DIR}
RUN export PS1="\h:driver\w\$ "
RUN git clone ${DEFENDER_GIT_REPO}

WORKDIR ${HOME_DIR}/defender
COPY scripts/attacker.sh ${HOME_DIR}/defender/attacker.sh
COPY scripts/defender.sh ${HOME_DIR}/defender/defender.sh
CMD ["/home/wruser/defender/attacker.sh"]
