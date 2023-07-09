from functools import wraps
import threading
from sqlalchemy import create_engine

from gb_python_async01.server.db.model import *
# from gb_python_async01.server.db.errors import *


class ServerStorage():
    def __init__(self, db_url) -> None:
        self.db_engine = create_engine(db_url, echo=False, pool_recycle=7200)
        self.lock = threading.Lock()

    def adm_init_db_tables(self):
        Base.metadata.create_all(self.db_engine)

    def stop(self):
        self.db_engine.dispose()


class ServerDBBaseView():
    def __init__(self, db: ServerStorage) -> None:
        self.db = db
        self.db_engine = db.db_engine


# class ServerDBLock():
#     def __call__(self, func):
#         @wraps(func)
#         def with_lock(*args, **kwargs):
#             view = args[0]  # type: ignore
#             if isinstance(view, ServerDBBaseView):
#                 with view.db.lock:
#                     result = func(*args, **kwargs)
#                 return result
#             raise NotImplemented
#         return with_lock
