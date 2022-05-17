FROM defender-base

EXPOSE 5000-5010

ENV HOME_DIR /home/wruser
ENV LANG=en_US.UTF-8
ENV DEFENDER_GIT_REPO=https://github.com/rmoorewrs/defender.git

USER wruser
RUN echo 'export PS1="\h:server\w\$ "' > ${HOME_DIR}/.bashrc
WORKDIR ${HOME_DIR}
RUN git clone ${DEFENDER_GIT_REPO}

WORKDIR ${HOME_DIR}/defender
CMD ["/home/wruser/defender/start_server.sh"]
