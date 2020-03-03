import pytest


if __name__ == '__main__':
    from bdc_stac_tests.test_app import TestBDCStac
    pytest.main(['--color=auto', '--no-cov', '-v'])