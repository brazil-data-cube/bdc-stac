#
# This file is part of Brazil Data Cube STAC Service.
# Copyright (C) 2019-2020 INPE.
#
# Brazil Data Cube STAC Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

FROM python:3.7-slim-buster

RUN apt-get update -y \
    && apt-get install -y libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p bdc_stac

COPY requirements.txt bdc_stac/
COPY ./bdc_stac bdc_stac/
RUN pip install -r bdc_stac/requirements.txt
RUN pip install gunicorn

EXPOSE 5000

CMD ["gunicorn", "-w4", "--bind=0.0.0.0:5000", "bdc_stac:create_app()"]
