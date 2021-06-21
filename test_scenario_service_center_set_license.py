from http import HTTPStatus

import pytest as pytest

import no_ssl_verification as SSL
import stubbing_utils as WireMockStubbing
from platform_api.base64_encoder import Base64Encoder
from platform_api.facades.lifetime_facade import LifetimeFacade
from platform_api.facades.lifetime_model import LifetimeCredentials, LifetimeError, \
    LifetimeChangeUserPassword
from platform_api.facades.platform_service_center_facade import PlatformServiceCenterFacade
from platform_api.facades.platform_service_center_model import ServiceCenterCredentials, ServiceCenterError
from wiremock_service import WireMockService, WIREMOCK_DEFAULT_URL

EXPECTED_SERVICE_CENTER_SET_LICENSE_REQUEST_TEMPLATE = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:out="http://www.outsystems.com">
   <soapenv:Header/>
   <soapenv:Body>
      <out:SetLicense>
         <out:username>${{xmlunit.ignore}}</out:username>
         <out:password>${{xmlunit.ignore}}</out:password>
         <out:fileContent>{file_content}</out:fileContent>
      </out:SetLicense>
   </soapenv:Body>
</soapenv:Envelope>"""

EXPECTED_SERVICE_CENTER_SET_LICENSE_RESPONSE_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
    <SetLicenseResponse xmlns="http://www.outsystems.com">
        <success>{success}</success>
    </SetLicenseResponse>
</soap:Body>
</soap:Envelope>"""

EXPECTED_SERVICE_CENTER_SET_LICENSE_RESPONSE_TEMPLATE_WITH_ERROR_TEXT = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
    <SetLicenseResponse xmlns="http://www.outsystems.com">
        <success>{success}</success>
        <errorText>{error_message}</errorText>
    </SetLicenseResponse>
</soap:Body>
</soap:Envelope>"""

PLATFORM_API_SOAP_OPERATIONS_URL = "/ServiceCenter/OutSystemsPlatform.asmx?wsdl"

wiremock = WireMockService(WIREMOCK_DEFAULT_URL)

FILE_FOR_SUCCESSFUL_OPERATION = Base64Encoder().from_string_to_base64_string("good_license_file")
FILE_FOR_UNSUCCESSFUL_OPERATION = Base64Encoder().from_string_to_base64_string("bad_license_file")
FILE_FOR_CATASTROPHIC_OPERATION = Base64Encoder().from_string_to_base64_string("catastrophic_license_file")


def _setup_mappings_for_service_center_set_license(run_id: str):
    happy_request = EXPECTED_SERVICE_CENTER_SET_LICENSE_REQUEST_TEMPLATE.format(
        file_content=FILE_FOR_SUCCESSFUL_OPERATION,
    )
    happy_response = EXPECTED_SERVICE_CENTER_SET_LICENSE_RESPONSE_TEMPLATE.format(
        success="true",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=PLATFORM_API_SOAP_OPERATIONS_URL,
        expected_request=happy_request,
        expected_response=happy_response
    )

    expected_request_for_unsuccessful_operation = EXPECTED_SERVICE_CENTER_SET_LICENSE_REQUEST_TEMPLATE.format(
        file_content=FILE_FOR_UNSUCCESSFUL_OPERATION,
    )
    expected_response_for_unsuccessful_operation = EXPECTED_SERVICE_CENTER_SET_LICENSE_RESPONSE_TEMPLATE_WITH_ERROR_TEXT.format(
        success="false",
        error_message="There was an internal error installing the license",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=PLATFORM_API_SOAP_OPERATIONS_URL,
        expected_request=expected_request_for_unsuccessful_operation,
        expected_response=expected_response_for_unsuccessful_operation
    )

    expected_request_for_network_error = EXPECTED_SERVICE_CENTER_SET_LICENSE_REQUEST_TEMPLATE.format(
        file_content=FILE_FOR_CATASTROPHIC_OPERATION,
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=PLATFORM_API_SOAP_OPERATIONS_URL,
        expected_request=expected_request_for_network_error,
        expected_response=None,
        http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR
    )


DEFAULT_DOMAIN = "localhost:8433"


@pytest.fixture(autouse=True, scope="session")
def boostrap():
    run_id = WireMockStubbing.new_run_id()

    with SSL.do_not_verify():
        _setup_mappings_for_service_center_set_license(run_id)

    yield run_id

    with SSL.do_not_verify():
        wiremock.delete_by_run_id(run_id)


def test_when_set_license_is_successful():
    with SSL.do_not_verify():
        service_center = PlatformServiceCenterFacade()

        happy_response = service_center.set_license(
            domain=DEFAULT_DOMAIN,
            authentication=ServiceCenterCredentials(username="admin_username", password="admin_password"),
            b64_license=FILE_FOR_SUCCESSFUL_OPERATION
        )

    assert happy_response


def test_when_set_license_is_unsuccessful():
    with SSL.do_not_verify():
        service_center = PlatformServiceCenterFacade()

        with pytest.raises(ServiceCenterError) as e:
            _ = service_center.set_license(
                domain=DEFAULT_DOMAIN,
                authentication=ServiceCenterCredentials(username="admin_username", password="admin_password"),
                b64_license=FILE_FOR_UNSUCCESSFUL_OPERATION
            )

    assert e.value.error_code == ""
    assert e.value.error_message == "There was an internal error installing the license"
    assert e.value.http_status_code == HTTPStatus.BAD_REQUEST


def test_when_set_license_with_catastrophic_error():
    with SSL.do_not_verify():
        service_center = PlatformServiceCenterFacade()

        with pytest.raises(ServiceCenterError) as e:
            _ = service_center.set_license(
                domain=DEFAULT_DOMAIN,
                authentication=ServiceCenterCredentials(username="admin_username", password="admin_password"),
                b64_license=FILE_FOR_CATASTROPHIC_OPERATION
            )

    assert e.value.error_code == ""
    assert e.value.error_message == "Server Error"
    assert e.value.http_status_code == HTTPStatus.INTERNAL_SERVER_ERROR
