from platform_api.facades.platform_service_center_model import (
    PlatformInfo,
    ServiceCenterChangeUserPassword,
    ServiceCenterCredentials,
    ServiceCenterUser,
    SolutionDownloadResponse,
)
from platform_api.facades.protocol_wrappers.platform_rest_wrapper import (
    ServiceCenterRestWrapperService,
)
from platform_api.facades.protocol_wrappers.platform_soap_wrapper import (
    ServiceCenterSoapWrapperService,
)


class PlatformServiceCenterFacade:
    def __init__(self) -> None:
        super().__init__()
        self._soap_client = ServiceCenterSoapWrapperService()
        self._rest_client = ServiceCenterRestWrapperService()

    def get_platform_info(self, domain: str) -> PlatformInfo:

        return self._soap_client.get_platform_info(domain=domain)

    def set_license(self, domain: str, authentication: ServiceCenterCredentials, b64_license: str) -> bool:
        return self._soap_client.set_license(domain=domain, authentication=authentication, b64_license=b64_license)

    def create_all_solution(self, domain: str, authentication: ServiceCenterCredentials, all_solution_name: str) -> int:
        return self._soap_client.create_all_solution(
            domain=domain, authentication=authentication, all_solution_name=all_solution_name
        )

    def solution_download(
        self, domain: str, authentication: ServiceCenterCredentials, solution_name: str, solution_version_id: int
    ) -> SolutionDownloadResponse:

        return self._soap_client.solution_download(
            domain=domain,
            authentication=authentication,
            solution_name=solution_name,
            solution_version_id=solution_version_id,
        )

    def create_user(
        self, domain: str, authentication: ServiceCenterCredentials, service_center_user: ServiceCenterUser
    ) -> bool:

        return self._rest_client.create_user(
            domain=domain, authentication=authentication, service_center_user=service_center_user
        )

    def change_user_password(
        self,
        domain: str,
        authentication: ServiceCenterCredentials,
        service_center_change_user_password: ServiceCenterChangeUserPassword,
    ) -> bool:

        return self._rest_client.change_user_password_v2(
            domain=domain,
            authentication=authentication,
            service_center_change_user_password=service_center_change_user_password,
        )
