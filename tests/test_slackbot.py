import unittest
from .common import (
    get_test_logger,
    random_string
)


class TestSlackBotBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._log = get_test_logger()


if __name__ == '__main__':
    unittest.main()