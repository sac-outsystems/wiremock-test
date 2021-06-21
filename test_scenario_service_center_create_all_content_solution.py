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

EXPECTED_SERVICE_CENTER_CREATE_ALL_CONTENT_SOLUTION_REQUEST_TEMPLATE = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:out="http://www.outsystems.com">
   <soapenv:Header/>
   <soapenv:Body>
      <out:CreateAllSolution>
         <out:AllSolutionName>{solution_name}</out:AllSolutionName>
         <out:username>${{xmlunit.ignore}}</out:username>
         <out:password>${{xmlunit.ignore}}</out:password>
      </out:CreateAllSolution>
   </soapenv:Body>   
</soapenv:Envelope>"""

EXPECTED_SERVICE_CENTER_CREATE_ALL_CONTENT_SOLUTION_RESPONSE_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
    <CreateAllSolutionResponse xmlns="http://www.outsystems.com">
        <SolutionId>{solution_id}</SolutionId>
    </CreateAllSolutionResponse>
</soap:Body>
</soap:Envelope>"""


PLATFORM_SOLUTIONS_SOAP_OPERATIONS_URL = "/ServiceCenter/Solutions.asmx?wsdl"

wiremock = WireMockService(WIREMOCK_DEFAULT_URL)


def _setup_mappings_for_service_center_all_content_solution(run_id: str):
    happy_request = EXPECTED_SERVICE_CENTER_CREATE_ALL_CONTENT_SOLUTION_REQUEST_TEMPLATE.format(
        solution_name="a_beautiful_name",
    )
    happy_response = EXPECTED_SERVICE_CENTER_CREATE_ALL_CONTENT_SOLUTION_RESPONSE_TEMPLATE.format(
        solution_id="666",
    )
    WireMockStubbing.register_soap_mapping(
        wiremock=wiremock,
        run_id=run_id,
        soap_operations_url=PLATFORM_SOLUTIONS_SOAP_OPERATIONS_URL,
        expected_request=happy_request,
        expected_response=happy_response
    )

    expected_request_for_network_error = EXPECTED_SERVICE_CENTER_CREATE_ALL_CONTENT_SOLUTION_REQUEST_TEMPLATE.format(
        solution_name="the_belzebu_name",
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
        _setup_mappings_for_service_center_all_content_solution(run_id)

    yield run_id

    with SSL.do_not_verify():
        wiremock.delete_by_run_id(run_id)


def test_when_create_all_content_solution_is_successful():
    with SSL.do_not_verify():
        service_center = PlatformServiceCenterFacade()

        response = service_center.create_all_solution(
            domain=DEFAULT_DOMAIN,
            authentication=ServiceCenterCredentials(username="admin_username", password="admin_password"),
            all_solution_name="a_beautiful_name"
        )

    assert response == 666


def test_when_create_all_content_solution_with_catastrophic_error():
    with SSL.do_not_verify():
        service_center = PlatformServiceCenterFacade()

        with pytest.raises(ServiceCenterError) as e:
            _ = service_center.create_all_solution(
                domain=DEFAULT_DOMAIN,
                authentication=ServiceCenterCredentials(username="admin_username", password="admin_password"),
                all_solution_name="the_belzebu_name"
            )

    assert e.value.error_code == ""
    assert e.value.error_message == "Server Error"
    assert e.value.http_status_code == HTTPStatus.INTERNAL_SERVER_ERROR
