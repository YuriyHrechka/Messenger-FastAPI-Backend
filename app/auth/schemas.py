from sqlmodel import SQLModel


class TokenRefresh(SQLModel):
    refresh_token: str
