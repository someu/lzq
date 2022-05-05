import requests
import pandas as pd
import akshare as ak
from core.config import Config
from core.run_with_pool import run_with_pool
from model.kdata import KData

# from core.sql import safe_sessionmaker
from core.logger import logger


def code_id_map_em() -> dict:
    url = "http://80.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "5000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:1 t:2,m:1 t:23",
        "fields": "f12",
        "_": "1623833739532",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if not data_json["data"]["diff"]:
        return dict()
    temp_df = pd.DataFrame(data_json["data"]["diff"])
    temp_df["market_id"] = 1
    temp_df.columns = ["sh_code", "sh_id"]
    code_id_dict = dict(zip(temp_df["sh_code"], temp_df["sh_id"]))
    params = {
        "pn": "1",
        "pz": "5000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0 t:6,m:0 t:80",
        "fields": "f12",
        "_": "1623833739532",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if not data_json["data"]["diff"]:
        return dict()
    temp_df_sz = pd.DataFrame(data_json["data"]["diff"])
    temp_df_sz["sz_id"] = 0
    code_id_dict.update(dict(zip(temp_df_sz["f12"], temp_df_sz["sz_id"])))
    params = {
        "pn": "1",
        "pz": "5000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0 t:81 s:2048",
        "fields": "f12",
        "_": "1623833739532",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if not data_json["data"]["diff"]:
        return dict()
    temp_df_sz = pd.DataFrame(data_json["data"]["diff"])
    temp_df_sz["bj_id"] = 0
    code_id_dict.update(dict(zip(temp_df_sz["f12"], temp_df_sz["bj_id"])))
    return code_id_dict


def find_index(l, v):
    for i in range(len(l)):
        if l[i] == v:
            return i
    return -1


def stock_zh_a_hist(
    symbol: str,
    code_id: str,
    trading_dates: list,
    period: str = "daily",
    adjust: str = "hfq",
):
    """
    symbol: 代码
    period: 周期: daily,weekly,monthly
    code_id: 市场id
    adjust: 复权: qfq,hfq,bfq
    """
    logger.debug(f"下载 {symbol} {period} {adjust} 行情数据")
    adjust_dict = {"qfq": "1", "hfq": "2", "bfq": "0"}
    period_dict = {"daily": "101", "weekly": "102", "monthly": "103"}
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": period_dict[period],
        "fqt": adjust_dict[adjust],
        "secid": f"{code_id}.{symbol}",
        "beg": "0",
        "end": "20500000",
        "_": "1623766962675",
    }
    r = requests.get(url, params=params)
    data_json = r.json()

    kdatas = []
    start_date = data_json["data"]["klines"][0].split(",")[0]
    start_index = offset_index = find_index(trading_dates, start_date)
    end_index = len(trading_dates) - 1
    if start_index == -1:
        logger.warn(f"无效的日期 {start_date}")
        return
    for item in data_json["data"]["klines"]:
        [
            date,
            open,
            close,
            high,
            low,
            volume,
            amount,
            amplitude,
            ttm,
            updown_price,
            turnover,
        ] = item.split(",")
        if start_index < offset_index < end_index:
            last_kdata = kdatas[len(kdatas) - 1]
            while date > trading_dates[offset_index + 1]:
                # 填充停牌
                kdatas.append(
                    KData(
                        code=symbol,
                        adjust=adjust,
                        date=trading_dates[offset_index + 1],
                        open=last_kdata["close"],
                        close=last_kdata["close"],
                        high=last_kdata["close"],
                        low=last_kdata["close"],
                        volume=0,
                        amount=0,
                        amplitude=0,
                        ttm=0,
                        updown_price=0,
                        turnover=0,
                        is_trading=False,
                    )
                )
                offset_index += 1
        kdatas.append(
            KData(
                code=symbol,
                adjust=adjust,
                date=date,
                open=open,
                close=close,
                high=high,
                low=low,
                volume=volume,
                amount=amount,
                amplitude=amplitude,
                ttm=ttm,
                updown_price=updown_price,
                turnover=turnover,
                is_trading=True,
            )
        )
        offset_index += 1
    logger.debug(f"保存 {len(kdatas)} 条数据")
    KData.save_to_csv(
        f"{Config.OUTPUT_DIR}/{symbol}_{period}_{adjust}.csv", kdatas, "date"
    )
    # with safe_sessionmaker() as session:
    #     session.query(KData).filter(
    #         KData.code == symbol, KData.period == period, KData.adjust == adjust,
    #     ).delete()
    #     session.add_all(kdatas)


def download_all_stock_zh_a_hist():
    code_id_map = code_id_map_em()
    info = ak.stock_zh_index_daily(symbol="sh000001")
    trading_dates = list(info["date"].apply(lambda x: x.strftime("%Y-%m-%d")))

    params = []
    for code in code_id_map:
        params.append((code, code_id_map[code], trading_dates))

    run_with_pool(stock_zh_a_hist, Config.RequestWorker, params, desc="下载股票行情数据")

