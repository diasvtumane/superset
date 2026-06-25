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
import pytest

from superset.utils.retries import retry_call


def test_retry_call_succeeds_immediately() -> None:
    result = retry_call(lambda: 42)
    assert result == 42


def test_retry_call_with_args() -> None:
    def add(a: int, b: int) -> int:
        return a + b

    result = retry_call(add, fargs=[3, 4])
    assert result == 7


def test_retry_call_with_kwargs() -> None:
    def greet(name: str, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}!"

    result = retry_call(greet, fargs=["World"], fkwargs={"greeting": "Hi"})
    assert result == "Hi, World!"


def test_retry_call_retries_on_exception() -> None:
    call_count = 0

    def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("not yet")
        return "success"

    result = retry_call(
        flaky,
        exception=ValueError,
        max_tries=5,
        interval=0,
    )
    assert result == "success"
    assert call_count == 3


def test_retry_call_gives_up() -> None:
    def always_fails() -> None:
        raise ValueError("always fails")

    with pytest.raises(ValueError, match="always fails"):
        retry_call(
            always_fails,
            exception=ValueError,
            max_tries=2,
            interval=0,
        )
