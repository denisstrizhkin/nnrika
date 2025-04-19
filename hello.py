from google import genai

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "MyApp"
    api_key: Optional[str] = None
    debug: bool = False
    database_url: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

print(f"App Name: {settings.app_name}")
print(f"API Key: {settings.api_key}")
print(f"Debug: {settings.debug}")
print(f"Database URL: {settings.database_url}")


def main():
    client = genai.Client(api_key="YOUR_API_KEY")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="Explain how AI works"
    )
    print(response.text)


if __name__ == "__main__":
    main()
