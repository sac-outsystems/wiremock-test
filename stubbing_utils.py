import uuid
from datetime import datetime

from wiremock_service import WireMockService


def new_run_id() -> str:
    return str(uuid.uuid4())


def register_soap_mapping(
        wiremock: WireMockService,
        run_id: str,
        soap_operations_url: str,
        expected_request: str,
        expected_response: str = None,
        http_status_code=200
):
    wiremock.post_mapping(
        {
            "request": {
                "method": "POST",
                "url": soap_operations_url,
                "bodyPatterns": [
                    {
                        "equalToXml": expected_request,
                        "enablePlaceholders": True
                    }
                ]
            },
            "response": {
                "status": http_status_code,
                "headers": {
                    "Content-Type": "application/xml"
                },
                "body": "" if expected_response is None else expected_response,
                "transformers": ["response-template"]
            },
            "persistent": True,
            "priority": 100,
            "metadata": {"run_id": run_id, "date": datetime.now().isoformat()},
        }
    )
