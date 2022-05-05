# -*- coding: UTF-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from threading import Lock
import pandas as pd

from .logger import logger
from .config import Config

engine = create_engine(Config.OUTPUT_DB_URL, echo=False, encoding="utf-8",)
Session = scoped_session(sessionmaker(bind=engine))
ModelBase = declarative_base()
lock = Lock()


@contextmanager
def safe_sessionmaker(session=Session()):
    try:
        lock.acquire()
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        lock.release()
        session.close()


class Mixin:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def save_to_csv(filename, data, index, **kwags):
        df = pd.DataFrame(i.to_dict() for i in data)
        logger.debug(f"保存数据到 {filename}")

        df.set_index(index, drop=True)
        df.to_csv(filename, **kwags)
        logger.debug(f"保存数据到 {filename} 成功")

    @staticmethod
    def save_to_json(filename, data, index, **kwags):
        df = pd.DataFrame([i.to_dict for i in data])
        df.set_index(index, drop=True)
        df.to_json(filename, **kwags)
        logger.debug(f"保存数据到 {filename}")

    @classmethod
    def query_all(cls, *query):
        with safe_sessionmaker() as session:
            raw_list = session.query(cls).filter(*query).all()
            result = []
            for item in raw_list:
                result.append(item.to_dict())
            return pd.DataFrame(result)

