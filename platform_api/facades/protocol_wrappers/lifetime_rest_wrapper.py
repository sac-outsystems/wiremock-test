import logging
from http import HTTPStatus
from typing import Any, List

import requests
from pydantic import parse_obj_as
from requests.models import HTTPBasicAuth

from platform_api.facades.lifetime_model import (
    ApplySettingsStatusResponse,
    EnvironmentSetPublicHostResponse,
    LifetimeCredentials,
    LifetimeEnvironment,
    LifetimeError,
)
from platform_api.facades.log_extra import log_extra

LTCC_SERVICES_SET_PUBLIC_HOST = (
    "/LifeTimeCloudConnect/rest/LTCCServices/Environment_SetPublicHost?EnvironmentSerial={environment_serial}"
)
COA_INFRASTRUCTURE = "/CloudOrchestrationAPI/rest/v1/Infrastructure"
COA_ENVIRONMENT_APPLY_SETTINGS = "/CloudOrchestrationAPI/rest/v1/applysettings/environment/{environment_key}"
COA_ENVIRONMENT_GET_STATUS_APPLY_SETTINGS = (
    "/CloudOrchestrationAPI/rest/v1/applysettings/{operation_id}/status?EnvironmentKey={environment_key}"
)

logger = logging.getLogger(__name__)


class LifeTimeRestWrapperService:
    """Wraps lifetime REST services"""

    def set_public_host(
        self,
        domain: str,
        authentication: LifetimeCredentials,
        environment_serial: str,
        public_host: str,
        is_lifetime: bool,
    ) -> EnvironmentSetPublicHostResponse:
        """Sets the public host for an environment.

        Args:
            domain (str): The host domain of the Lifetime server.
            authentication (LifetimeCredentials): The authentication information to call Lifetime web services.
            environment_serial (str): The serial number of the environment.
            public_host (str): The desired public host.
            is_filetime (bool): True if the environment to change is lifetime.

        Raises:
            LifetimeError: [description]

        Returns:
            LifetimeUser: [description]
        """

        set_public_host_url = f"https://{domain}{LTCC_SERVICES_SET_PUBLIC_HOST}"
        logger.debug(f"calling {set_public_host_url} endpoint")
        url = set_public_host_url.format(environment_serial=environment_serial)

        auth = HTTPBasicAuth(
            authentication.username,
            authentication.password,
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = ({"IsLifetime": is_lifetime, "PublicHost": public_host},)

        response = requests.post(url, auth=auth, headers=headers, data=body)
        logger.debug(f"End calling {set_public_host_url} endpoint: {response.text}")

        if response.status_code != HTTPStatus.OK:
            raise LifetimeError(error_code="", error_message=response.text, http_status_code=response.status_code)

        return EnvironmentSetPublicHostResponse(**response.json())

    def get_infrastructure(self, domain: str, authentication: LifetimeCredentials) -> List[LifetimeEnvironment]:
        """
        Gets Environments of the Infrastructure

        Args:
            domain (str): The host domain of the Lifetime server.
            authentication (LifetimeCredentials): The authentication information to call Lifetime web services.

        Raises:
            LifetimeError: If any error occurs while get environments.

        Returns:
            List[LifetimeEnvironment]: The List of environments
        """

        logger.info("Calling infrastructure_get on CloudOrchestrationAPI")

        url = f"https://{domain}{COA_INFRASTRUCTURE}"
        logger.debug(f"calling {url} endpoint")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        auth = HTTPBasicAuth(
            authentication.username,
            authentication.password,
        )

        response = requests.get(url, auth=auth, headers=headers)
        logger.debug(response.text)

        if response.status_code != HTTPStatus.OK:
            raise LifetimeError(error_code="", error_message=response.text, http_status_code=response.status_code)

        infra = parse_obj_as(List[LifetimeEnvironment], response.json())
        logger.info("The infrastructure_get was called successfully")

        return infra

    def apply_environment_settings(self, domain: str, authentication: LifetimeCredentials, environment_key: str) -> int:
        """
        Gets Environments of the Infrastructure

        Args:
            domain (str): The host domain of the Lifetime server.
            authentication (LifetimeCredentials): The authentication information to call Lifetime web services.
            environment_key (str): The lifetime EnvironmentKey

        Raises:
            LifetimeError: If any error occurs while get environments.

        Returns:
            int: The operation_id
        """

        logger.info("Calling Apply_Settings on CloudOrchestrationAPI")

        url = f"https://{domain}{COA_ENVIRONMENT_APPLY_SETTINGS}"
        url = url.format(environment_key=environment_key)
        logger.debug(f"calling {url} endpoint")

        headers = {"Content-Type": "application/json"}
        auth = HTTPBasicAuth(
            authentication.username,
            authentication.password,
        )

        response = requests.put(url, auth=auth, headers=headers)
        logger.debug("Response received from Platform apply settings api", extra=log_extra(response))

        if response.status_code != HTTPStatus.OK:
            raise LifetimeError(error_code="", error_message=response.text, http_status_code=response.status_code)

        operation_id = response.json()
        logger.info("The Apply_Settings was called successfully")

        return operation_id

    def get_apply_settings_status(
        self, domain: str, authentication: LifetimeCredentials, operation_id: int, environment_key: str
    ) -> ApplySettingsStatusResponse:
        """
        Gets Status of the Process Apply Settings

        Args:
            domain (str): The host domain of the Lifetime server.
            authentication (LifetimeCredentials): The authentication information to call Lifetime web services.
            operation_id (int): The identifier of operation
            environment_key (str): The lifetime EnvironmentKey

        Raises:
            LifetimeError: If any error occurs while get environments.

        Returns:
            int: The operation_id
        """

        logger.info("Calling Apply_Settings_Status on CloudOrchestrationAPI")

        url = f"https://{domain}{COA_ENVIRONMENT_GET_STATUS_APPLY_SETTINGS}"
        url = url.format(operation_id=operation_id, environment_key=environment_key)
        logger.debug(f"calling {url} endpoint")

        headers = {"Content-Type": "application/json"}
        auth = HTTPBasicAuth(
            authentication.username,
            authentication.password,
        )

        response = requests.get(url, auth=auth, headers=headers)
        logger.debug(response.text)

        if response.status_code != HTTPStatus.OK:
            raise LifetimeError(error_code="", error_message=response.text, http_status_code=response.status_code)

        status = ApplySettingsStatusResponse(**response.json())
        logger.info("The Apply_Settings was called successfully")

        return status

    def _raise_lt_rest_error(self, rest_result: Any) -> None:
        """Raises a standard error based on the result structure from the Lifetime service

        Args:
            rest_result (Any): The rest result structure from the Lifetime service

        Raises:
            LifetimeError: Standard Lifetime error
        """
        raise LifetimeError(
            error_code=rest_result.StatusCode,
            error_message=rest_result.StatusMessage,
            http_status_code=HTTPStatus.BAD_REQUEST,
        )

    def _raise_lt_rest_error_from_http_error(self, http_error: HTTPStatus) -> None:
        """Raises as standard error based on a HTTP error

        Args:
            http_error (HTTPError): The HTTP error in the origin of the problem.

        Raises:
            LifetimeError: Standard Lifetime error
        """
        error_message = http_error.message
        if not error_message:
            error_message = http_error.response.text

        raise LifetimeError(error_code="", error_message=error_message, http_status_code=http_error.value)
