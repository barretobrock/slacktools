from unittest import (
    TestCase,
    main,
)

from slacktools.db_engine import PSQLClient
from tests.common import (
    get_test_logger,
    make_patcher,
)


class TestPSQLClient(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.log = get_test_logger()

    def setUp(self) -> None:
        self.mock_create_engine = make_patcher(self, 'slacktools.db_engine.create_engine')
        self.mock_url = make_patcher(self, 'slacktools.db_engine.URL')
        self.mock_sessionmacher = make_patcher(self, 'slacktools.db_engine.sessionmaker')
        props = {
            'usr': 'someone',
            'pwd': 'password',
            'host': 'hostyhost',
            'database': 'dateybase',
            'port': 5432,
        }
        self.eng = PSQLClient(props=props, parent_log=self.log)

    def test_init(self):
        self.mock_create_engine.assert_called()
        self.mock_url.create.assert_called()
        self.mock_sessionmacher.assert_called()

    def test_session_mgr(self):
        # Normal ops
        with self.eng.session_mgr():
            self.mock_sessionmacher().assert_called()
        self.mock_sessionmacher()().commit.assert_called()
        self.mock_sessionmacher()().close.assert_called()
        self.mock_sessionmacher()().rollback.assert_not_called()
        # Exception
        with self.assertRaises(Exception):
            with self.eng.session_mgr():
                raise Exception('rollback')
        self.mock_sessionmacher()().rollback.assert_called()


if __name__ == '__main__':
    main()
