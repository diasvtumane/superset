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
from unittest.mock import MagicMock

from superset.utils.feature_flag_manager import FeatureFlagManager


def test_initial_state() -> None:
    mgr = FeatureFlagManager()
    assert mgr.get_feature_flags() == {}
    assert mgr.is_feature_enabled("ANY_FLAG") is False


def test_init_app_merges_flags() -> None:
    mgr = FeatureFlagManager()
    app = MagicMock()
    app.config = {
        "GET_FEATURE_FLAGS_FUNC": None,
        "IS_FEATURE_ENABLED_FUNC": None,
        "DEFAULT_FEATURE_FLAGS": {"A": True, "B": False},
        "FEATURE_FLAGS": {"B": True, "C": True},
    }
    mgr.init_app(app)
    flags = mgr.get_feature_flags()
    assert flags == {"A": True, "B": True, "C": True}


def test_is_feature_enabled_basic() -> None:
    mgr = FeatureFlagManager()
    app = MagicMock()
    app.config = {
        "GET_FEATURE_FLAGS_FUNC": None,
        "IS_FEATURE_ENABLED_FUNC": None,
        "DEFAULT_FEATURE_FLAGS": {"ENABLED": True, "DISABLED": False},
        "FEATURE_FLAGS": {},
    }
    mgr.init_app(app)
    assert mgr.is_feature_enabled("ENABLED") is True
    assert mgr.is_feature_enabled("DISABLED") is False
    assert mgr.is_feature_enabled("NONEXISTENT") is False


def test_get_feature_flags_func() -> None:
    mgr = FeatureFlagManager()

    def custom_func(flags: dict[str, bool]) -> dict[str, bool]:
        flags["INJECTED"] = True
        return flags

    app = MagicMock()
    app.config = {
        "GET_FEATURE_FLAGS_FUNC": custom_func,
        "IS_FEATURE_ENABLED_FUNC": None,
        "DEFAULT_FEATURE_FLAGS": {"A": True},
        "FEATURE_FLAGS": {},
    }
    mgr.init_app(app)
    flags = mgr.get_feature_flags()
    assert flags["INJECTED"] is True
    assert flags["A"] is True


def test_is_feature_enabled_func() -> None:
    mgr = FeatureFlagManager()

    def custom_enabled(feature: str, default: bool) -> bool:
        if feature == "SPECIAL":
            return True
        return default

    app = MagicMock()
    app.config = {
        "GET_FEATURE_FLAGS_FUNC": None,
        "IS_FEATURE_ENABLED_FUNC": custom_enabled,
        "DEFAULT_FEATURE_FLAGS": {"SPECIAL": False, "OTHER": False},
        "FEATURE_FLAGS": {},
    }
    mgr.init_app(app)
    assert mgr.is_feature_enabled("SPECIAL") is True
    assert mgr.is_feature_enabled("OTHER") is False
    assert mgr.is_feature_enabled("UNKNOWN") is False


def test_get_feature_flags_with_is_feature_enabled_func() -> None:
    mgr = FeatureFlagManager()

    def custom_enabled(feature: str, default: bool) -> bool:
        return not default

    app = MagicMock()
    app.config = {
        "GET_FEATURE_FLAGS_FUNC": None,
        "IS_FEATURE_ENABLED_FUNC": custom_enabled,
        "DEFAULT_FEATURE_FLAGS": {"A": True, "B": False},
        "FEATURE_FLAGS": {},
    }
    mgr.init_app(app)
    flags = mgr.get_feature_flags()
    assert flags == {"A": False, "B": True}
