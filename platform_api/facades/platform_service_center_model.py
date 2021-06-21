from http import HTTPStatus
from typing import Dict

from pydantic import BaseModel, Field

from platform_api.facades.base_model import GenericError


class ServiceCenterError(GenericError):
    """Error class for Service Center web service exceptions"""

    def __init__(self, error_code: str, error_message: str, http_status_code: int = HTTPStatus.OK):
        super().__init__(error_code, error_message, http_status_code)


class ServiceCenterCredentials(BaseModel):
    """Authentication information for services"""

    username: str = Field(default="")
    password: str = Field(default="")
    password_encrypted: str = Field(default="")


class PlatformInfo(BaseModel):
    """
    Holds information about Service Center
    """

    version: str = Field(default="")
    serial: str = Field(default="")

    def __str__(self) -> str:
        return f"PlatformInfo({self.version},{self.serial})"


class ServiceCenterChangeUserPassword(BaseModel):
    """Service Center user information"""

    tenant_id: str = Field(..., alias="tenantId")
    environment_orn: str = Field(..., alias="environmentOrn")
    username: str = Field(..., alias="userName")
    new_password: str = Field(..., alias="newPassword")

    def __str__(self) -> str:
        return f"ServiceCenterChangeUserPassword(tenant_id: {self.tenant_id} environment_orn:{self.environment_orn} username:{self.username})"

    class Config:
        allow_population_by_field_name = True


class ServiceCenterUser(BaseModel):
    """Service Center user information"""

    name: str
    username: str = Field(default="", alias="userName")
    password: str
    email: str
    is_admin: bool = Field(default="", alias="isAdmin")

    def __str__(self) -> str:
        return f"ServiceCenterUser({self.name},{self.username},{self.email},{self.is_admin})"

    @classmethod
    def from_dict(cls, json_object: Dict):
        """
        Create a Service Center User from a json object

        Args:
            json_object (Dict): The json object representing the user
        Returns:
            ServiceCenterUser: A Service Center user deserialized from the json string
        """

        return cls(**json_object)

    class Config:
        allow_population_by_field_name = True


class SolutionDownloadResponse(BaseModel):
    """
    Holds information Solution Download Response from service center
    """

    file_content: str
    solution_download_op_id: int = Field(alias="solutionDownloadOpId")

    def __str__(self) -> str:
        return f"SolutionDownloadResponse({self.solution_download_op_id},{self.file_content})"

    class Config:
        allow_population_by_field_name = True
