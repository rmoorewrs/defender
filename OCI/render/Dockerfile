FROM defender-base

EXPOSE 5000-5010

ENV HOME_DIR /home/wruser
ENV LANG=en_US.UTF-8
ENV PS1="renderer%"
USER wruser
RUN echo 'export PS1="\h:render\w\$ "' >> .bashrc
WORKDIR ${HOME_DIR}/defender/renderer
#ENTRYPOINT ["/home/wruser/defender/renderer/serve.sh"]
CMD ["/home/wruser/defender/renderer/serve.sh"]
