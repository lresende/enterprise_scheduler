FROM jupyter/minimal-notebook

# minimal-notebook leaves user as jovyan
USER root

COPY enterprise_scheduler*.whl /tmp
RUN pip install /tmp/enterprise_scheduler*.whl && \
	rm -f /tmp/enterprise_scheduler*.whl 

COPY bootstrap-enterprise-scheduler.sh /etc/bootstrap-enterprise-scheduler.sh
RUN chown root.root /etc/bootstrap-enterprise-scheduler.sh && \
	chmod 0755 /etc/bootstrap-enterprise-scheduler.sh

CMD ["/etc/bootstrap-enterprise-scheduler.sh"]

USER jovyan

