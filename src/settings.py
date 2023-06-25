from pydantic import BaseSettings, HttpUrl


class Settings(BaseSettings):
    """These settings can be modified using env vars (case-insensitive)"""
    api_url_base: HttpUrl = "https://swapi.dev/api/"
    api_max_page_results: int = 10
    max_simultaneous_requests: int = 10
    max_request_retries: int = 3
    max_person_filter: int = 10
