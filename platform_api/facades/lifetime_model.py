from http import HTTPStatus
from typing import List

from pydantic import BaseModel, Field

from platform_api.facades.base_model import GenericError


class LifetimeError(GenericError):
    """Error class for Lifetime web service exceptions"""

    def __init__(self, error_code: str, error_message: str, http_status_code: int = HTTPStatus.OK):
        super().__init__(error_code, error_message, http_status_code)


class LifetimeCredentials(BaseModel):
    """Authentication information for services"""

    username: str = Field(default="")
    password: str = Field(default="")


class ApplySettingsMessage(BaseModel):
    step: str = Field(default="", alias="Step")
    message: str = Field(default="", alias="Message")
    message_type: str = Field(default="", alias="MessageType")

    class Config:
        allow_population_by_field_name = True


class ApplySettingsStatusResponse(BaseModel):
    """
    Represents an Infrastructure
    """

    status: str = Field(default="", alias="Status")
    messages: List[ApplySettingsMessage] = Field(default=[], alias="Messages")

    class Config:
        allow_population_by_field_name = True


class InactivateLifetimeUserRequest(BaseModel):
    """Info for lifetime user deletion"""

    tenant_id: str = Field(..., alias="tenantId")
    username: str = Field(..., alias="userName")

    def __str__(self) -> str:
        return f"DeleteLifetimeUser(tenant_id: {self.tenant_id} username:{self.username})"

    class Config:
        allow_population_by_field_name = True


class LifetimeChangeUserPassword(BaseModel):
    """Lifetime user/password information"""

    tenant_id: str = Field(..., alias="tenantId")
    username: str = Field(..., alias="userName")
    new_password: str = Field(..., alias="newPassword")

    def __str__(self) -> str:
        return f"LifetimeChangeUserPassword(tenant_id: {self.tenant_id} username:{self.username})"

    class Config:
        allow_population_by_field_name = True


class LifetimeUser(BaseModel):
    """Lifetime user information"""

    identifier: str = Field(default="")
    username: str = Field(default="", alias="userName")
    password: str
    name: str
    email: str
    role: str

    def __str__(self) -> str:
        return f"LifetimeUser({self.identifier},{self.username},{self.email},{self.role})"

    class Config:
        allow_population_by_field_name = True


class LifetimeEnvironment(BaseModel):
    """
    Represents an Infrastructure
    """

    key: str = Field(alias="Key")
    name: str = Field(alias="Name")
    environment_type: str = Field(default="", alias="EnvironmentType")
    is_lifetime: bool = Field(alias="IsLifeTime")
    host_name: str = Field(alias="HostName")

    class Config:
        allow_population_by_field_name = True


class SetPublicHostEnvironments(BaseModel):

    key: str = Field(alias="Key")
    name: str = Field(alias="Name")

    class Config:
        allow_population_by_field_name = True


class EnvironmentSetPublicHostResponse(BaseModel):

    environment_list: List[SetPublicHostEnvironments] = Field(default=[], alias="EnvironmentList")

    class Config:
        allow_population_by_field_name = True
