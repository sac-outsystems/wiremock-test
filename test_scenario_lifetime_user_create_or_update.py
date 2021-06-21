from http import HTTPStatus

import pytest as pytest

import no_ssl_verification as SSL
import stubbing_utils as WireMockStubbing
from platform_api.facades.lifetime_facade import LifetimeFacade
from platform_api.facades.lifetime_model import LifetimeCredentials, LifetimeError, \
    LifetimeUser
from wiremock_service import WireMockService, WIREMOCK_DEFAULT_URL

EXPECTED_USER_CREATE_OR_UPDATE_REQUEST_TEMPLATE = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:out="http://www.outsystems.com">
   <soapenv:Header/>
   <soapenv:Body>
      <out:User_CreateOrUpdate>
         <out:Authentication>
            <out:Username>${{xmlunit.ignore}}</out:Username>
            <out:Password>${{xmlunit.ignore}}</out:Password>
         </out:Authentication>
         <out:Username>{username}</out:Username>
         <out:Password>{password}</out:Password>
         <out:EncryptPassword>{encrypt_password}</out:EncryptPassword>
         <out:Name>{name}</out:Name>
         <out:Email>{email}</out:Email>
         <out:RoleName>{role_name}</out:RoleName>
      </out:User_CreateOrUpdate>
   </soapenv:Body>
</soapenv:Envelope>"""

EXPECTED_USER_CREATE_OR_UPDATE_RESPONSE_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <User_CreateOrUpdateResponse xmlns="http://www.outsystems.com">
            <Success>{success}</Success>
            <Status>
                <Id>{status_id}</Id>
                <ResponseId>{response_id}</ResponseId>
                <ResponseMessage>{response_message}</ResponseMessage>
                <ResponseAdditionalInfo/>
            </Status>
            <PlatformUser>
                <Id>{{{{randomValue length=4 type='NUMERIC'}}}}</Id>
                <Username>{{{{xPath request.body '/User_CreateOrUpdate/Username/text()'}}}}</Username>
                <Name>{{{{xPath request.body '/User_CreateOrUpdate/Name/text()'}}}}</Name>
                <Email>{{{{xPath request.body '/User_CreateOrUpdate/Email/text()'}}}}</Email>
                <RoleName>{{{{xPath request.body '/User_CreateOrUpdate/RoleName/text()'}}}}</RoleName>
            </PlatformUser>
        </User_CreateOrUpdateResponse>
    </soap:Body>
</soap:Envelope>"""

USER_MANAGEMENT_SOAP_OPERATIONS_URL = "/LifeTimeServices/UserManagementService.asmx?wsdl"

wiremock = WireMockService(WIREMOCK_DEFAULT_URL)


def _setup_mappings_for_user_create_or_update(run_id: str):
    happy_request = EXPECTED_USER_CREATE_OR_UPDATE_REQUEST_TEMPLATE.format(
        username="username",
        password="password",
        encrypt_password="true",
        name="name",
        email="email",
        role_name="role_name",
    )
    happy_response = EXPECTED_USER_CREATE_OR_UPDATE_RESPONSE_TEMPLATE.format(
        success="true",
        status_id="1",
        response_id="2",
        response_message="smooth",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=USER_MANAGEMENT_SOAP_OPERATIONS_URL,
        expected_request=happy_request,
        expected_response=happy_response
    )

    expected_request_for_unsuccessful_operation = EXPECTED_USER_CREATE_OR_UPDATE_REQUEST_TEMPLATE.format(
        username="unsuccessful_user",
        password="password",
        encrypt_password="true",
        name="unsuccessful_name",
        email="unsuccessful_email",
        role_name="unsuccessful_role_name",
    )
    expected_response_for_unsuccessful_operation = EXPECTED_USER_CREATE_OR_UPDATE_RESPONSE_TEMPLATE.format(
        success="false",
        status_id="-1",
        response_id="1000",
        response_message="The email is invalid",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=USER_MANAGEMENT_SOAP_OPERATIONS_URL,
        expected_request=expected_request_for_unsuccessful_operation,
        expected_response=expected_response_for_unsuccessful_operation
    )

    expected_request_for_internal_lifetime_error = EXPECTED_USER_CREATE_OR_UPDATE_REQUEST_TEMPLATE.format(
        username="internal_invalid_state_user",
        password="internal_invalid_state_password",
        encrypt_password="true",
        name="internal_invalid_state_name",
        email="internal_invalid_state_email",
        role_name="internal_invalid_state_role_name",
    )
    expected_response_for_internal_lifetime_error = EXPECTED_USER_CREATE_OR_UPDATE_RESPONSE_TEMPLATE.format(
        success="false",
        status_id="10",
        response_id="999",
        response_message="Lifetime internal error",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=USER_MANAGEMENT_SOAP_OPERATIONS_URL,
        expected_request=expected_request_for_internal_lifetime_error,
        expected_response=expected_response_for_internal_lifetime_error
    )

    expected_request_for_network_error = EXPECTED_USER_CREATE_OR_UPDATE_REQUEST_TEMPLATE.format(
        username="kaboom_user",
        password="kaboom_password",
        encrypt_password="true",
        name="kaboom_name",
        email="kaboom_email",
        role_name="kaboom_role_name",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=USER_MANAGEMENT_SOAP_OPERATIONS_URL,
        expected_request=expected_request_for_network_error,
        expected_response=None,
        http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR
    )


