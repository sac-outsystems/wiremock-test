import base64


class Base64Encoder:
    def __init__(self, encoding: str = "utf-8") -> None:
        super().__init__()

        self.encoding = encoding

    def from_base64_string_to_string(self, base64_string: str) -> str:
        """
        Converts a base 64 string it's string representation

        Args:
            base64_string (str): the base 64 string

        Raises:
            None

        Returns:
            str: the original string

        """
        return self.from_bytes_to_string(self.from_base64_string_to_bytes(base64_string))

    def from_string_to_base64_string(self, _string: str) -> str:
        """
        Converts a string to it's base64 string representation

        Args:
            _string (str): the string value

        Raises:
            None

        Returns:
            str: the base 64 string representation

        """
        return self.from_bytes_to_base64_string(self.from_string_to_bytes(_string))

    def from_bytes_to_base64_string(self, _bytes: bytes) -> str:
        """
        Converts the bytes sequence to it's string representation

        Args:
            _bytes (bytes): the sequence of bytes

        Raises:
            None

        Returns:
            str: the string representation of the bytes

        """
        return base64.b64encode(_bytes).decode(self.encoding)

    def from_base64_string_to_bytes(self, base64_string: str) -> bytes:
        """
        Converts the base 64 string to it's bytes representation

        Args:
            base64_string (str): the base 64 string value

        Raises:
            None

        Returns:
            bytes: the bytes representation of the string

        """
        return base64.b64decode(base64_string)

    def from_string_to_bytes(self, _string: str) -> bytes:
        """
        A helper to encode a string to bytes using the very same encoding of the service

        Args:
            _string (str): the string value

        Raises:
            None

        Returns:
            str: the bytes string representation

        """
        return _string.encode(self.encoding)

    def from_bytes_to_string(self, _bytes: bytes) -> str:
        """
        A helper to decode a byte sequence to it's string representation using the very same encoding of the service

        Args:
            _bytes (str): the bytes value

        Raises:
            None

        Returns:
            str: the bytes string representation

        """
        return _bytes.decode(self.encoding)
