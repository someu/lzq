# -*- coding: UTF-8 -*-
import pandas as pd
from sqlalchemy import Column, String, Boolean, Float
from core.sql import ModelBase, engine, Mixin


class KData(ModelBase, Mixin):
    '''K线，日/周/月'''
    __tablename__ = 'k_data'
    id = Column(String(32), primary_key=True)
    code = Column(String(16))  # 股票代码
    open = Column(Float)  # 开盘价
    close = Column(Float)  # 收盘价
    high = Column(Float)  # 最高价
    low = Column(Float)  # 最低价
    volume = Column(Float)  # 成交量
    amount = Column(Float)  # 成交额
    amplitude = Column(Float)  # 振幅
    ttm = Column(Float)  # 涨跌幅
    updown_price = Column(Float)  # 涨跌额
    turnover = Column(Float)  # 换手率
    period = Column(String(8))  # 周期：daily、weekly、monthly
    date = Column(String(16))  # 时间
    adjust = Column(String(4))  # 复权，qfq、hfq、bfq
    is_trading = Column(Boolean)  # 是否处于交易日


KData.metadata.create_all(engine)
