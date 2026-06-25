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
from unittest.mock import patch

from superset.utils.version import _get_local_branch, _get_local_sha, get_dev_env_label


def test_get_local_branch_returns_string() -> None:
    result = _get_local_branch()
    # running in a git repo, should return something
    assert result is None or isinstance(result, str)


def test_get_local_sha_returns_string() -> None:
    result = _get_local_sha()
    assert result is None or isinstance(result, str)
    if result:
        assert len(result) == 40  # full SHA


def test_get_dev_env_label_with_github_env() -> None:
    with patch.dict(
        "os.environ",
        {"GITHUB_HEAD_REF": "feature-branch", "GITHUB_SHA": "abc12345def67890"},
        clear=False,
    ):
        label = get_dev_env_label()
        assert "feature-branch" in label
        assert "abc12345" in label


def test_get_dev_env_label_sha_only() -> None:
    with (
        patch.dict(
            "os.environ",
            {"GITHUB_SHA": "abc12345def67890"},
            clear=False,
        ),
        patch(
            "superset.utils.version._get_local_branch",
            return_value=None,
        ),
        patch.dict(
            "os.environ",
            {"GITHUB_HEAD_REF": "", "GITHUB_REF_NAME": ""},
            clear=False,
        ),
    ):
        label = get_dev_env_label()
        assert label.startswith("@")
        assert "abc12345" in label


def test_get_dev_env_label_branch_only() -> None:
    with (
        patch.dict(
            "os.environ",
            {"GITHUB_HEAD_REF": "my-branch"},
            clear=False,
        ),
        patch(
            "superset.utils.version._get_local_sha",
            return_value=None,
        ),
        patch.dict(
            "os.environ",
            {"GITHUB_SHA": ""},
            clear=False,
        ),
    ):
        label = get_dev_env_label()
        assert label == "my-branch"


def test_get_dev_env_label_empty() -> None:
    with (
        patch.dict(
            "os.environ",
            {"GITHUB_HEAD_REF": "", "GITHUB_REF_NAME": "", "GITHUB_SHA": ""},
            clear=False,
        ),
        patch(
            "superset.utils.version._get_local_branch",
            return_value=None,
        ),
        patch(
            "superset.utils.version._get_local_sha",
            return_value=None,
        ),
    ):
        label = get_dev_env_label()
        assert label == ""


def test_get_local_branch_handles_failure() -> None:
    with patch(
        "superset.utils.version.subprocess.check_output",
        side_effect=OSError("git not found"),
    ):
        result = _get_local_branch()
        assert result is None


def test_get_local_sha_handles_failure() -> None:
    with patch(
        "superset.utils.version.subprocess.check_output",
        side_effect=OSError("git not found"),
    ):
        result = _get_local_sha()
        assert result is None
