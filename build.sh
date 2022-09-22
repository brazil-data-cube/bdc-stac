#!/usr/bin/env bash
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

echo
echo "Build started..."
echo

echo "NEW TAG - BDC-STAC:"
read BDC_STAC_TAG
IMAGE_BDC_STAC="registry.dpi.inpe.br/brazildatacube/bdc-stac"
IMAGE_BDC_STAC_FULL="${IMAGE_BDC_STAC}:${BDC_STAC_TAG}"
docker build -t ${IMAGE_BDC_STAC_FULL} . --no-cache
docker push ${IMAGE_BDC_STAC_FULL}

echo "Build finished!"