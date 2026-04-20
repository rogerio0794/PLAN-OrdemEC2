from pydantic import BaseModel, Field
from typing import Dict, List
from utils.class_validation import Settings, Fabric, Patterns


class SettingsOpt(Settings):
    """Model for general configuration settings."""

    contour_step: int = Field(default=50, ge=1, le=5000)


class Layout(BaseModel):
    """Model for layout information."""

    saving: float = Field(default=0.8, ge=0.1, le=1)
    fabric_width: int = Field(ge=100, le=5000) #mm
    spread_length: float = Field(ge=100, le=50e3) #mm
    total_perimeter: float = Field(ge=100, le=500e3) #mm
    grades: List[Dict[str, int]]


class OptimizationConfig(BaseModel):
    """Model for base file configuration."""

    settings: SettingsOpt
    fabric: Fabric
    patterns: List[Patterns]
    spread_results: Dict[int, List[List[Dict[str, int]]]]
    layouts: Dict[int, List[Layout]]
    demands: Dict[str, List[Dict[str, int]]]
    model_config = {
        "json_schema_extra": {
            "examples": [
{
    "settings": {
        "optimality_gap": 0.001,
        "solver_time_limit": 30.0,
        "overproduction_percentage": 0.05,
        "max_grade_combinations": 10,
        "grade_limit": 4,
        "max_length": 30000.0,
        "min_length": 1000.0,
        "cost_overproduction_allowed": 1.0,
        "cost_overproduction_not_allowed": 100.0,
        "contour_step": 103
    },
    "fabric": {
        "name": "algodão",
        "max_layers": 200,
        "widths": [
            {
                "width": 1500,
                "cost_per_meter": 15.43
            },
            {
                "width": 1800,
                "cost_per_meter": 18.51
            }
        ],
        "costs": {
            "cut_meter": 1.89,
            "layout_meter": 0.1,
            "layer": 0.75,
            "setup": 40.0
        }
    },
    "patterns": [
        {
            "name": "Bata motorista",
            "quantity": {
                "azul": {
                    "P": 100,
                    "G": 198,
                    "G2": 0
                },
                "preto": {
                    "P": 200,
                    "G": 290,
                    "G2": 125
                },
                "verde": {
                    "P": 50,
                    "G": 390,
                    "G2": 225
                }
            },
            "grades": {
                "P": {
                    "panels": [
                        {
                            "area": 48060.80586488542,
                            "perimeter": 1172.6775150202488,
                            "quantity": 2,
                            "width": 104.10000000000014,
                            "height": 499.0
                        },
                        {
                            "area": 316691.6560135774,
                            "perimeter": 2205.952322284541,
                            "quantity": 1,
                            "width": 556.4588976455836,
                            "height": 590.0439090096493
                        },
                        {
                            "area": 23354.999999999964,
                            "perimeter": 615.9999999999993,
                            "quantity": 1,
                            "width": 172.9999999999996,
                            "height": 135.0000000000001
                        },
                        {
                            "area": 28818.242552446503,
                            "perimeter": 661.9089188755062,
                            "quantity": 1,
                            "width": 182.0047280492936,
                            "height": 169.3218512643316
                        },
                        {
                            "area": 13905.000000000055,
                            "perimeter": 476.0000000000008,
                            "quantity": 1,
                            "width": 103.00000000000085,
                            "height": 135.0
                        },
                        {
                            "area": 35489.06425384147,
                            "perimeter": 855.586855737221,
                            "quantity": 2,
                            "width": 291.0773185084769,
                            "height": 184.66448875885192
                        },
                        {
                            "area": 27345.22558355333,
                            "perimeter": 775.1995991062961,
                            "quantity": 2,
                            "width": 268.79999999999995,
                            "height": 163.0999999999999
                        }
                    ]
                },
                "G": {
                    "panels": [
                        {
                            "area": 369152.8026007816,
                            "perimeter": 2376.414992147762,
                            "quantity": 1,
                            "width": 590.4588976455836,
                            "height": 650.0439090096493
                        },
                        {
                            "area": 32492.742758615877,
                            "perimeter": 702.6191950567263,
                            "quantity": 1,
                            "width": 194.0047280492936,
                            "height": 179.3218512643316
                        },
                        {
                            "area": 35489.06425384147,
                            "perimeter": 855.586855737221,
                            "quantity": 2,
                            "width": 291.0773185084769,
                            "height": 184.66448875885192
                        },
                        {
                            "area": 27345.22558355333,
                            "perimeter": 775.1995991062961,
                            "quantity": 2,
                            "width": 268.79999999999995,
                            "height": 163.0999999999999
                        },
                        {
                            "area": 23354.999999999964,
                            "perimeter": 615.9999999999993,
                            "quantity": 1,
                            "width": 172.9999999999996,
                            "height": 135.0000000000001
                        },
                        {
                            "area": 13905.000000000055,
                            "perimeter": 476.0000000000008,
                            "quantity": 1,
                            "width": 103.00000000000085,
                            "height": 135.0
                        },
                        {
                            "area": 51016.44136413287,
                            "perimeter": 1232.6740633400743,
                            "quantity": 2,
                            "width": 104.10000000000014,
                            "height": 528.9999999999995
                        }
                    ]
                },
                "G2": {
                    "panels": [
                        {
                            "area": 52479.386241424,
                            "perimeter": 1262.6754126145606,
                            "quantity": 2,
                            "width": 104.10000000000014,
                            "height": 543.9999999999995
                        },
                        {
                            "area": 35489.06425384147,
                            "perimeter": 855.586855737221,
                            "quantity": 2,
                            "width": 291.0773185084769,
                            "height": 184.66448875885192
                        },
                        {
                            "area": 27345.22558355333,
                            "perimeter": 775.1995991062961,
                            "quantity": 2,
                            "width": 268.79999999999995,
                            "height": 163.0999999999999
                        },
                        {
                            "area": 13905.000000000055,
                            "perimeter": 476.0000000000008,
                            "quantity": 1,
                            "width": 103.00000000000085,
                            "height": 135.0
                        },
                        {
                            "area": 23354.999999999964,
                            "perimeter": 615.9999999999993,
                            "quantity": 1,
                            "width": 172.9999999999996,
                            "height": 135.0000000000001
                        },
                        {
                            "area": 34412.49286170057,
                            "perimeter": 722.9768552560431,
                            "quantity": 1,
                            "width": 200.0047280492936,
                            "height": 184.3218512643316
                        },
                        {
                            "area": 391199.39200581587,
                            "perimeter": 2445.8196548980313,
                            "quantity": 1,
                            "width": 607.4588976455836,
                            "height": 670.0439090096493
                        }
                    ]
                }
            }
        }
    ],
    "spread_results": {
        "1500": [
            [
                {
                    "P": 1,
                    "G": 2,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 2,
                    "G": 4,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 2,
                    "G": 3,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 1,
                    "G": 3,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 3,
                    "G": 4,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 1,
                    "G": 4,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 2,
                    "G": 4,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 2,
                    "G": 2,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 4,
                    "G": 4,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 3,
                    "G": 3,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 3,
                    "G": 4,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 2,
                    "G": 3,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 4,
                    "G": 4,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 2,
                    "G": 2,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 1,
                    "G": 2,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 2,
                    "G": 4,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 3,
                    "G": 4,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 2,
                    "G": 3,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 3,
                    "G": 3,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 3,
                    "G": 4,
                    "G2": 3
                }
            ],
            [
                {
                    "P": 1,
                    "G": 4,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 0,
                    "G": 3,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 0,
                    "G": 4,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 0,
                    "G": 2,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 1,
                    "G": 4,
                    "G2": 3
                }
            ],
            [
                {
                    "P": 0,
                    "G": 4,
                    "G2": 3
                }
            ],
            [
                {
                    "P": 1,
                    "G": 3,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 1,
                    "G": 3,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 1,
                    "G": 4,
                    "G2": 4
                }
            ],
            [
                {
                    "P": 2,
                    "G": 4,
                    "G2": 3
                }
            ]
        ],
        "1800": [
            [
                {
                    "P": 1,
                    "G": 2,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 2,
                    "G": 4,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 2,
                    "G": 3,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 1,
                    "G": 3,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 3,
                    "G": 4,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 1,
                    "G": 4,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 2,
                    "G": 4,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 2,
                    "G": 2,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 4,
                    "G": 4,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 3,
                    "G": 3,
                    "G2": 0
                }
            ],
            [
                {
                    "P": 3,
                    "G": 4,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 2,
                    "G": 3,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 4,
                    "G": 4,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 2,
                    "G": 2,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 1,
                    "G": 2,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 2,
                    "G": 4,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 3,
                    "G": 4,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 2,
                    "G": 3,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 3,
                    "G": 3,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 3,
                    "G": 4,
                    "G2": 3
                }
            ],
            [
                {
                    "P": 1,
                    "G": 4,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 0,
                    "G": 3,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 0,
                    "G": 4,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 0,
                    "G": 2,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 1,
                    "G": 4,
                    "G2": 3
                }
            ],
            [
                {
                    "P": 0,
                    "G": 4,
                    "G2": 3
                }
            ],
            [
                {
                    "P": 1,
                    "G": 3,
                    "G2": 2
                }
            ],
            [
                {
                    "P": 1,
                    "G": 3,
                    "G2": 1
                }
            ],
            [
                {
                    "P": 1,
                    "G": 4,
                    "G2": 4
                }
            ],
            [
                {
                    "P": 2,
                    "G": 4,
                    "G2": 3
                }
            ]
        ]
    },
    "layouts": {
        "1500": [
            {
                "saving": 0.7985,
                "fabric_width": 1500,
                "spread_length": 1617.89,
                "total_perimeter": 29362.7,
                "grades": [
                    {
                        "P": 1,
                        "G": 2,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.8295,
                "fabric_width": 1500,
                "spread_length": 3114.76,
                "total_perimeter": 58725.4,
                "grades": [
                    {
                        "P": 2,
                        "G": 4,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.785,
                "fabric_width": 1500,
                "spread_length": 2725.18,
                "total_perimeter": 48827.44,
                "grades": [
                    {
                        "P": 2,
                        "G": 3,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.7967,
                "fabric_width": 1500,
                "spread_length": 2179.17,
                "total_perimeter": 39260.65,
                "grades": [
                    {
                        "P": 1,
                        "G": 3,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.8182,
                "fabric_width": 1500,
                "spread_length": 3650.5,
                "total_perimeter": 68292.19,
                "grades": [
                    {
                        "P": 3,
                        "G": 4,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.812,
                "fabric_width": 1500,
                "spread_length": 2685.48,
                "total_perimeter": 49158.61,
                "grades": [
                    {
                        "P": 1,
                        "G": 4,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.8133,
                "fabric_width": 1500,
                "spread_length": 3745.12,
                "total_perimeter": 68773.12,
                "grades": [
                    {
                        "P": 2,
                        "G": 4,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.7961,
                "fabric_width": 1500,
                "spread_length": 2129.12,
                "total_perimeter": 38929.49,
                "grades": [
                    {
                        "P": 2,
                        "G": 2,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.8195,
                "fabric_width": 1500,
                "spread_length": 4136.22,
                "total_perimeter": 77858.98,
                "grades": [
                    {
                        "P": 4,
                        "G": 4,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.7983,
                "fabric_width": 1500,
                "spread_length": 3184.76,
                "total_perimeter": 58394.23,
                "grades": [
                    {
                        "P": 3,
                        "G": 3,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.8281,
                "fabric_width": 1500,
                "spread_length": 4723.55,
                "total_perimeter": 88387.63,
                "grades": [
                    {
                        "P": 3,
                        "G": 4,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.8156,
                "fabric_width": 1500,
                "spread_length": 3189.76,
                "total_perimeter": 58875.16,
                "grades": [
                    {
                        "P": 2,
                        "G": 3,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.8251,
                "fabric_width": 1500,
                "spread_length": 5228.76,
                "total_perimeter": 97954.42,
                "grades": [
                    {
                        "P": 4,
                        "G": 4,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.7958,
                "fabric_width": 1500,
                "spread_length": 2710.66,
                "total_perimeter": 48977.21,
                "grades": [
                    {
                        "P": 2,
                        "G": 2,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.7911,
                "fabric_width": 1500,
                "spread_length": 2217.4,
                "total_perimeter": 39410.42,
                "grades": [
                    {
                        "P": 1,
                        "G": 2,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.8153,
                "fabric_width": 1500,
                "spread_length": 4303.32,
                "total_perimeter": 78820.84,
                "grades": [
                    {
                        "P": 2,
                        "G": 4,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.795,
                "fabric_width": 1500,
                "spread_length": 4338.22,
                "total_perimeter": 78339.91,
                "grades": [
                    {
                        "P": 3,
                        "G": 4,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.805,
                "fabric_width": 1500,
                "spread_length": 3806.12,
                "total_perimeter": 68922.88,
                "grades": [
                    {
                        "P": 2,
                        "G": 3,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.8095,
                "fabric_width": 1500,
                "spread_length": 4283.12,
                "total_perimeter": 78489.67,
                "grades": [
                    {
                        "P": 3,
                        "G": 3,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.8303,
                "fabric_width": 1500,
                "spread_length": 5267.88,
                "total_perimeter": 98435.35,
                "grades": [
                    {
                        "P": 3,
                        "G": 4,
                        "G2": 3
                    }
                ]
            },
            {
                "saving": 0.8146,
                "fabric_width": 1500,
                "spread_length": 3812.12,
                "total_perimeter": 69254.05,
                "grades": [
                    {
                        "P": 1,
                        "G": 4,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.7969,
                "fabric_width": 1500,
                "spread_length": 2833.34,
                "total_perimeter": 49789.31,
                "grades": [
                    {
                        "P": 0,
                        "G": 3,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.8163,
                "fabric_width": 1500,
                "spread_length": 3310.55,
                "total_perimeter": 59687.26,
                "grades": [
                    {
                        "P": 0,
                        "G": 4,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.7762,
                "fabric_width": 1500,
                "spread_length": 1740.8,
                "total_perimeter": 29843.63,
                "grades": [
                    {
                        "P": 0,
                        "G": 2,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.8303,
                "fabric_width": 1500,
                "spread_length": 4296.95,
                "total_perimeter": 79301.77,
                "grades": [
                    {
                        "P": 1,
                        "G": 4,
                        "G2": 3
                    }
                ]
            },
            {
                "saving": 0.8059,
                "fabric_width": 1500,
                "spread_length": 3926.87,
                "total_perimeter": 69734.98,
                "grades": [
                    {
                        "P": 0,
                        "G": 4,
                        "G2": 3
                    }
                ]
            },
            {
                "saving": 0.8038,
                "fabric_width": 1500,
                "spread_length": 3310.55,
                "total_perimeter": 59356.1,
                "grades": [
                    {
                        "P": 1,
                        "G": 3,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.8208,
                "fabric_width": 1500,
                "spread_length": 2678.45,
                "total_perimeter": 49308.38,
                "grades": [
                    {
                        "P": 1,
                        "G": 3,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.8185,
                "fabric_width": 1500,
                "spread_length": 4923.76,
                "total_perimeter": 89349.49,
                "grades": [
                    {
                        "P": 1,
                        "G": 4,
                        "G2": 4
                    }
                ]
            },
            {
                "saving": 0.8305,
                "fabric_width": 1500,
                "spread_length": 4780.89,
                "total_perimeter": 88868.56,
                "grades": [
                    {
                        "P": 2,
                        "G": 4,
                        "G2": 3
                    }
                ]
            }
        ],
        "1800": [
            {
                "saving": 0.7566,
                "fabric_width": 1800,
                "spread_length": 1422.92,
                "total_perimeter": 29362.7,
                "grades": [
                    {
                        "P": 1,
                        "G": 2,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.7979,
                "fabric_width": 1800,
                "spread_length": 2698.36,
                "total_perimeter": 58725.4,
                "grades": [
                    {
                        "P": 2,
                        "G": 4,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.823,
                "fabric_width": 1800,
                "spread_length": 2166.18,
                "total_perimeter": 48827.44,
                "grades": [
                    {
                        "P": 2,
                        "G": 3,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.7868,
                "fabric_width": 1800,
                "spread_length": 1839.0,
                "total_perimeter": 39260.65,
                "grades": [
                    {
                        "P": 1,
                        "G": 3,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.8082,
                "fabric_width": 1800,
                "spread_length": 3079.56,
                "total_perimeter": 68292.19,
                "grades": [
                    {
                        "P": 3,
                        "G": 4,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.7963,
                "fabric_width": 1800,
                "spread_length": 2282.18,
                "total_perimeter": 49158.61,
                "grades": [
                    {
                        "P": 1,
                        "G": 4,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.8067,
                "fabric_width": 1800,
                "spread_length": 3146.71,
                "total_perimeter": 68773.12,
                "grades": [
                    {
                        "P": 2,
                        "G": 4,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.7877,
                "fabric_width": 1800,
                "spread_length": 1793.0,
                "total_perimeter": 38929.49,
                "grades": [
                    {
                        "P": 2,
                        "G": 2,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.821,
                "fabric_width": 1800,
                "spread_length": 3440.56,
                "total_perimeter": 77858.98,
                "grades": [
                    {
                        "P": 4,
                        "G": 4,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.8111,
                "fabric_width": 1800,
                "spread_length": 2611.91,
                "total_perimeter": 58394.23,
                "grades": [
                    {
                        "P": 3,
                        "G": 3,
                        "G2": 0
                    }
                ]
            },
            {
                "saving": 0.8233,
                "fabric_width": 1800,
                "spread_length": 3959.0,
                "total_perimeter": 88387.63,
                "grades": [
                    {
                        "P": 3,
                        "G": 4,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.8017,
                "fabric_width": 1800,
                "spread_length": 2704.36,
                "total_perimeter": 58875.16,
                "grades": [
                    {
                        "P": 2,
                        "G": 3,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.8194,
                "fabric_width": 1800,
                "spread_length": 4387.88,
                "total_perimeter": 97954.42,
                "grades": [
                    {
                        "P": 4,
                        "G": 4,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.7936,
                "fabric_width": 1800,
                "spread_length": 2265.18,
                "total_perimeter": 48977.21,
                "grades": [
                    {
                        "P": 2,
                        "G": 2,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.8064,
                "fabric_width": 1800,
                "spread_length": 1812.82,
                "total_perimeter": 39410.42,
                "grades": [
                    {
                        "P": 1,
                        "G": 2,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.7965,
                "fabric_width": 1800,
                "spread_length": 3670.59,
                "total_perimeter": 78820.84,
                "grades": [
                    {
                        "P": 2,
                        "G": 4,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.8173,
                "fabric_width": 1800,
                "spread_length": 3516.79,
                "total_perimeter": 78339.91,
                "grades": [
                    {
                        "P": 3,
                        "G": 4,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.8031,
                "fabric_width": 1800,
                "spread_length": 3179.44,
                "total_perimeter": 68922.88,
                "grades": [
                    {
                        "P": 2,
                        "G": 3,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.8112,
                "fabric_width": 1800,
                "spread_length": 3561.52,
                "total_perimeter": 78489.67,
                "grades": [
                    {
                        "P": 3,
                        "G": 3,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.8008,
                "fabric_width": 1800,
                "spread_length": 4551.62,
                "total_perimeter": 98435.35,
                "grades": [
                    {
                        "P": 3,
                        "G": 4,
                        "G2": 3
                    }
                ]
            },
            {
                "saving": 0.8014,
                "fabric_width": 1800,
                "spread_length": 3229.05,
                "total_perimeter": 69254.05,
                "grades": [
                    {
                        "P": 1,
                        "G": 4,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.7829,
                "fabric_width": 1800,
                "spread_length": 2403.18,
                "total_perimeter": 49789.31,
                "grades": [
                    {
                        "P": 0,
                        "G": 3,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.7928,
                "fabric_width": 1800,
                "spread_length": 2840.58,
                "total_perimeter": 59687.26,
                "grades": [
                    {
                        "P": 0,
                        "G": 4,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.7917,
                "fabric_width": 1800,
                "spread_length": 1422.16,
                "total_perimeter": 29843.63,
                "grades": [
                    {
                        "P": 0,
                        "G": 2,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.7985,
                "fabric_width": 1800,
                "spread_length": 3723.15,
                "total_perimeter": 79301.77,
                "grades": [
                    {
                        "P": 1,
                        "G": 4,
                        "G2": 3
                    }
                ]
            },
            {
                "saving": 0.8097,
                "fabric_width": 1800,
                "spread_length": 3256.94,
                "total_perimeter": 69734.98,
                "grades": [
                    {
                        "P": 0,
                        "G": 4,
                        "G2": 3
                    }
                ]
            },
            {
                "saving": 0.8097,
                "fabric_width": 1800,
                "spread_length": 2738.46,
                "total_perimeter": 59356.1,
                "grades": [
                    {
                        "P": 1,
                        "G": 3,
                        "G2": 2
                    }
                ]
            },
            {
                "saving": 0.7955,
                "fabric_width": 1800,
                "spread_length": 2303.18,
                "total_perimeter": 49308.38,
                "grades": [
                    {
                        "P": 1,
                        "G": 3,
                        "G2": 1
                    }
                ]
            },
            {
                "saving": 0.7983,
                "fabric_width": 1800,
                "spread_length": 4207.1,
                "total_perimeter": 89349.49,
                "grades": [
                    {
                        "P": 1,
                        "G": 4,
                        "G2": 4
                    }
                ]
            },
            {
                "saving": 0.818,
                "fabric_width": 1800,
                "spread_length": 4045.31,
                "total_perimeter": 88868.56,
                "grades": [
                    {
                        "P": 2,
                        "G": 4,
                        "G2": 3
                    }
                ]
            }
        ]
    },
    "demands": {
        "azul": [
            {
                "P": 100,
                "G": 198,
                "G2": 0
            }
        ],
        "preto": [
            {
                "P": 200,
                "G": 290,
                "G2": 125
            }
        ],
        "verde": [
            {
                "P": 50,
                "G": 390,
                "G2": 225
            }
        ]
    }
}
            ]
        }
    }
