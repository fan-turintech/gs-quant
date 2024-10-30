"""
Copyright 2019 Goldman Sachs.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

import datetime as dt
from enum import Enum

from dataclasses import dataclass
from dataclasses_json import dataclass_json

from typing import Callable, Tuple, Union

from gs_quant.datetime.relative_date import RelativeDate
from gs_quant.instrument import Instrument


class CalcType(Enum):
    simple = 'simple'
    semi_path_dependent = 'semi_path_dependent'
    path_dependent = 'path_dependent'


@dataclass_json
@dataclass
class CustomDuration:
    durations: Tuple[Union[str, dt.date, dt.timedelta], ...]
    function: Callable[[Tuple[Union[str, dt.date, dt.timedelta], ...]], Union[str, dt.date, dt.timedelta]]

    def __hash__(self):
        return hash((self.durations, self.function))


def make_list(thing):
    if thing is None:
        return []
    if isinstance(thing, str):
        return [thing]
    else:
        try:
            iter(thing)
        except TypeError:
            return [thing]
        else:
            return list(thing)

final_date_cache = {}

def get_final_date(inst, create_date, duration, holiday_calendar=None, trigger_info=None):
    global final_date_cache
    cache_key = (inst, create_date, duration, holiday_calendar)
    if cache_key in final_date_cache:
        return final_date_cache[cache_key]

    result = None
    if duration is None:
        result = dt.date.max
    elif isinstance(duration, (dt.datetime, dt.date)):
        result = duration
    elif hasattr(inst, str(duration)):
        result = getattr(inst, str(duration))
    elif str(duration).lower() == 'next schedule':
        if hasattr(trigger_info, 'next_schedule'):
            result = trigger_info.next_schedule or dt.date.max
        else:
            raise RuntimeError('Next schedule not supported by action')
    elif isinstance(duration, CustomDuration):
        result = duration.function(*(get_final_date(inst, create_date, d, holiday_calendar, trigger_info) for
                                    d in duration.durations))
    else:
        result = RelativeDate(duration, create_date).apply_rule(holiday_calendar=holiday_calendar)

    final_date_cache[cache_key] = result
    return result

def scale_trade(inst: Instrument, ratio: float):
    return inst.scale(ratio)