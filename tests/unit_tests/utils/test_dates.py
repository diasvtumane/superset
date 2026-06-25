# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from datetime import datetime

import pytz

from superset.utils.dates import datetime_to_epoch, EPOCH, now_as_float


def test_epoch_constant() -> None:
    assert EPOCH == datetime(1970, 1, 1)


def test_datetime_to_epoch_at_epoch() -> None:
    result = datetime_to_epoch(datetime(1970, 1, 1))
    assert result == 0.0


def test_datetime_to_epoch_known_date() -> None:
    # 2000-01-01 00:00:00 UTC = 946684800000 ms
    result = datetime_to_epoch(datetime(2000, 1, 1))
    assert result == 946684800000.0


def test_datetime_to_epoch_with_timezone() -> None:
    dttm = pytz.utc.localize(datetime(2000, 1, 1))
    result = datetime_to_epoch(dttm)
    assert result == 946684800000.0


def test_datetime_to_epoch_with_non_utc_timezone() -> None:
    eastern = pytz.timezone("US/Eastern")
    # 2000-01-01 00:00:00 EST = 2000-01-01 05:00:00 UTC
    dttm = eastern.localize(datetime(2000, 1, 1))
    result = datetime_to_epoch(dttm)
    assert result == 946684800000.0 + 5 * 3600 * 1000


def test_datetime_to_epoch_subsecond() -> None:
    dttm = datetime(1970, 1, 1, 0, 0, 1, 500000)  # 1.5 seconds
    result = datetime_to_epoch(dttm)
    assert result == 1500.0


def test_now_as_float_returns_positive() -> None:
    result = now_as_float()
    assert result > 0
    assert isinstance(result, float)
