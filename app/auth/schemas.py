from sqlmodel import SQLModel


class TokenRefresh(SQLModel):
    """Schema for token refresh requests.

    This model is used to validate the request body when a client
    attempts to obtain a new access token using a refresh token.
    """

    refresh_token: str
