FROM python:3.8

WORKDIR /usr/src/gaia

COPY assets/downloader/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY cdalvaro cdalvaro
COPY scripts/downloader.py .

LABEL \
  maintainer="carlos@cdalvaro.io" \
  org.label-schema.vendor="cdalvaro" \
  org.label-schema.name="Gaia Downloader" \
  org.label-schema.description="Gaia DR2 Downloader" \
  org.label-schema.url="https://github.com/cdalvaro/machine-learning-master-thesis" \
  org.label-schema.vcs-url="https://github.com/cdalvaro/machine-learning-master-thesis.git" \
  org.label-schema.docker.schema-version="1.0" \
  com.cdalvaro.docker-salt-master.license="MIT"

ENTRYPOINT [ "python", "downloader.py" ]
CMD [ "--cluster", "ALL", "--verbose" ]
