import datetime as dt
import pandas as pd
import math
from typing import List
from pandas.tseries.offsets import BDay


def _get_ppaa_batches(asset_count: pd.DataFrame, max_row_limit: int) \
        -> List[List[dt.date]]:
    start_row = asset_count.iloc[0]
    end_row = asset_count.iloc[-1]
    avg_positions = (start_row['assetCount'] + end_row['assetCount']) / 2
    start_date = pd.to_datetime(start_row['date']).date()
    end_date = pd.to_datetime(end_row['date']).date()
    # multiply by 5 because of # fields: pnl, exposure, asset id, report id, date
    days_per_batch = math.ceil(max_row_limit / (avg_positions * 5))
    return _batch_dates(start_date, end_date, days_per_batch)


def _batch_dates(start_date: dt.date, end_date: dt.date, batch_size: int) -> List[List[dt.date]]:
    if (start_date - end_date).days < batch_size:
        return [[start_date, end_date]]
    date_list = []
    curr_end = start_date
    while end_date > curr_end:
        curr_end = (start_date + BDay(batch_size)).date()
        curr_end = curr_end if curr_end < end_date else end_date
        date_batches = [start_date, curr_end]
        date_list.append(date_batches)
        start_date = curr_end + dt.timedelta(days=1)
    return date_list