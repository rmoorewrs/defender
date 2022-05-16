FROM defender-base

EXPOSE 5000-5010

ENV HOME_DIR /home/wruser
ENV LANG=en_US.UTF-8
USER wruser
RUN echo 'export PS1="\h:driver\w\$ "' >> .bashrc
WORKDIR ${HOME_DIR}/defender
RUN cd /home/wruser/defender && git pull
CMD ["/home/wruser/defender/start_example_driver.sh"]
