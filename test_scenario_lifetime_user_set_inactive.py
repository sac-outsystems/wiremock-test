from http import HTTPStatus

import pytest as pytest

import stubbing_utils as WireMockStubbing
import no_ssl_verification as SSL
from platform_api.facades.lifetime_facade import LifetimeFacade
from platform_api.facades.lifetime_model import LifetimeCredentials, InactivateLifetimeUserRequest, LifetimeError
from platform_api.facades.protocol_wrappers.lifetime_soap_wrapper import LIFETIME_INACTIVATE_USER_USER_NOT_FOUND
from wiremock_service import WireMockService, WIREMOCK_DEFAULT_URL

EXPECTED_USER_SET_INACTIVE_REQUEST_TEMPLATE = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:out="http://www.outsystems.com">
   <soapenv:Header/>
   <soapenv:Body>
      <out:User_SetInactive>
         <out:Authentication>
            <out:Username>${{xmlunit.ignore}}</out:Username>
            <out:Password>${{xmlunit.ignore}}</out:Password>
         </out:Authentication>
         <out:Username>{username}</out:Username>
      </out:User_SetInactive>
   </soapenv:Body>
</soapenv:Envelope>"""

EXPECTED_USER_SET_INACTIVE_RESPONSE_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <User_SetInactiveResponse xmlns="http://www.outsystems.com">
            <Success>{success}</Success>
            <Status>
                <Id>{status_id}</Id>
                <ResponseId>{response_id}</ResponseId>
                <ResponseMessage>{response_message}</ResponseMessage>
                <ResponseAdditionalInfo/>
            </Status>
        </User_SetInactiveResponse>
    </soap:Body>
</soap:Envelope>"""

USER_MANAGEMENT_SOAP_OPERATIONS_URL = "/LifeTimeServices/UserManagementService.asmx?wsdl"

wiremock = WireMockService(WIREMOCK_DEFAULT_URL)


def _setup_mappings_for_user_set_inactive(run_id: str):
    """
    Exemplo de introduzir o run_id por forma a garantir testes concorrentes
    """

    happy_request = EXPECTED_USER_SET_INACTIVE_REQUEST_TEMPLATE.format(
        username="{}-username".format(run_id),
    )
    happy_response = EXPECTED_USER_SET_INACTIVE_RESPONSE_TEMPLATE.format(
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

    # special case where the error response ID is LIFETIME_INACTIVATE_USER_USER_NOT_FOUND
    expected_not_found_user_request = EXPECTED_USER_SET_INACTIVE_REQUEST_TEMPLATE.format(
        username="{}-not_found_user".format(run_id),
    )
    expected_not_found_user_response = EXPECTED_USER_SET_INACTIVE_RESPONSE_TEMPLATE.format(
        success="false",
        status_id="1",
        response_id=str(LIFETIME_INACTIVATE_USER_USER_NOT_FOUND),
        response_message="The user was not found",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=USER_MANAGEMENT_SOAP_OPERATIONS_URL,
        expected_request=expected_not_found_user_request,
        expected_response=expected_not_found_user_response
    )

    expected_request_for_unsuccessful_operation = EXPECTED_USER_SET_INACTIVE_REQUEST_TEMPLATE.format(
        username="{}-unsuccessful_user".format(run_id),
    )
    expected_response_for_unsuccessful_operation = EXPECTED_USER_SET_INACTIVE_RESPONSE_TEMPLATE.format(
        success="false",
        status_id="-1",
        response_id="1000",
        response_message="The user is already inactive",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=USER_MANAGEMENT_SOAP_OPERATIONS_URL,
        expected_request=expected_request_for_unsuccessful_operation,
        expected_response=expected_response_for_unsuccessful_operation
    )

    expected_request_for_internal_lifetime_error = EXPECTED_USER_SET_INACTIVE_REQUEST_TEMPLATE.format(
        username="{}-user_for_internal_error".format(run_id),
    )
    expected_response_for_internal_lifetime_error = EXPECTED_USER_SET_INACTIVE_RESPONSE_TEMPLATE.format(
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

    expected_request_for_network_error = EXPECTED_USER_SET_INACTIVE_REQUEST_TEMPLATE.format(
        username="{}-username_for_network_error".format(run_id),
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
        _setup_mappings_for_user_set_inactive(run_id)

    yield run_id

    with SSL.do_not_verify():
        wiremock.delete_by_run_id(run_id)


def test_when_set_inactive_is_successful(boostrap):
    run_id = boostrap

    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        happy_response = lifetime.inactivate_user(
            domain=DEFAULT_DOMAIN,
            authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
            request=InactivateLifetimeUserRequest(
                tenant_id="1122333",
                username="{}-username".format(run_id)
            )
        )

    assert happy_response


def test_when_set_inactive_is_unsuccessful(boostrap):
    run_id = boostrap

    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        with pytest.raises(LifetimeError) as e:
            _ = lifetime.inactivate_user(
                domain=DEFAULT_DOMAIN,
                authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
                request=InactivateLifetimeUserRequest(
                    tenant_id="1122333",
                    username="{}-unsuccessful_user".format(run_id)
                )
            )

    assert e.value.error_code == 1000
    assert e.value.error_message == "The user is already inactive"
    assert e.value.http_status_code == HTTPStatus.BAD_REQUEST


def test_when_set_inactive_with_internal_lifetime_error(boostrap):
    run_id = boostrap

    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        with pytest.raises(LifetimeError) as e:
            _ = lifetime.inactivate_user(
                domain=DEFAULT_DOMAIN,
                authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
                request=InactivateLifetimeUserRequest(
                    tenant_id="1122333",
                    username="{}-user_for_internal_error".format(run_id)
                )
            )

        assert e.value.error_code == 999
        assert e.value.error_message == "Lifetime internal error"


def test_when_set_inactive_with_not_found_user_error(boostrap):
    run_id = boostrap

    # special case where the error response ID from LT is LIFETIME_INACTIVATE_USER_USER_NOT_FOUND
    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        with pytest.raises(LifetimeError) as e:
            _ = lifetime.inactivate_user(
                domain=DEFAULT_DOMAIN,
                authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
                request=InactivateLifetimeUserRequest(
                    tenant_id="1122333",
                    username="{}-not_found_user".format(run_id)
                )
            )

        assert e.value.error_code == LIFETIME_INACTIVATE_USER_USER_NOT_FOUND
        assert e.value.error_message == "The user was not found"
        assert e.value.http_status_code == HTTPStatus.NOT_FOUND


def test_when_set_inactive_with_catastrophic_error(boostrap):
    run_id = boostrap

    with SSL.do_not_verify():
        lifetime = LifetimeFacade()

        with pytest.raises(LifetimeError) as e:
            _ = lifetime.inactivate_user(
                domain=DEFAULT_DOMAIN,
                authentication=LifetimeCredentials(username="admin_username", password="admin_password"),
                request=InactivateLifetimeUserRequest(
                    tenant_id="1122333",
                    username="{}-username_for_network_error".format(run_id)
                )
            )

        assert e.value.error_code == ""
        assert e.value.error_message == "Server Error"
        assert e.value.http_status_code == HTTPStatus.INTERNAL_SERVER_ERROR
