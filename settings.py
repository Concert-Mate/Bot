from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = ''
    rabbitmq_user: str = 'rabbit-admin'
    rabbitmq_password: str = 'rabbit-password'
    rabbitmq_queue: str = 'new-concerts-queue'
    rabbitmq_host: str = 'localhost'
    rabbitmq_port: int = 5672
    user_service_host: str = 'localhost'
    user_service_port: int = 8080
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str = 'redis-password'

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
