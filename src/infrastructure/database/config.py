from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseSettings):
    DB_TYPE: str
    DB_CONNECTOR: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def uri(self) -> str:
        return (
            f"{self.DB_TYPE}+{self.DB_CONNECTOR}"
            f"://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env.non-dev", env_file_encoding="utf-8", extra="ignore"
    )


load_dotenv()

db_config = DBConfig()
