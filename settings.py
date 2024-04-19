from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    rabbitmq_user: str
    rabbitmq_password: str
    rabbitmq_queue: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
