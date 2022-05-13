FROM rmoorewrs/defender-base:latest

EXPOSE 5000-5010

ENV HOME_DIR /home/wruser
ENV LANG=en_US.UTF-8
USER wruser
RUN echo 'export PS1="\h:server\w\$ "' >> .bashrc
WORKDIR ${HOME_DIR}/defender
ENTRYPOINT ["/home/wruser/defender/start_server.sh"]