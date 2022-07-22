#
# This file is part of Brazil Data Cube STAC Service.
# Copyright (C) 2019-2020 INPE.
#
# Brazil Data Cube STAC Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

FROM python:3.7-slim-buster

# Image metadata
LABEL "org.repo.maintainer"="Brazil Data Cube <brazildatacube@inpe.br>"
LABEL "org.repo.title"="Docker image for STAC Server"
LABEL "org.repo.description"="Docker image for SpatioTemporal Asset Catalog (STAC) Server for Brazil Data Cube."

RUN apt-get update -y \
    && apt-get install -y libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /bdc_stac

WORKDIR /bdc_stac

COPY . .
RUN pip install -e .
RUN pip install gunicorn

EXPOSE 5000

CMD ["gunicorn", "-w4", "--bind=0.0.0.0:5000", "bdc_stac:create_app()"]
