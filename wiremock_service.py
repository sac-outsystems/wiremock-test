import json

import requests

DEFAULT_JSON_HEADER = {"Content-Type": "application/json"}
DEFAULT_XML_HEADER = {"Content-Type": "application/xml"}

WIREMOCK_DEFAULT_URL = "https://localhost:8433"


class WireMockService:
    """Handles call to the wiremock api"""

    def __init__(self, wiremock_base_url=WIREMOCK_DEFAULT_URL) -> None:
        self._base_url = wiremock_base_url
        self._wiremock_admin_url = f"{self._base_url}/__admin"
        self._mappings_url = f"{self._wiremock_admin_url}/mappings"
        self._requests_count = f"{self._wiremock_admin_url}/requests/count"

    @property
    def base_url(self) -> str:
        return self._base_url

    def post_mapping(self, data: dict, content_type=None):
        if content_type is None:
            content_type = DEFAULT_JSON_HEADER
        response = requests.post(
            self._mappings_url,
            json=data,
            headers=content_type,
        )
        response.raise_for_status()

        return json.loads(response.text)

    def get_mappings(self, data: dict = {}):
        """Get all stub mappings"""

        response = requests.get(self._mappings_url, json=data)
        response.raise_for_status()

        return json.loads(response.text)

    def delete_all_mappings(self):
        """Deletes all mappings"""

        response = requests.delete(self._mappings_url)
        response.raise_for_status()

        return json.loads(response.text)

    def delete_by_mappings_metadata(self, data: dict):
        """Delete stub mappings matching metadata"""

        url = f"{self._wiremock_admin_url}/mappings/remove-by-metadata"
        response = requests.post(url, json=data)
        response.raise_for_status()

        return json.loads(response.text)

    def delete_by_run_id(self, run_id: str):
        """Deletes stub mappings by run id

        Args:
            run_id (str): The unique identifier of the test run
        """
        self.delete_by_mappings_metadata(
            {
                "matchesJsonPath": {
                    "expression": "$.run_id",
                    "equalTo": run_id,
                }
            }
        )

    def delete_by_id(self, uuid: str):
        """Deletes stub mappings by id

        Args:
            uuid (str): The unique identifier of the test run
        """

        url = f"{self._wiremock_admin_url}/mappings/{uuid}"
        response = requests.delete(url)
        response.raise_for_status()

        return json.loads(response.text)

    def upload_file(self, file_name: str, file_content: str):
        response = requests.put(f"{self._wiremock_admin_url}/files/{file_name}", data=file_content)

        response.raise_for_status()

    def get_requests_count(self, data: dict):
        """Return count per request body

        Args:
            data (dict): the data to send in the request
        """

        response = requests.post(
            self._requests_count,
            json=data,
            headers=DEFAULT_JSON_HEADER,
        )
        response.raise_for_status()

        return json.loads(response.text)

    def reset_mappings(self):
        """Reset the  mappings"""

        url = f"{self._wiremock_admin_url}/mappings/reset?reloadStaticMappings=true"
        response = requests.post(url)
        response.raise_for_status()
