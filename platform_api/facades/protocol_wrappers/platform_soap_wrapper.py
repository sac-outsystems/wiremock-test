"""
Wrapper to call Service Center services
"""
import logging
from http import HTTPStatus

from suds.client import Client

from platform_api.facades.platform_service_center_model import (
    PlatformInfo,
    ServiceCenterCredentials,
    ServiceCenterError,
    SolutionDownloadResponse,
)
from platform_api.facades.protocol_wrappers.base_soap_wrapper import BaseSoapWrapperService

logger = logging.getLogger(__name__)

OUTSYSTEMS_PLATFORM_SERVICE_WSDL = "/ServiceCenter/OutSystemsPlatform.asmx?wsdl"
OUTSYSTEMS_SC_SOLUTIONS_WSDL = "/ServiceCenter/Solutions.asmx?wsdl"


class ServiceCenterSoapWrapperService(BaseSoapWrapperService):
    """Wraps Service Center SOAP services"""

    def get_platform_info(self, domain: str) -> PlatformInfo:
        """Get PlatformInfo from Service Center

        Args:
            domain (str): The host domain of the Service center server.

        Raises:
            ServiceCenterError: If any error occurs while getting the PlatformInfo in service center

        Returns:
            PlatformInfo: The PlatformInfo with Serial and Version
        """

        logger.info("Calling Get Platform Info on Service Center")

        url = f"https://{domain}{OUTSYSTEMS_PLATFORM_SERVICE_WSDL}"
        logger.debug(f"calling {url} endpoint")

        client = self._get_soap_client(url=url, faults=False)
        response = self._call_get_platform_info(client=client)
        logger.debug(response)

        if response[0] != HTTPStatus.OK:
            self._raise_sc_soap_error_from_code(response[0], response[1])

        return PlatformInfo(version=response[1][0], serial=response[1][1])

    def _call_get_platform_info(self, client: Client):
        """Get Platform Info from Service Center

        Args:
            client (Client): The Client to call

        Returns:

        """

        return client.service.GetPlatformInfo()

    def set_license(self, domain: str, authentication: ServiceCenterCredentials, b64_license: str) -> bool:
        """Get Serial from Service Center

        Args:
            domain (str): The host domain of the Service center server.
            authentication (Credentials): The authentication information to call ServiCenter web services.
            b64_license (str): the license

        Raises:
            ServiceCenterError: If any error occurs while getting the serial in service center

        Returns:
            bool: If new license is installed successfully
        """

        logger.info("Calling Set Serial on Service Center")

        url = f"https://{domain}{OUTSYSTEMS_PLATFORM_SERVICE_WSDL}"
        logger.debug("calling {url} endpoint")

        client = self._get_soap_client(url=url, faults=False)
        response = self._call_set_license(client=client, authentication=authentication, b64_license=b64_license)

        if response[0] != HTTPStatus.OK:
            self._raise_sc_soap_error_from_code(response[0], response[1])

        if not response[1].success:
            raise ServiceCenterError(
                error_code="", error_message=response[1].errorText if "errorText" in response[1] else "The license was not installed", http_status_code=HTTPStatus.BAD_REQUEST
            )

        return True

    def _call_set_license(self, authentication: ServiceCenterCredentials, client: Client, b64_license: str):
        """Install new license in Service Center

        Args:
            client (Client): The Client to call
            authentication (Credentials): The authentication information to call ServiCenter web services.
            b64_license (str): the license

        Returns:

        """

        return client.service.SetLicense(authentication.username, authentication.password_encrypted, b64_license)

    def create_all_solution(self, domain: str, authentication: ServiceCenterCredentials, all_solution_name: str) -> int:
        """
        Call Solutions/CreateAllSolution in Service Center

        Args:
            domain (str): The host domain of the Service center server.
            authentication (Credentials): The authentication information to call ServiCenter web services.
            all_solution_name (str): solution name

        Raises:
            ServiceCenterError: If any error occurs while getting the PlatformInfo in service center

        Returns:
            int: The Solution identifier
        """

        logger.info("Calling Create All Solution on Service Center")

        url = f"https://{domain}{OUTSYSTEMS_SC_SOLUTIONS_WSDL}"
        logger.debug(f"calling {url} endpoint")

        client = self._get_soap_client(url=url, faults=False)
        response = self._call_create_all_solution(
            client=client,
            authentication=authentication,
            all_solution_name=all_solution_name,
        )
        logger.debug(response)

        if response[0] != HTTPStatus.OK:
            self._raise_sc_soap_error_from_code(response[0], response[1])

        return response[1]

    def _call_create_all_solution(
        self, client: Client, authentication: ServiceCenterCredentials, all_solution_name: str
    ) -> int:
        """
        Call Solutions/CreateAllSolution

        Args:
            client (Client): The Client to call
            authentication (Credentials): The authentication information to call ServiCenter web services.
            all_solution_name (str): solution name

        Returns:
            int: The Solution identifier
        """

        return client.service.CreateAllSolution(
            all_solution_name,
            authentication.username,
            authentication.password_encrypted,
        )

    def solution_download(
        self, domain: str, authentication: ServiceCenterCredentials, solution_name: str, solution_version_id: int
    ) -> SolutionDownloadResponse:
        """
        Call Solutions/Download in Service Center

        Args:
            domain (str): The host domain of the Service center server.
            authentication (Credentials): The authentication information to call ServiCenter web services.
            solution_name (str): the solution name
            solution_version_id (int): The solution version identifier

        Raises:
            ServiceCenterError: If any error occurs while Get Solution from service center

        Returns:
            SolutionDownloadResponse: The SolutionDownloadResponse with content file and the Solution Download Operation Id
        """

        logger.info("Calling Get Solution(Download) on Service Center")

        url = f"https://{domain}{OUTSYSTEMS_SC_SOLUTIONS_WSDL}"
        logger.debug(f"calling {url} endpoint")

        logger.debug(f"Send values: solution_name:{solution_name} solution_version_id:{solution_version_id}")
        client = self._get_soap_client(url=url, faults=False)
        response = self._call_solution_download(
            client=client,
            authentication=authentication,
            solution_name=solution_name,
            solution_version_id=solution_version_id,
        )

        if response[0] != HTTPStatus.OK:
            logger.error(f"Returned from ServiceCenter.Solutions.Download: {response}")
            self._raise_sc_soap_error_from_code(response[0], response[1])

        logger.debug(f"SolutionDownloadOpId: {response[1]['SolutionDownloadOpId']}")

        return SolutionDownloadResponse(
            solution_download_op_id=response[1]["SolutionDownloadOpId"], file_content=str(response[1]["file"])
        )

    def _call_solution_download(
        self, client: Client, authentication: ServiceCenterCredentials, solution_name: str, solution_version_id: int
    ):
        """
        Call Solutions/Download

        Args:
            client (Client): The Client to call
            authentication (Credentials): The authentication information to call ServiCenter web services.
            solution_name (str): the solution name
            solution_version_id (int): The solution version identifier

        Returns:
            int: The Solution identifier
        """

        if solution_version_id:
            os_solution_version_id = solution_version_id
        else:
            os_solution_version_id = 0

        return client.service.Download(
            solution_name,
            os_solution_version_id,
            authentication.username,
            authentication.password_encrypted,
        )
