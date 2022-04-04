FROM python:3.10.2

MAINTAINER calgo-lab

# Pre-installed some packages
RUN pip install scrapyd-client poetry

COPY start-job/scripts /workdir
RUN chmod +x /workdir/entrypoint.sh

ENTRYPOINT ["/workdir/entrypoint.sh"]