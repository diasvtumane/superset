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
import logging
from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Optional

from flask_appbuilder.models.sqla import Model
from flask_appbuilder.security.sqla.models import User

from superset.commands.utils import compute_owner_list, populate_owner_list

logger = logging.getLogger(__name__)


class BaseCommand(ABC):
    """
    Base class for all Command like Superset Logic objects
    """

    @abstractmethod
    def run(self) -> Any:
        """
        Run executes the command. Can raise command exceptions
        :raises: CommandException
        """

    @abstractmethod
    def validate(self) -> None:
        """
        Validate is normally called by run to validate data.
        Will raise exception if validation fails
        :raises: CommandException
        """


class BaseDeleteCommand(BaseCommand):
    """
    Shared base for bulk-delete commands.

    Subclasses declare the DAO, exception types, and whether ownership
    should be verified.  The ``run`` / ``validate`` boilerplate is
    handled here.

    Class attributes that subclasses must set:
        dao            – the DAO class (must expose ``find_by_ids`` / ``delete``)
        not_found_error – exception raised when one or more IDs are missing
        delete_failed_error – exception wrapped around unexpected failures

    Optional class attributes:
        check_ownership – when ``True`` (default ``False``), each model is
                          checked via ``security_manager.raise_for_ownership``
        forbidden_error – exception raised on ownership violations
    """

    dao: type[Any]
    not_found_error: type[Exception]
    delete_failed_error: type[Exception]
    check_ownership: bool = False
    forbidden_error: type[Exception] | None = None

    def __init__(self, model_ids: list[int]) -> None:
        self._model_ids = model_ids
        self._models: Optional[list[Model]] = None

    def run(self) -> None:
        from superset.utils.decorators import on_error, transaction

        @transaction(on_error=partial(on_error, reraise=self.delete_failed_error))
        def _execute(cmd: "BaseDeleteCommand") -> None:
            cmd.validate()
            assert cmd._models
            cmd.dao.delete(cmd._models)

        _execute(self)

    def validate(self) -> None:
        self._models = self.dao.find_by_ids(self._model_ids)
        if not self._models or len(self._models) != len(self._model_ids):
            raise self.not_found_error()
        if self.check_ownership:
            self._validate_ownership()
        self._extra_validation()

    def _validate_ownership(self) -> None:
        from superset import security_manager
        from superset.exceptions import SupersetSecurityException

        assert self._models
        for model in self._models:
            try:
                security_manager.raise_for_ownership(model)
            except SupersetSecurityException as ex:
                if self.forbidden_error is None:
                    raise
                raise self.forbidden_error() from ex

    def _extra_validation(self) -> None:
        """Hook for subclass-specific validation (report checks, etc.)."""


class CreateMixin:  # pylint: disable=too-few-public-methods
    @staticmethod
    def populate_owners(owner_ids: Optional[list[int]] = None) -> list[User]:
        """
        Populate list of owners, defaulting to the current user if `owner_ids` is
        undefined or empty. If current user is missing in `owner_ids`, current user
        is added unless belonging to the Admin role.

        :param owner_ids: list of owners by id's
        :raises OwnersNotFoundValidationError: if at least one owner can't be resolved
        :returns: Final list of owners
        """
        return populate_owner_list(owner_ids, default_to_user=True)


class UpdateMixin:
    @staticmethod
    def populate_owners(owner_ids: Optional[list[int]] = None) -> list[User]:
        """
        Populate list of owners. If current user is missing in `owner_ids`, current user
        is added unless belonging to the Admin role.

        :param owner_ids: list of owners by id's
        :raises OwnersNotFoundValidationError: if at least one owner can't be resolved
        :returns: Final list of owners
        """
        return populate_owner_list(owner_ids, default_to_user=False)

    @staticmethod
    def compute_owners(
        current_owners: Optional[list[User]],
        new_owners: Optional[list[int]],
    ) -> list[User]:
        """
        Handle list of owners for update events.

        :param current_owners: list of current owners
        :param new_owners: list of new owners specified in the update payload
        :returns: Final list of owners
        """
        return compute_owner_list(current_owners, new_owners)
