# -*- coding: UTF-8 -*-
import pandas as pd
from sqlalchemy import Column, String, Float
from core.sql import ModelBase, engine, Mixin


class Stock(ModelBase, Mixin):
    """股票"""

    __tablename__ = "stock"
    code = Column(String(16), primary_key=True)  # 股票代码
    name = Column(String(16))  # 简称
    launch_date = Column(String(10))  # 上市日期
    industry = Column(String(16))  # 行业
    total_capitalization = Column(Float)  # 总市值
    flow_capitalization = Column(Float)  # 流通市值
    total_capital = Column(Float)  # 总股本
    flow_capital = Column(Float)  # 流通股本


Stock.metadata.create_all(engine)

