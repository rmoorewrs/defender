#FROM rmoorewrs/defender-base:latest
FROM defender-base-u18

EXPOSE 5000-5010

ENV HOME_DIR /home/wruser
ENV LANG=en_US.UTF-8
USER wruser
RUN echo 'export PS1="\h:server\w\$ "' >> .bashrc
WORKDIR ${HOME_DIR}/defender
CMD ["/home/wruser/defender/start_server.sh"]