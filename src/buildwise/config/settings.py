"""Settings management for BuildWise CLI."""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Settings:
    """Manages application settings."""
    
    def __init__(self):
        """Initialize settings with default values."""
        self.config_dir = Path.home() / ".buildwise"
        self.config_file = self.config_dir / "config.json"
        
        # Default settings
        self._defaults = {
            "openai_api_key": "",
            "project_dir": str(self.config_dir / "projects"),
            "theme": "light",
            "default_location": "United States",
            "material_prices": {
                "concrete_per_yard": 150,
                "lumber_pine_per_bf": 3.0,
                "steel_per_pound": 0.85
            }
        }
        
        # Current settings
        self._settings = {}
        
        # Load settings
        self._ensure_config_dir()
        self._load_settings()
    
    def _ensure_config_dir(self):
        """Ensure config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        project_dir = Path(self._defaults["project_dir"])
        project_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_settings(self):
        """Load settings from config file."""
        if not self.config_file.exists():
            # Create with default settings
            self._settings = self._defaults.copy()
            self._save_settings()
        else:
            # Load from file
            try:
                with open(self.config_file, 'r') as f:
                    self._settings = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                # If file is corrupt or missing, use defaults
                self._settings = self._defaults.copy()
                self._save_settings()
    
    def _save_settings(self):
        """Save settings to config file."""
        with open(self.config_file, 'w') as f:
            json.dump(self._settings, f, indent=2)
    
    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key."""
        return self._settings.get("openai_api_key", "")
    
    @openai_api_key.setter
    def openai_api_key(self, value: str):
        """Set OpenAI API key."""
        self._settings["openai_api_key"] = value
        self._save_settings()
    
    @property
    def project_dir(self) -> str:
        """Get project directory."""
        return self._settings.get("project_dir", self._defaults["project_dir"])
    
    @project_dir.setter
    def project_dir(self, value: str):
        """Set project directory."""
        self._settings["project_dir"] = value
        Path(value).mkdir(parents=True, exist_ok=True)
        self._save_settings()
    
    @property
    def theme(self) -> str:
        """Get theme."""
        return self._settings.get("theme", "light")
    
    @theme.setter
    def theme(self, value: str):
        """Set theme."""
        self._settings["theme"] = value
        self._save_settings()
    
    @property
    def default_location(self) -> str:
        """Get default location."""
        return self._settings.get("default_location", "United States")
    
    @default_location.setter
    def default_location(self, value: str):
        """Set default location."""
        self._settings["default_location"] = value
        self._save_settings()
    
    @property
    def material_prices(self) -> Dict[str, float]:
        """Get material prices."""
        return self._settings.get("material_prices", self._defaults["material_prices"])
    
    def update_material_price(self, key: str, value: float):
        """Update material price."""
        if "material_prices" not in self._settings:
            self._settings["material_prices"] = {}
        
        self._settings["material_prices"][key] = value
        self._save_settings()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return self._settings.copy()

# Create a singleton instance
settings = Settings()
