#!/usr/bin/env bash

##### DEPLOY
echo
echo "BUILD STARTED"
echo
echo "NEW TAG - BDC-STAC:"
read BDC_STAC_TAG
IMAGE_BDC_STAC="registry.dpi.inpe.br/brazildatacube/bdc-stac-0.8.0"
IMAGE_BDC_STAC_FULL="${IMAGE_BDC_STAC}:${BDC_STAC_TAG}"
docker build -t ${IMAGE_BDC_STAC_FULL} . --no-cache
docker push ${IMAGE_BDC_STAC_FULL}
