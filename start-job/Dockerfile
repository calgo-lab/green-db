FROM python:3.10.4

MAINTAINER calgo-lab

# Pre-installed some packages
RUN pip install scrapyd-client poetry

COPY start-job /workdir
RUN chmod +x /workdir/scripts/entrypoint.sh

ENTRYPOINT ["/workdir/scripts/entrypoint.sh"]