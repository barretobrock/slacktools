import traceback
from typing import (
    Any,
    Dict
)
from contextlib import contextmanager
from sqlalchemy.engine import (
    create_engine,
    URL
)
from sqlalchemy.orm import (
    sessionmaker,
    Session
)
from loguru import logger


class PSQLClient:
    """Creates Postgres connection engine"""

    def __init__(self, props: Dict, parent_log: logger, **kwargs):
        _ = kwargs
        self.log = parent_log.bind(child_name=self.__class__.__name__)
        self.engine = create_engine(URL.create(
            drivername='postgresql+psycopg2',
            username=props.get('usr'),
            password=props.get('pwd'),
            host=props.get('host'),
            port=props.get('port'),
            database=props.get('database')
        ))
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

        self.log.debug('Received request to refresh object...')
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
