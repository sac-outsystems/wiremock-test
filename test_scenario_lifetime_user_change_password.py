from http import HTTPStatus

import pytest as pytest

import no_ssl_verification as SSL
import stubbing_utils as WireMockStubbing
from platform_api.facades.lifetime_facade import LifetimeFacade
from platform_api.facades.lifetime_model import LifetimeCredentials, LifetimeError, \
    LifetimeChangeUserPassword
from wiremock_service import WireMockService, WIREMOCK_DEFAULT_URL

EXPECTED_USER_CHANGE_PASSWORD_REQUEST_TEMPLATE = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:out="http://www.outsystems.com">
   <soapenv:Header/>
   <soapenv:Body>
      <out:User_ChangePassword>
         <out:Authentication>
            <out:Username>${{xmlunit.ignore}}</out:Username>
            <out:Password>${{xmlunit.ignore}}</out:Password>
         </out:Authentication>
         <out:Username>{username}</out:Username>
         <out:NewPassword>{new_password}</out:NewPassword>
         <out:EncryptPassword>{encrypt_password}</out:EncryptPassword>
      </out:User_ChangePassword>
   </soapenv:Body>
</soapenv:Envelope>"""

EXPECTED_USER_CHANGE_PASSWORD_RESPONSE_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <User_ChangePasswordResponse xmlns="http://www.outsystems.com">
            <Success>{success}</Success>
            <Status>
                <Id>{status_id}</Id>
                <ResponseId>{response_id}</ResponseId>
                <ResponseMessage>{response_message}</ResponseMessage>
                <ResponseAdditionalInfo/>
            </Status>
        </User_ChangePasswordResponse>
    </soap:Body>
</soap:Envelope>"""

USER_MANAGEMENT_SOAP_OPERATIONS_URL = "/LifeTimeServices/UserManagementService.asmx?wsdl"

wiremock = WireMockService(WIREMOCK_DEFAULT_URL)


def _setup_mappings_for_user_change_password(run_id: str):
    happy_request = EXPECTED_USER_CHANGE_PASSWORD_REQUEST_TEMPLATE.format(
        username="username",
        new_password="new_password",
        encrypt_password="true",
    )
    happy_response = EXPECTED_USER_CHANGE_PASSWORD_RESPONSE_TEMPLATE.format(
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

    expected_request_for_unsuccessful_operation = EXPECTED_USER_CHANGE_PASSWORD_REQUEST_TEMPLATE.format(
        username="unsuccessful_user",
        new_password="new_password",
        encrypt_password="true",
    )
    expected_response_for_unsuccessful_operation = EXPECTED_USER_CHANGE_PASSWORD_RESPONSE_TEMPLATE.format(
        success="false",
        status_id="-1",
        response_id="1000",
        response_message="The password is the same as the old one",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=USER_MANAGEMENT_SOAP_OPERATIONS_URL,
        expected_request=expected_request_for_unsuccessful_operation,
        expected_response=expected_response_for_unsuccessful_operation
    )

    expected_request_for_internal_lifetime_error = EXPECTED_USER_CHANGE_PASSWORD_REQUEST_TEMPLATE.format(
        username="unknown_user",
        new_password="new_password",
        encrypt_password="true",
    )
    expected_response_for_internal_lifetime_error = EXPECTED_USER_CHANGE_PASSWORD_RESPONSE_TEMPLATE.format(
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

    expected_request_for_network_error = EXPECTED_USER_CHANGE_PASSWORD_REQUEST_TEMPLATE.format(
        username="username_for_network_error",
        new_password="new_password",
        encrypt_password="true",
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
        _setup_mappings_for_user_change_password(run_id)

    yield run_id

    with SSL.do_not_verify():
        wiremock.delete_by_run_id(run_id)


def test_when_user_change_password_is_successful():
    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        happy_response = lifetime.change_user_password(
            domain=DEFAULT_DOMAIN,
            authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
            user=LifetimeChangeUserPassword(
                tenant_id="1122333",
                username="username",
                new_password="new_password",
            ),
            encrypt_password=True
        )

    assert happy_response


def test_when_user_change_password_is_unsuccessful():
    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        with pytest.raises(LifetimeError) as e:
            _ = lifetime.change_user_password(
                domain=DEFAULT_DOMAIN,
                authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
                user=LifetimeChangeUserPassword(
                    tenant_id="1122333",
                    username="unsuccessful_user",
                    new_password="new_password",
                ),
                encrypt_password=True
            )

    assert e.value.error_code == 1000
    assert e.value.error_message == "The password is the same as the old one"
    assert e.value.http_status_code == HTTPStatus.BAD_REQUEST


def test_when_user_change_password_with_internal_lifetime_error():
    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        with pytest.raises(LifetimeError) as e:
            _ = lifetime.change_user_password(
                domain=DEFAULT_DOMAIN,
                authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
                user=LifetimeChangeUserPassword(
                    tenant_id="1122333",
                    username="unknown_user",
                    new_password="new_password",
                ),
                encrypt_password=True
            )

        assert e.value.error_code == 999
        assert e.value.error_message == "Lifetime internal error"


def test_when_user_change_password_with_catastrophic_error():
    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        with pytest.raises(LifetimeError) as e:
            _ = lifetime.change_user_password(
                domain=DEFAULT_DOMAIN,
                authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
                user=LifetimeChangeUserPassword(
                    tenant_id="1122333",
                    username="username_for_network_error",
                    new_password="new_password",
                ),
                encrypt_password=True
            )

        assert e.value.error_code == ""
        assert e.value.error_message == "Server Error"
        assert e.value.http_status_code == HTTPStatus.INTERNAL_SERVER_ERROR
