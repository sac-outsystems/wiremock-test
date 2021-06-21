from http import HTTPStatus

import pytest as pytest

import no_ssl_verification as SSL
import stubbing_utils as WireMockStubbing
from platform_api.facades.lifetime_facade import LifetimeFacade
from platform_api.facades.lifetime_model import LifetimeCredentials, LifetimeError, \
    LifetimeChangeUserPassword
from platform_api.facades.platform_service_center_facade import PlatformServiceCenterFacade
from wiremock_service import WireMockService, WIREMOCK_DEFAULT_URL

EXPECTED_SERVICE_CENTER_GET_PLATFORM_INFO_REQUEST_TEMPLATE = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:out="http://www.outsystems.com">
   <soapenv:Header/>
   <soapenv:Body>
      <out:GetPlatformInfo/>
   </soapenv:Body>
</soapenv:Envelope>"""

EXPECTED_SERVICE_CENTER_GET_PLATFORM_INFO_RESPONSE_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
    <GetPlatformInfoResponse xmlns="http://www.outsystems.com">
        <Version>{{randomValue length=2 type='NUMERIC'}}.{{randomValue length=5 type='NUMERIC'}}</Version>
        <Serial>{{randomValue length=24 type='ALPHABETIC'}}</Serial>
    </GetPlatformInfoResponse>
</soap:Body>
</soap:Envelope>"""

PLATFORM_API_SOAP_OPERATIONS_URL = "/ServiceCenter/OutSystemsPlatform.asmx?wsdl"


wiremock = WireMockService(WIREMOCK_DEFAULT_URL)


DEFAULT_DOMAIN = "localhost:8433"


@pytest.fixture(autouse=True, scope="session")
def boostrap():
    run_id = WireMockStubbing.new_run_id()

    with SSL.do_not_verify():
        WireMockStubbing.register_soap_mapping(
            wiremock=wiremock,
            run_id=run_id,
            soap_operations_url=PLATFORM_API_SOAP_OPERATIONS_URL,
            expected_request=EXPECTED_SERVICE_CENTER_GET_PLATFORM_INFO_REQUEST_TEMPLATE,
            expected_response=EXPECTED_SERVICE_CENTER_GET_PLATFORM_INFO_RESPONSE_TEMPLATE
        )

    yield run_id

    with SSL.do_not_verify():
        wiremock.delete_by_run_id(run_id)


def test_when_get_platform_info_is_successful():
    with SSL.do_not_verify():
        service_center = PlatformServiceCenterFacade()

        platform_info = service_center.get_platform_info(
            domain=DEFAULT_DOMAIN,
        )

    assert len(platform_info.serial) > 0
    assert len(platform_info.version) > 0
