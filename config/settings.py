from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass
class Settings:
    github_token: str
    github_username: str


def get_settings() -> Settings:
    """Load settings from environment variables."""
    load_dotenv()
    
    github_token = os.getenv("GITHUB_TOKEN")
    github_username = os.getenv("GITHUB_USERNAME")
    
    if not github_token:
        raise RuntimeError(
            "GITHUB_TOKEN environment variable is required. "
            "Please set it in your .env file or environment."
        )
    
    if not github_username:
        raise RuntimeError(
            "GITHUB_USERNAME environment variable is required. "
            "Please set it in your .env file or environment."
        )
    
    return Settings(
        github_token=github_token,
        github_username=github_username
    )