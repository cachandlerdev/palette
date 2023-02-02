from dataclasses import dataclass

@dataclass
class Config:
    """Class for keeping track of application settings."""
    loaded_settings = False
    num_of_colors: int
    num_of_generated_colors: int
    colors = ["primary", "secondary", "accent"]