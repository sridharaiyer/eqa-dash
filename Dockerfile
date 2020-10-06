FROM python:3.8-slim-buster AS compile-image
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc git ncdu

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install dash pandas gunicorn xlrd dash-bootstrap-components

FROM python:3.8-slim-buster AS build-image
COPY --from=compile-image /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
COPY . /wd
WORKDIR /wd
CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:8000", "app:server"]
