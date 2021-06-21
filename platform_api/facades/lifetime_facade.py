from typing import List

from platform_api.facades.lifetime_model import (
    ApplySettingsStatusResponse,
    EnvironmentSetPublicHostResponse,
    InactivateLifetimeUserRequest,
    LifetimeChangeUserPassword,
    LifetimeCredentials,
    LifetimeEnvironment,
    LifetimeUser,
)
from platform_api.facades.protocol_wrappers.lifetime_rest_wrapper import (
    LifeTimeRestWrapperService,
)
from platform_api.facades.protocol_wrappers.lifetime_soap_wrapper import (
    LifeTimeSoapWrapperService,
)


class LifetimeFacade:
    def __init__(self) -> None:
        super().__init__()
        self._soap_client = LifeTimeSoapWrapperService()
        self._rest_client = LifeTimeRestWrapperService()

    def create_or_update_user(
        self, domain: str, authentication: LifetimeCredentials, user: LifetimeUser, encrypt_password: bool = True
    ) -> LifetimeUser:
        return self._soap_client.create_or_update_user(
            domain=domain, authentication=authentication, user=user, encrypt_password=encrypt_password
        )

    def change_user_password(
        self,
        domain: str,
        authentication: LifetimeCredentials,
        user: LifetimeChangeUserPassword,
        encrypt_password: bool = True,
    ) -> bool:

        return self._soap_client.change_user_password(
            domain=domain, authentication=authentication, user=user, encrypt_password=encrypt_password
        )

    def inactivate_user(
        self, domain: str, authentication: LifetimeCredentials, request: InactivateLifetimeUserRequest
    ) -> bool:

        return self._soap_client.inactivate_user(domain=domain, authentication=authentication, request=request)

    def set_public_host(
        self,
        domain: str,
        authentication: LifetimeCredentials,
        environment_serial: str,
        public_host: str,
        is_lifetime: bool,
    ) -> EnvironmentSetPublicHostResponse:

        return self._rest_client.set_public_host(
            domain=domain,
            authentication=authentication,
            environment_serial=environment_serial,
            public_host=public_host,
            is_lifetime=is_lifetime,
        )

    def get_infrastructure(self, domain: str, authentication: LifetimeCredentials) -> List[LifetimeEnvironment]:

        return self._rest_client.get_infrastructure(domain=domain, authentication=authentication)

    def apply_environment_settings(self, domain: str, authentication: LifetimeCredentials, environment_key: str) -> int:

        return self._rest_client.apply_environment_settings(
            domain=domain, authentication=authentication, environment_key=environment_key
        )

    def get_apply_settings_status(
        self, domain: str, authentication: LifetimeCredentials, operation_id: int, environment_key: str
    ) -> ApplySettingsStatusResponse:

        return self._rest_client.get_apply_settings_status(
            domain=domain, authentication=authentication, operation_id=operation_id, environment_key=environment_key
        )
