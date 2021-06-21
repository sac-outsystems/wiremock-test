"""
Wrapper to call Lifetime services
"""
import logging
from http import HTTPStatus
from typing import Any, Union

from suds.client import Client

from platform_api.facades.lifetime_model import (
    InactivateLifetimeUserRequest,
    LifetimeChangeUserPassword,
    LifetimeCredentials,
    LifetimeError,
    LifetimeUser,
)
from platform_api.facades.protocol_wrappers.base_soap_wrapper import BaseSoapWrapperService

logger = logging.getLogger(__name__)

USER_MANAGEMENT_SERVICE_WSDL = "LifeTimeServices/UserManagementService.asmx?wsdl"

LIFETIME_INACTIVATE_USER_USER_NOT_FOUND = 101


class LifeTimeSoapWrapperService(BaseSoapWrapperService):
    """Wraps lifetime SOAP services"""

    # wsdl WebServiceSimpleAuthentication
    __soap_authentication: Any = None

    def __get_soap_authentication(self, client: Client, username: str, password: str, token: Union[str, None]):
        """
        Build the WebServiceSimpleAuthentication object to authentication

        Args:
            client (Client): The Soap Client
            username (str): The username
            password (str): The password
            token (str): The token

        Return:
            WebServiceSimpleAuthentication: the authentication info
        """

        if not self.__soap_authentication:
            self.__soap_authentication = client.factory.create("s0:WebServiceSimpleAuthentication")

        self.__soap_authentication.Username = username
        self.__soap_authentication.Password = password
        self.__soap_authentication.Token = token

        return self.__soap_authentication

    def create_or_update_user(
        self, domain: str, authentication: LifetimeCredentials, user: LifetimeUser, encrypt_password: bool = True
    ) -> LifetimeUser:
        """Creates a Lifetime user

        Args:
            domain (str): The host domain of the Lifetime server.
            authentication (LifetimeCredentials): The authentication information to call Lifetime web services.
            user (LifeTimeUser): The information to create the user.
            encrypt_password (bool, optional): If true the user password will be encrypted. Defaults to True.

        Raises:
            LifetimeError: If any error occurs while creating the user in Lifetime.

        Returns:
            LifetimeUser: The created user.
        """

        url = f"https://{domain}/{USER_MANAGEMENT_SERVICE_WSDL}"

        # The Client must be created with faults=False to can get HttpCode
        # If you want to change faults=True, the handling of "response" object must change (https://github.com/suds-community/suds#faults)
        client = self._get_soap_client(url=url, faults=False)
        auth_struct = self.__get_soap_authentication(
            client=client, username=authentication.username, password=authentication.password, token=None
        )

        response = self._call_create_or_update_user(client, auth_struct, user, encrypt_password)

        if response[0] != HTTPStatus.OK:
            self._raise_lt_soap_error_from_code(response[0], response[1])

        if not response[1].Success:
            self._raise_lt_soap_error(response[1].Status)

        user.identifier = response[1].PlatformUser.Id

        return user

    def _call_create_or_update_user(
        self, client: Client, authentication: LifetimeCredentials, user: LifetimeUser, encrypt_password: bool
    ):
        """Creates a Lifetime user

        Args:
            client (Client): The Client to call
            authentication (LifetimeCredentials): The authentication information to call Lifetime web services.
            user (LifeTimeUser): The information to create the user.
            encrypt_password (bool, optional): If true the user password will be encrypted. Defaults to True.

        Returns:
            LifetimeUser: The created user.
        """

        return client.service.User_CreateOrUpdate(
            authentication, user.username, user.password, encrypt_password, user.name, user.email, user.role
        )

    def change_user_password(
        self,
        domain: str,
        authentication: LifetimeCredentials,
        user: LifetimeChangeUserPassword,
        encrypt_password: bool = True,
    ) -> bool:
        """Change user password in Lifetime

        Args:
            domain (str): The host domain of the Lifetime server.
            authentication (LifetimeCredentials): The authentication information to call Lifetime web services.
            user (LifetimeChangeUserPassword): The information to change the user password.
            encrypt_password (bool, optional): If true the user password will be encrypted. Defaults to True.

        Raises:
            LifetimeError: If any error occurs while change user password in Lifetime.

        Returns:
            bool: True if password was successful changed.
        """

        url = f"https://{domain}/{USER_MANAGEMENT_SERVICE_WSDL}"

        # The Client must be created with faults=False to can get HttpCode
        # If you want to change faults=True, the handling of "response" object must change (https://github.com/suds-community/suds#faults)
        client = self._get_soap_client(url=url, faults=False)
        auth_struct = self.__get_soap_authentication(
            client=client, username=authentication.username, password=authentication.password, token=None
        )

        response = self._call_change_user_password(
            client=client, authentication=auth_struct, user=user, encrypt_password=encrypt_password
        )

        if response[0] != HTTPStatus.OK:
            self._raise_lt_soap_error_from_code(response[0], response[1])

        if not response[1].Success:
            self._raise_lt_soap_error(response[1].Status)

        return response[1].Success

    def _call_change_user_password(
        self,
        client: Client,
        authentication: LifetimeCredentials,
        user: LifetimeChangeUserPassword,
        encrypt_password: bool,
    ):
        """Change user password in Lifetime

        Args:
            client (Client): The Client to call
            authentication (LifetimeCredentials): The authentication information to call Lifetime web services.
            user (LifetimeChangeUserPassword): The information to change the user password.
            encrypt_password (bool, optional): If true the user password will be encrypted. Defaults to True.

        Returns:
            bool: True if password was successful changed.
        """
        return client.service.User_ChangePassword(authentication, user.username, user.new_password, encrypt_password)

    def inactivate_user(
        self, domain: str, authentication: LifetimeCredentials, request: InactivateLifetimeUserRequest
    ) -> bool:
        """Inactivate Lifetime user

        Args:
            domain (str): The host domain of the Lifetime server.
            authentication (LifetimeCredentials): The authentication information to call Lifetime web services.
            user (DeleteLifetimeUser): Information to inactivate the lifetime user

        Raises:
            LifetimeError: If any error occurs while inactivating the user in Lifetime.

        Returns:
            bool: True if the user was inactivated
        """

        url = f"https://{domain}/{USER_MANAGEMENT_SERVICE_WSDL}"

        # The Client must be created with faults=False so it can get an HttpCode
        # If you want to change to faults=True, the handling of "response" object must change (https://github.com/suds-community/suds#faults)
        client = self._get_soap_client(url=url, faults=False)
        auth_struct = self.__get_soap_authentication(
            client=client, username=authentication.username, password=authentication.password, token=None
        )

        response = self._call_inactivate_user(client=client, authentication=auth_struct, request=request)
        logger.debug(response)

        if response[0] != HTTPStatus.OK:
            logger.error(f"status: {response[0]}, fault message: {response[1]}")
            self._raise_lt_soap_error_from_code(response[0], response[1])

        if not response[1].Success:
            logger.error(
                f"response_id: {response[1].Status.ResponseId}, response message: {response[1].Status.ResponseMessage}"
            )
            if response[1].Status.ResponseId == LIFETIME_INACTIVATE_USER_USER_NOT_FOUND:
                raise LifetimeError(
                    error_code=response[1].Status.ResponseId,
                    error_message=response[1].Status.ResponseMessage,
                    http_status_code=HTTPStatus.NOT_FOUND,
                )
            self._raise_lt_soap_error(response[1].Status)

        return response[1].Success

    def _call_inactivate_user(
        self, client: Client, authentication: LifetimeCredentials, request: InactivateLifetimeUserRequest
    ):
        """Inactivate Lifetime user

        Args:
            client (Client): The Client to call
            authentication (LifetimeCredentials): The authentication information to call Lifetime web services.
            user (DeleteLifetimeUser): The information to inactivate the lifetime user

        Returns:
            bool: True if the user was successfully inactivated
        """
        return client.service.User_SetInactive(authentication, request.username)
