FROM defender-base

EXPOSE 5000-5010

ENV HOME_DIR /home/wruser
ENV LANG=en_US.UTF-8
ENV DEFENDER_GIT_REPO=https://github.com/rmoorewrs/defender.git
ENV SERVER_IP=172.17.0.3
ENV SERVER_PORT=5000
ENV OBJECT_NAME=attacker01
ENV RESET=true


USER wruser
WORKDIR ${HOME_DIR}
RUN export PS1="\h:driver\w\$ "
RUN git clone ${DEFENDER_GIT_REPO}

WORKDIR ${HOME_DIR}/defender
COPY scripts/start_example_driver.sh ${HOME_DIR}/defender/start_example_driver.sh
CMD ["/home/wruser/defender/start_example_driver.sh"]
