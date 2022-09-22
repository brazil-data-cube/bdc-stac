#
# This file is part of BDC-STAC.
# Copyright (C) 2022 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
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
