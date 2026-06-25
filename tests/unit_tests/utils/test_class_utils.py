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

from superset.utils.class_utils import load_class_from_name


def test_load_builtin_class() -> None:
    cls = load_class_from_name("collections.OrderedDict")
    from collections import OrderedDict

    assert cls is OrderedDict


def test_load_nested_module_class() -> None:
    cls = load_class_from_name("os.path.join")
    import os.path

    assert cls is os.path.join


def test_load_empty_string_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Invalid class name"):
        load_class_from_name("")


def test_load_nonexistent_module_raises() -> None:
    with pytest.raises(ModuleNotFoundError):
        load_class_from_name("nonexistent_module_xyz.SomeClass")


def test_load_nonexistent_class_raises() -> None:
    with pytest.raises(AttributeError):
        load_class_from_name("collections.NonExistentClassXyz")