DEFAULT_DOMAIN = "localhost:8433"


@pytest.fixture(autouse=True, scope="session")
def boostrap():
    run_id = WireMockStubbing.new_run_id()

    with SSL.do_not_verify():
        _setup_mappings_for_user_create_or_update(run_id)

    yield run_id

    with SSL.do_not_verify():
        wiremock.delete_by_run_id(run_id)


def test_when_user_create_or_update_is_successful():
    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        user = lifetime.create_or_update_user(
            domain=DEFAULT_DOMAIN,
            authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
            user=LifetimeUser(
                username="username",
                password="password",
                name="name",
                email="email",
                role="role_name",
            ),
            encrypt_password=True
        )

    assert user.identifier > 0
    assert user.username == "username"
    assert user.password == "password"
    assert user.name == "name"
    assert user.email == "email"
    assert user.role == "role_name"


def test_when_user_create_or_update_is_unsuccessful():
    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        with pytest.raises(LifetimeError) as e:
            _ = lifetime.create_or_update_user(
                domain=DEFAULT_DOMAIN,
                authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
                user=LifetimeUser(
                    username="unsuccessful_user",
                    password="password",
                    name="unsuccessful_name",
                    email="unsuccessful_email",
                    role="unsuccessful_role_name",
                ),
                encrypt_password=True
            )

    assert e.value.error_code == 1000
    assert e.value.error_message == "The email is invalid"
    assert e.value.http_status_code == HTTPStatus.BAD_REQUEST


def test_when_user_create_or_update_with_internal_lifetime_error():
    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        with pytest.raises(LifetimeError) as e:
            _ = lifetime.create_or_update_user(
                domain=DEFAULT_DOMAIN,
                authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
                user=LifetimeUser(
                    username="internal_invalid_state_user",
                    password="internal_invalid_state_password",
                    name="internal_invalid_state_name",
                    email="internal_invalid_state_email",
                    role="internal_invalid_state_role_name",
                ),
                encrypt_password=True
            )

        assert e.value.error_code == 999
        assert e.value.error_message == "Lifetime internal error"


def test_when_user_create_or_update_with_catastrophic_error():
    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        with pytest.raises(LifetimeError) as e:
            _ = lifetime.create_or_update_user(
                domain=DEFAULT_DOMAIN,
                authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
                user=LifetimeUser(
                    username="kaboom_user",
                    password="kaboom_password",
                    name="kaboom_name",
                    email="kaboom_email",
                    role="kaboom_role_name",
                ),
                encrypt_password=True
            )

        assert e.value.error_code == ""
        assert e.value.error_message == "Server Error"
        assert e.value.http_status_code == HTTPStatus.INTERNAL_SERVER_ERROR
