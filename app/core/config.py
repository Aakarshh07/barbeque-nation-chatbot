from pydantic_settings import BaseSettings
from typing import Optional, Dict, List, ClassVar
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Barbeque Nation Chatbot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Retell AI Configuration
    RETELL_API_KEY: str = os.getenv("RETELL_API_KEY", "")
    
    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_DIR: str = "data/knowledge_base"
    PROMPTS_DIR: str = "data/prompts"
    
    # Token Configuration
    MAX_TOKENS_PER_RESPONSE: int = 800
    
    # Cities and Locations
    CITIES: ClassVar[Dict[str, List[str]]] = {
        "delhi": [
            "Connaught Place",
            "Unity Mall, Janakpuri",
            "Sector C, Vasant Kunj"
        ],
        "bangalore": [
            "JP Nagar",
            "Koramangala 1st Block",
            "Electronic City",
            "Indiranagar"
        ]
    }

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True

settings = Settings() 