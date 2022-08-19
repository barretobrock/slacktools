import unittest

from tests.common import get_test_logger


class TestSlackSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()


if __name__ == '__main__':
    unittest.main()
