FROM python:3.8-slim-buster

RUN apt-get update && \
    apt-get install -y git gcc ncdu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a working directory.
RUN mkdir wd
WORKDIR wd

RUN set -ex && \
    pip install --upgrade pip && \
    pip install dash pandas gunicorn xlrd dash-bootstrap-components && \
    rm -rf /root/.cache

COPY . ./

# Finally, run gunicorn.
CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:8000", "app:server"]
# gunicorn --workers=5 --threads=1 -b 0.0.0.0:8000 app:server
