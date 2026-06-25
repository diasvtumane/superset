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
from typing import Any
from unittest.mock import MagicMock

from superset.utils.dashboard_filter_scopes_converter import (
    convert_filter_scopes,
    copy_filter_scopes,
)


def _make_filter_box(slice_id: int, params: str | None) -> MagicMock:
    fb = MagicMock()
    fb.id = slice_id
    fb.params = params
    return fb


def test_convert_filter_scopes_with_date_filter() -> None:
    json_metadata: dict[Any, Any] = {}
    fb = _make_filter_box(1, '{"date_filter": true}')
    result = convert_filter_scopes(json_metadata, [fb])
    assert 1 in result
    assert "__time_range" in result[1]
    assert result[1]["__time_range"]["scope"] == ["ROOT_ID"]


def test_convert_filter_scopes_with_time_column() -> None:
    json_metadata: dict[Any, Any] = {}
    fb = _make_filter_box(1, '{"show_sqla_time_column": true}')
    result = convert_filter_scopes(json_metadata, [fb])
    assert "__time_col" in result[1]


def test_convert_filter_scopes_with_time_granularity() -> None:
    json_metadata: dict[Any, Any] = {}
    fb = _make_filter_box(1, '{"show_sqla_time_granularity": true}')
    result = convert_filter_scopes(json_metadata, [fb])
    assert "__time_grain" in result[1]


def test_convert_filter_scopes_with_filter_configs() -> None:
    json_metadata: dict[Any, Any] = {}
    params = '{"filter_configs": [{"column": "country"}, {"column": "city"}]}'
    fb = _make_filter_box(1, params)
    result = convert_filter_scopes(json_metadata, [fb])
    assert "country" in result[1]
    assert "city" in result[1]


def test_convert_filter_scopes_with_immune_slices() -> None:
    json_metadata = {"filter_immune_slices": [10, 20]}
    fb = _make_filter_box(1, '{"date_filter": true}')
    result = convert_filter_scopes(json_metadata, [fb])
    immune = result[1]["__time_range"]["immune"]
    assert 10 in immune
    assert 20 in immune


def test_convert_filter_scopes_with_immune_slice_fields() -> None:
    json_metadata = {
        "filter_immune_slice_fields": {"5": ["country"]},
    }
    params = '{"filter_configs": [{"column": "country"}]}'
    fb = _make_filter_box(1, params)
    result = convert_filter_scopes(json_metadata, [fb])
    assert 5 in result[1]["country"]["immune"]


def test_convert_filter_scopes_empty() -> None:
    result = convert_filter_scopes({}, [])
    assert result == {}


def test_convert_filter_scopes_no_params() -> None:
    fb = _make_filter_box(1, None)
    result = convert_filter_scopes({}, [fb])
    assert result == {}


def test_copy_filter_scopes_remaps_ids() -> None:
    old_to_new = {1: 100, 2: 200, 3: 300}
    old_scopes = {
        1: {
            "__time_range": {
                "scope": ["ROOT_ID"],
                "immune": [2, 3],
            }
        }
    }
    result = copy_filter_scopes(old_to_new, old_scopes)
    assert "100" in result
    assert result["100"]["__time_range"]["immune"] == [200, 300]


def test_copy_filter_scopes_skips_missing_ids() -> None:
    old_to_new = {1: 100}
    old_scopes: dict[int, dict[str, dict[str, Any]]] = {
        1: {
            "col": {"scope": ["ROOT_ID"], "immune": [2, 3]},
        },
        99: {
            "col2": {"scope": ["ROOT_ID"], "immune": []},
        },
    }
    result = copy_filter_scopes(old_to_new, old_scopes)
    assert "100" in result
    assert "99" not in result
    # immune IDs 2 and 3 are not in old_to_new, so they are filtered out
    assert result["100"]["col"]["immune"] == []


def test_copy_filter_scopes_empty() -> None:
    result = copy_filter_scopes({}, {})
    assert result == {}
