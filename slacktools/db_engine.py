from contextlib import contextmanager
import traceback
from typing import (
    Any,
    Dict,
)

from loguru import logger
from sqlalchemy.engine import (
    URL,
    Engine,
    create_engine,
)
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)


class DBClient:
    """Creates Postgres connection engine"""

    def __init__(self, engine: Engine):
        self.engine = engine
        self._dbsession = sessionmaker(bind=self.engine)

    @contextmanager
    def session_mgr(self):
        """This sets up a transactional scope around a series of operations"""
        session = self._dbsession()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def refresh_table_object(self, tbl_obj, session: Session = None):
        """Refreshes a table object by adding it to the session, committing and refreshing it before
        removing it from the session"""

        def _refresh(sess: Session, tbl) -> Any:
            # Bind to session
            sess.add(tbl)
            # Prime, pull down changes
            sess.commit()
            # Populate changes to obj
            sess.refresh(tbl)
            # Remove obj from session
            sess.expunge(tbl)

        logger.debug('Received request to refresh db object...')
        if session is None:
            with self.session_mgr() as session:
                tbl_obj = _refresh(sess=session, tbl=tbl_obj)
        else:
            # Working in an existing session
            tbl_obj = _refresh(sess=session, tbl=tbl_obj)
        return tbl_obj

    def log_error_to_db(self, e: Exception, err_tbl, error_type, **kwargs):
        """Logs error info to the service_error_log table"""
        err = err_tbl(
            error_type=error_type,
            error_class=e.__class__.__name__,
            error_text=str(e),
            error_traceback=''.join(traceback.format_tb(e.__traceback__)),
            **kwargs
        )
        with self.session_mgr() as session:
            session.add(err)


class PSQLClient(DBClient):

    def __init__(self, props: Dict, **kwargs):
        self.engine = create_engine(URL.create(
            drivername='postgresql+psycopg2',
            username=props['usr'],
            password=props['pwd'],
            host=props['host'],
            port=props['port'],
            database=props['database']
        ))
        super().__init__(engine=self.engine)


class SQLiteClient(DBClient):

    def __init__(self, props: Dict, **kwargs):
        self.engine = create_engine(URL.create(
            drivername='sqlite',
            database=props['database']
        ))
        super().__init__(engine=self.engine)
