#
# This file is part of bdc-stac.
# Copyright (C) 2019 INPE.
#
# bdc-stac is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import pytest


if __name__ == '__main__':
    from bdc_stac_tests.test_app import TestBDCStac
    pytest.main(['--color=auto', '--no-cov', '-v'])
