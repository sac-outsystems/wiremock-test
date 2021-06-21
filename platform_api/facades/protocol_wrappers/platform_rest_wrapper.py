import json
import logging
from http import HTTPStatus

import requests
from requests.models import HTTPBasicAuth

from platform_api.facades.platform_service_center_model import (
    ServiceCenterChangeUserPassword,
    ServiceCenterCredentials,
    ServiceCenterError,
    ServiceCenterUser,
)

OUTSYSTEMS_CCA_CREATE_USER = "/CloudConnectAgent/rest/BussinessUsers/user"
OUTSYSTEMS_CCA_CHANGE_USER_PWD = "/CloudConnectAgent/rest/BussinessUsers/user/{username}/setpassword"
OUTSYSTEMS_CCA_CHANGE_USER_PWD_V2 = "/CloudConnectAgent/rest/BussinessUsers/user/setpassword"

CONTENT_TYPE_JSON_HEADER = {"Content-Type": "application/json"}

logger = logging.getLogger(__name__)

class ServiceCenterRestWrapperService:
    """
    Wraps Service Center REST services
    """

    def create_user(
        self, domain: str, authentication: ServiceCenterCredentials, service_center_user: ServiceCenterUser
    ) -> bool:
        """
        Creates a Service Center user

        Args:
            domain (str): The host domain of the Lifetime server.
            authentication (Credentials): The authentication information to call Cloud Connect Agent
            service_center_user (LifeTServiceCenterUserimeUser): The information to create the user.

        Raises:
            ServiceCenterError: If any error occurs while creating the user in Cloud Connect Agent.

        Returns:
            bool: True if user was created
        """

        logger.info("Calling Create Business User")

        url = f"https://{domain}{OUTSYSTEMS_CCA_CREATE_USER}"
        logger.debug(f"Calling Create Business User {url}")

        auth = HTTPBasicAuth(authentication.username, authentication.password)

        body = {
            "Name": service_center_user.name,
            "Username": service_center_user.username,
            "Password": service_center_user.password,
            "Email": service_center_user.email,
            "IsAdmin": service_center_user.is_admin,
        }

        response = requests.post(url, auth=auth, headers=CONTENT_TYPE_JSON_HEADER, data=json.dumps(body))
        logger.debug(response.text)

        if response.status_code != HTTPStatus.OK:
            raise ServiceCenterError(error_code="", error_message=response.text, http_status_code=response.status_code)

        response_data = response.json()
        if response_data["StatusCode"] != "OK":
            raise ServiceCenterError(
                error_code=response_data["StatusCode"],
                error_message=response_data["StatusMessage"],
                http_status_code=HTTPStatus.BAD_REQUEST,
            )

        return True

    def change_user_password(
        self,
        domain: str,
        authentication: ServiceCenterCredentials,
        service_center_change_user_password: ServiceCenterChangeUserPassword,
    ) -> bool:
        """
        Change a password for business user

        Args:
            domain (str): The host domain of the Lifetime server.
            authentication (Credentials): The authentication information to call Cloud Connect Agent
            service_center_change_user_password (ServiceCenterChangeUserPassword): The data with new password

        Raises:
            ServiceCenterError: If any error occurs while creating the user in Cloud Connect Agent.

        Returns:
            bool: True if user was created
        """

        logger.info("Calling Change User password for a business user")

        url = f"https://{domain}{OUTSYSTEMS_CCA_CHANGE_USER_PWD}"
        url = url.format(username=service_center_change_user_password.username)
        logger.debug(f"Endpoint to Change User Password {url}")

        auth = HTTPBasicAuth(authentication.username, authentication.password)

        body = {
            "Password": service_center_change_user_password.new_password,
        }

        response = requests.post(url, auth=auth, headers=CONTENT_TYPE_JSON_HEADER, data=json.dumps(body))
        logger.debug(response.text)

        if response.status_code != HTTPStatus.OK:
            logger.error(f"Error on Change User password: {response.status_code}: {response.text}")
            raise ServiceCenterError(error_code="", error_message=response.text, http_status_code=response.status_code)

        response_data = response.json()
        if response_data["StatusCode"] != "OK":
            logger.error(
                f'Error on Change User password: StatusCode={response_data["StatusCode"]} StatusMessage={response_data["StatusMessage"]}'
            )
            raise ServiceCenterError(
                error_code=response_data["StatusCode"],
                error_message=response_data["StatusMessage"],
                http_status_code=HTTPStatus.BAD_REQUEST,
            )

        return True

    def change_user_password_v2(
        self,
        domain: str,
        authentication: ServiceCenterCredentials,
        service_center_change_user_password: ServiceCenterChangeUserPassword,
    ) -> bool:
        """
        Change a password for business user

        Args:
            domain (str): The host domain of the Lifetime server.
            authentication (Credentials): The authentication information to call Cloud Connect Agent
            service_center_change_user_password (ServiceCenterChangeUserPassword): The data with new password

        Raises:
            ServiceCenterError: If any error occurs while creating the user in Cloud Connect Agent.

        Returns:
            bool: True if user was created
        """

        logger.info("Calling Change User password for a business user")

        url = f"https://{domain}{OUTSYSTEMS_CCA_CHANGE_USER_PWD_V2}"
        logger.debug(f"Endpoint to Change User Password v2 {url}")

        auth = HTTPBasicAuth(authentication.username, authentication.password_encrypted)

        body = {
            "Username": service_center_change_user_password.username,
            "Password": service_center_change_user_password.new_password,
        }

        response = requests.post(url, auth=auth, headers=CONTENT_TYPE_JSON_HEADER, data=json.dumps(body))
        logger.debug(response.text)

        if response.status_code != HTTPStatus.OK:
            logger.error(f"Error on Change User password: {response.status_code}: {response.text}")
            raise ServiceCenterError(error_code="", error_message=response.text, http_status_code=response.status_code)

        response_data = response.json()
        if response_data["StatusCode"] != "OK":
            logger.error(
                f'Error on Change User password: StatusCode={response_data["StatusCode"]} StatusMessage={response_data["StatusMessage"]}'
            )
            raise ServiceCenterError(
                error_code=response_data["StatusCode"],
                error_message=response_data["StatusMessage"],
                http_status_code=HTTPStatus.BAD_REQUEST,
            )

        return True
