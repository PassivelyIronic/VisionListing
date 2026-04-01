from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Provider: "anthropic" | "openai" | "google"
    model_provider: str = "google"

    # Modele
    anthropic_model: str = "claude-3-5-haiku-20241022"
    openai_model: str = "gpt-4o-mini"
    google_model: str = "gemini-1.5-flash"

    # Klucze API
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""

    # Aplikacja
    app_env: str = "development"
    log_level: str = "INFO"


settings = Settings()