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

from superset.utils.public_interfaces import (
    compute_class_hash,
    compute_func_hash,
    compute_hash,
    get_warning_message,
)


def _sample_func(a: int, b: str) -> bool:
    return True


class _SampleClass:
    def __init__(self, x: int) -> None:
        self.x = x

    def public_method(self, y: str) -> str:
        return y

    def _private_method(self) -> None:
        pass


def test_compute_func_hash_deterministic() -> None:
    h1 = compute_func_hash(_sample_func)
    h2 = compute_func_hash(_sample_func)
    assert h1 == h2
    assert isinstance(h1, str)
    assert len(h1) > 0


def test_compute_func_hash_different_signatures() -> None:
    def func_a(x: int) -> int:
        return x

    def func_b(x: str) -> str:
        return x

    assert compute_func_hash(func_a) != compute_func_hash(func_b)


def test_compute_class_hash_deterministic() -> None:
    h1 = compute_class_hash(_SampleClass)
    h2 = compute_class_hash(_SampleClass)
    assert h1 == h2
    assert isinstance(h1, str)


def test_compute_hash_dispatches_function() -> None:
    result = compute_hash(_sample_func)
    assert result == compute_func_hash(_sample_func)


def test_compute_hash_dispatches_class() -> None:
    result = compute_hash(_SampleClass)
    assert result == compute_class_hash(_SampleClass)


def test_compute_hash_invalid_object() -> None:
    with pytest.raises(Exception, match="Invalid object"):
        compute_hash(42)  # type: ignore


def test_get_warning_message_contains_info() -> None:
    msg = get_warning_message(_sample_func, "expected_hash_123")
    assert "_sample_func" in msg
    assert "expected_hash_123" in msg
    assert "SIP-57" in msg
