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

EXPECTED_SERVICE_CENTER_SOLUTION_DOWNLOAD_REQUEST_TEMPLATE = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:out="http://www.outsystems.com">
   <soapenv:Header/>
   <soapenv:Body>
      <out:Download>
         <out:SolutionName>{solution_name}</out:SolutionName>
         <out:SolutionVersionId>{solution_version_id}</out:SolutionVersionId>
         <out:username>${{xmlunit.ignore}}</out:username>
         <out:password>${{xmlunit.ignore}}</out:password>
      </out:Download>
   </soapenv:Body>   
</soapenv:Envelope>"""

EXPECTED_SERVICE_CENTER_SOLUTION_DOWNLOAD_RESPONSE_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
    <DownloadResponse xmlns="http://www.outsystems.com">
        <SolutionDownloadOpId>{solution_download_operation_id}</SolutionDownloadOpId>
        <file>{file_content}</file>
    </DownloadResponse>
</soap:Body>
</soap:Envelope>"""


PLATFORM_SOLUTIONS_SOAP_OPERATIONS_URL = "/ServiceCenter/Solutions.asmx?wsdl"

wiremock = WireMockService(WIREMOCK_DEFAULT_URL)

FILE_FOR_SUCCESSFUL_OPERATION = Base64Encoder().from_string_to_base64_string("the_master_solution_file")


def _setup_mappings_for_service_center_solution_download(run_id: str):
    happy_request = EXPECTED_SERVICE_CENTER_SOLUTION_DOWNLOAD_REQUEST_TEMPLATE.format(
        solution_name="the_master_solution",
        solution_version_id="1000",
    )
    happy_response = EXPECTED_SERVICE_CENTER_SOLUTION_DOWNLOAD_RESPONSE_TEMPLATE.format(
        solution_download_operation_id="1000",
        file_content=FILE_FOR_SUCCESSFUL_OPERATION,
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=PLATFORM_SOLUTIONS_SOAP_OPERATIONS_URL,
        expected_request=happy_request,
        expected_response=happy_response
    )

    expected_request_for_network_error = EXPECTED_SERVICE_CENTER_SOLUTION_DOWNLOAD_REQUEST_TEMPLATE.format(
        solution_name="the_belzebu_solution_name",
        solution_version_id="666",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=PLATFORM_SOLUTIONS_SOAP_OPERATIONS_URL,
        expected_request=expected_request_for_network_error,
        expected_response=None,
        http_status_code=HTTPStatus.INTERNAL_SERVER_ERROR
    )


DEFAULT_DOMAIN = "localhost:8433"


@pytest.fixture(autouse=True, scope="session")
def boostrap():
    run_id = WireMockStubbing.new_run_id()

    with SSL.do_not_verify():
        _setup_mappings_for_service_center_solution_download(run_id)

    yield run_id

    with SSL.do_not_verify():
        wiremock.delete_by_run_id(run_id)


def test_when_solution_download_is_successful():
    with SSL.do_not_verify():
        service_center = PlatformServiceCenterFacade()

        response = service_center.solution_download(
            domain=DEFAULT_DOMAIN,
            authentication=ServiceCenterCredentials(username="admin_username", password="admin_password"),
            solution_name="the_master_solution",
            solution_version_id=1000
        )

    assert response.solution_download_op_id == 1000
    assert len(response.file_content) > 0
    assert Base64Encoder().from_base64_string_to_string(response.file_content) == "the_master_solution_file"


def test_when_create_all_content_solution_with_catastrophic_error():
    with SSL.do_not_verify():
        service_center = PlatformServiceCenterFacade()

        with pytest.raises(ServiceCenterError) as e:
            _ = service_center.solution_download(
                domain=DEFAULT_DOMAIN,
                authentication=ServiceCenterCredentials(username="admin_username", password="admin_password"),
                solution_name="the_belzebu_solution_name",
                solution_version_id=666
            )

    assert e.value.error_code == ""
    assert e.value.error_message == "Server Error"
    assert e.value.http_status_code == HTTPStatus.INTERNAL_SERVER_ERROR
