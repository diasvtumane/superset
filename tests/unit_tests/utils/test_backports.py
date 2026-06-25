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
from enum import Enum

from superset.utils.backports import StrEnum


class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


def test_strenum_is_str() -> None:
    assert isinstance(Color.RED, str)


def test_strenum_is_enum() -> None:
    assert isinstance(Color.RED, Enum)


def test_strenum_value() -> None:
    assert Color.RED.value == "red"
    assert Color.GREEN.value == "green"


def test_strenum_string_comparison() -> None:
    assert Color.RED == "red"


def test_strenum_name() -> None:
    assert Color.RED.name == "RED"
