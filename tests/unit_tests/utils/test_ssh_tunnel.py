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

from superset.constants import PASSWORD_MASK
from superset.utils.ssh_tunnel import (
    get_default_port,
    mask_password_info,
    unmask_password_info,
)


def test_mask_password_info_replaces_secrets() -> None:
    tunnel = {
        "server_address": "host",
        "password": "secret123",
        "private_key": "key_data",
        "private_key_password": "key_pass",
    }
    result = mask_password_info(tunnel)
    assert result["password"] == PASSWORD_MASK
    assert result["private_key"] == PASSWORD_MASK
    assert result["private_key_password"] == PASSWORD_MASK
    assert result["server_address"] == "host"


def test_mask_password_info_no_secrets() -> None:
    tunnel = {"server_address": "host", "server_port": 22}
    result = mask_password_info(tunnel)
    assert result == {"server_address": "host", "server_port": 22}


def test_mask_password_info_partial() -> None:
    tunnel = {"server_address": "host", "password": "secret123"}
    result = mask_password_info(tunnel)
    assert result["password"] == PASSWORD_MASK
    assert "private_key" not in result


def test_unmask_password_info_restores_from_model() -> None:
    model = MagicMock()
    model.password = "real_password"  # noqa: S105
    model.private_key = "real_key"
    model.private_key_password = "real_key_pass"  # noqa: S105

    tunnel = {
        "password": PASSWORD_MASK,
        "private_key": PASSWORD_MASK,
        "private_key_password": PASSWORD_MASK,
    }
    result = unmask_password_info(tunnel, model)
    assert result["password"] == "real_password"  # noqa: S105
    assert result["private_key"] == "real_key"
    assert result["private_key_password"] == "real_key_pass"  # noqa: S105


def test_unmask_password_info_leaves_new_values() -> None:
    model = MagicMock()
    model.password = "old_password"  # noqa: S105

    tunnel = {"password": "new_password"}
    result = unmask_password_info(tunnel, model)
    assert result["password"] == "new_password"  # noqa: S105


def test_get_default_port_known_backends() -> None:
    assert get_default_port("postgresql") == 5432
    assert get_default_port("mysql") == 3306
    assert get_default_port("oracle") == 1521
    assert get_default_port("mssql") == 1433


def test_get_default_port_unknown_backend() -> None:
    assert get_default_port("sqlite") is None
    assert get_default_port("unknown") is None
