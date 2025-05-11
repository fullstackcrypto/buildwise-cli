"""Configuration settings for BuildWise CLI."""

import os
import json
from pathlib import Path
from typing import Dict, Optional

# Default configuration directory
DEFAULT_CONFIG_DIR = os.path.expanduser("~/.buildwise")
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_DIR, "config.json")


class Settings:
    """Configuration settings for BuildWise CLI."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize settings.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or DEFAULT_CONFIG_FILE
        self.config_dir = os.path.dirname(self.config_file)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            # Create default configuration
            os.makedirs(self.config_dir, exist_ok=True)
            default_config = {
                "openai_api_key": "",
                "project_dir": os.path.join(self.config_dir, "projects"),
                "theme": "light",
                "default_location": "United States",
                "material_prices": {
                    "concrete_per_yard": 150,
                    "lumber_pine_per_bf": 3.0,
                    "steel_per_pound": 0.85,
                },
            }
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Return default config if file is corrupted
            return {
                "openai_api_key": "",
                "project_dir": os.path.join(self.config_dir, "projects"),
                "theme": "light",
                "default_location": "United States",
                "material_prices": {
                    "concrete_per_yard": 150,
                    "lumber_pine_per_bf": 3.0,
                    "steel_per_pound": 0.85,
                },
            }
    
    def _save_config(self, config: Dict) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except IOError:
            print(f"Warning: Could not save configuration to {self.config_file}")
    
    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key."""
        # Check environment variable first
        env_key = os.environ.get("OPENAI_API_KEY")
        if env_key:
            return env_key
        
        # Then check config file
        return self._config.get("openai_api_key", "")
    
    @openai_api_key.setter
    def openai_api_key(self, value: str) -> None:
        """Set OpenAI API key."""
        self._config["openai_api_key"] = value
        self._save_config(self._config)
    
    @property
    def project_dir(self) -> str:
        """Get project directory."""
        return self._config.get("project_dir", os.path.join(self.config_dir, "projects"))
    
    @project_dir.setter
    def project_dir(self, value: str) -> None:
        """Set project directory."""
        self._config["project_dir"] = value
        self._save_config(self._config)
        
        # Ensure directory exists
        os.makedirs(value, exist_ok=True)
    
    @property
    def theme(self) -> str:
        """Get UI theme."""
        return self._config.get("theme", "light")
    
    @theme.setter
    def theme(self, value: str) -> None:
        """Set UI theme."""
        self._config["theme"] = value
        self._save_config(self._config)
    
    @property
    def default_location(self) -> str:
        """Get default location."""
        return self._config.get("default_location", "United States")
    
    @default_location.setter
    def default_location(self, value: str) -> None:
        """Set default location."""
        self._config["default_location"] = value
        self._save_config(self._config)
    
    @property
    def material_prices(self) -> Dict:
        """Get default material prices."""
        return self._config.get("material_prices", {
            "concrete_per_yard": 150,
            "lumber_pine_per_bf": 3.0,
            "steel_per_pound": 0.85,
        })
    
    def update_material_price(self, material: str, price: float) -> None:
        """Update a material price."""
        if "material_prices" not in self._config:
            self._config["material_prices"] = {}
        
        self._config["material_prices"][material] = price
        self._save_config(self._config)
    
    def get_material_price(self, material: str) -> Optional[float]:
        """Get a material price."""
        if "material_prices" not in self._config:
            return None
        
        return self._config["material_prices"].get(material)


# Create a global settings instance
settings = Settings()
