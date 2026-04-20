from pydantic import BaseModel, Field, RootModel, field_validator
from typing import Dict, List


class Settings(BaseModel):
    """Model for general configuration settings."""

    optimality_gap: float = Field(default=0.001, ge=1e-4, le=0.1)
    solver_time_limit: float = Field(default=30, ge=10, le=600) #s
    overproduction_percentage: float = Field(default=0.05, ge=0, le=0.2)
    cost_overproduction_allowed: float = Field(default=1, ge=0, le=100)
    cost_cut: float = Field(default=0.2, gt=0, le=1)
    cost_setup: float = Field(default=14, gt=0, le=20)
    speed: float = Field(default=0, ge=0, le=1)
    min_length: float = Field(default=200, ge=0, le=10e3) #mm


class Widths(BaseModel):
    """Model for fabric's width information."""

    width: int = Field(ge=100, le=5000) #mm
    cost_per_meter: float = Field(default=15, gt=0, le=1000) #R$/m
    spread_head: int = Field(default=40, ge=0, le=500) #mm
    margin_top: int = Field(default=40, ge=0, le=500) #mm
    margin_bottom: int = Field(default=40, ge=0, le=500) #mm


class Fabric(BaseModel):
    """Model for fabric information."""

    name: str
    cut_order_fabric_id: str
    max_length: float = Field(default=20e3, ge=1e3, le=100e3) #mm
    max_layers: int = Field(default=200, ge=1, le=10e3)
    widths: List[Widths]


class Panel(BaseModel):
    """Model for panels information."""

    area: float = Field(gt=0) #mm2
    perimeter: float = Field(ge=0.1) #mm
    quantity: int = Field(default=5, ge=0, le=1000)
    width: float = Field(gt=0) #mm
    height: float = Field(gt=0) #mm


class Grades(BaseModel):
    """Model for grades information."""

    panels: List[Panel]


class Color(RootModel):
    """Model for demand's colors information."""
    
    root: Dict[str, int]

    @field_validator('root')
    @classmethod
    def check_integer_interval(cls, v: Dict[str, int]) -> Dict[str, int]:
        if (sum(v.values()) < 1):
            raise ValueError(f"Demand {v} is zero.")
        min_val = 0
        max_val = 50e3
        for key, value in v.items():
            if not (min_val <= value <= max_val):
                raise ValueError(f"Value for key '{key}' must be between {min_val} and {max_val} inclusive.")
        return v


class Patterns(BaseModel):
    """Model for patterns information."""

    name: str
    cut_order_pattern_id: int
    quantity: Dict[str, Color]
    grades: Dict[str, Grades]


class FilterConfig(BaseModel):
    """Model for base file configuration."""

    settings: Settings
    fabric: Fabric
    patterns: List[Patterns]
