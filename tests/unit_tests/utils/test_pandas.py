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
import pandas as pd

from superset.utils.pandas import detect_datetime_format


def test_detect_iso_format() -> None:
    series = pd.Series(["2023-01-01 12:00:00", "2023-06-15 08:30:00"])
    assert detect_datetime_format(series) == "%Y-%m-%d %H:%M:%S"


def test_detect_date_only_format() -> None:
    series = pd.Series(["2023-01-01", "2023-06-15", "2024-12-31"])
    assert detect_datetime_format(series) == "%Y-%m-%d"


def test_detect_iso_t_format() -> None:
    series = pd.Series(["2023-01-01T12:00:00", "2023-06-15T08:30:00"])
    assert detect_datetime_format(series) == "%Y-%m-%dT%H:%M:%S"


def test_detect_us_date_format() -> None:
    series = pd.Series(["01/15/2023", "06/20/2023", "12/25/2023"])
    assert detect_datetime_format(series) == "%m/%d/%Y"


def test_detect_compact_format() -> None:
    series = pd.Series(["20230101", "20230615", "20241231"])
    assert detect_datetime_format(series) == "%Y%m%d"


def test_empty_series_returns_none() -> None:
    series = pd.Series([], dtype=str)
    assert detect_datetime_format(series) is None


def test_all_null_returns_none() -> None:
    series = pd.Series([None, None, None])
    assert detect_datetime_format(series) is None


def test_unrecognized_format_returns_none() -> None:
    series = pd.Series(["not a date", "also not", "nope"])
    assert detect_datetime_format(series) is None


def test_numeric_series_converted_to_string() -> None:
    series = pd.Series([20230101, 20230615, 20241231])
    assert detect_datetime_format(series) == "%Y%m%d"
