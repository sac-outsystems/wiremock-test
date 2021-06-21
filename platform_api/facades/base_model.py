"""Base model classes"""

import json


class GenericError(Exception):
    """Error class for web service exceptions"""

    def __init__(self, error_code: str, error_message: str, http_status_code: int = 200):
        super().__init__(error_code, error_message)
        self.error_code = error_code
        self.error_message = error_message
        self.http_status_code = http_status_code

    def to_json(self, indent: int = None) -> str:
        """Converts object to json string

        Args:
            indent (int, optional): The number of spaces to indent the json. Defaults to None.

        Returns:
            str: the json string representing the object
        """

        return json.dumps(
            {"errorMessage": self.error_message, "errorType": self.error_code, "httpStatusCode": self.http_status_code},
            indent=indent,
        )

    def to_return_lambda(self) -> dict:
        """
        Converts object to json string

        Args:
            indent (int, optional): The number of spaces to indent the json. Defaults to None.

        Returns:
            str: the json string representing the object
        """
        body = {
            "message": self.error_message,
            "code": self.error_code,
        }

        resp = {
            "statusCode": self.http_status_code,
            "body": json.dumps(body),
        }

        return resp
