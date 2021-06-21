"""
Module with Base methods for services
"""
import logging
from http import HTTPStatus
from typing import Any

from suds.cache import ObjectCache
from suds.client import Client

from platform_api.facades.lifetime_model import LifetimeError
from platform_api.facades.platform_service_center_model import ServiceCenterError

logger = logging.getLogger(__name__)

CACHE_DAYS = 365


class BaseSoapWrapperService:
    """Wraps Service Center services"""

    __soap_client: Client = None

    def _get_soap_client(self, url: str, faults: bool = False) -> Client:
        """
        Build the Client object

        Args:
            url (str): The URL to WSDL.
            faults (bool): True if method throws exception

        Return:
            Client: The Soap Client
        """

        logger.debug("calling %s endpoint" % url)

        if not self.__soap_client:
            self.__soap_client = Client(url, faults=faults, cache=ObjectCache(days=CACHE_DAYS))

        self.__soap_client.sd[0].service.setlocation(url)

        return self.__soap_client

    def _raise_lt_soap_error(self, response_status: Any) -> None:
        """Raises a standard error based on a Lifetime response

        Args:
            response_status (WSDL: APIStatus): The response from Lifetime

        Raises:
            LifetimeError: Standard Lifetime error
        """
        error_message = f"{response_status.ResponseMessage}{' ' + response_status.ResponseAdditionalInfo if response_status.ResponseAdditionalInfo else ''}"
        raise LifetimeError(
            error_code=response_status.ResponseId, error_message=error_message, http_status_code=HTTPStatus.BAD_REQUEST
        )

    def _raise_lt_soap_error_from_code(self, http_status_code: int, error_message: str) -> None:
        """Raises a standard error based on an http status code

        Args:
            http_status_code (int): The HTTP status code (e.g. 500 or 400)
            error_message (str): The fault message

        Raises:
            LifetimeError: Standard Lifetime error
        """
        raise LifetimeError(error_code="", error_message=error_message, http_status_code=http_status_code)

    def _raise_sc_soap_error_from_code(self, http_status_code: int, error_message: str) -> None:
        """Raises a standard error based on an http status code

        Args:
            http_status_code (int): The HTTP status code (e.g. 500 or 400)
            error_message (str): The fault message

        Raises:
            LifetimeError: Standard Lifetime error
        """
        raise ServiceCenterError(error_code="", error_message=error_message, http_status_code=http_status_code)
