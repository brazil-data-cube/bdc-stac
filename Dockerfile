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
ARG GIT_COMMIT
ARG BASE_IMAGE=python:3.8-slim-buster
FROM ${BASE_IMAGE}

# Image metadata
LABEL "org.repo.maintainer"="Brazil Data Cube <brazildatacube@inpe.br>"
LABEL "org.repo.title"="Docker image for STAC Server"
LABEL "org.repo.description"="Docker image for SpatioTemporal Asset Catalog (STAC) Server for Brazil Data Cube."
LABEL "org.repo.git_commit"="${GIT_COMMIT}"
LABEL "org.repo.licenses"="GPLv3"

# Build arguments
ARG BDC_STAC_VERSION="1.0.1"
ARG BDC_STAC_INSTALL_PATH="/opt/bdc-stac/${BDC_STAC_VERSION}"

RUN apt-get update -y \
    && apt-get install -y libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

COPY . ${BDC_STAC_INSTALL_PATH}
WORKDIR ${BDC_STAC_INSTALL_PATH}

RUN pip install -e .
RUN pip install gunicorn

EXPOSE 5000

CMD ["gunicorn", "-w4", "--bind=0.0.0.0:5000", "bdc_stac:create_app()"]
