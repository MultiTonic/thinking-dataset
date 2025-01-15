# @file thinking_dataset/template/template_schema.py
# @description Defines the schema for templates.
# @version 1.0.0
# @license MIT


class TemplateSchema:
    GENERATE_CABLE = {
        "metadata": {
            "type": "object",
            "properties": {
                "purpose": {
                    "type": "string"
                },
                "agent": {
                    "type": "string"
                },
                "version": {
                    "type": "string"
                }
            },
            "required": ["purpose", "agent", "version"]
        },
        "system_prompt": {
            "type": "object",
            "properties": {
                "instructions": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "format": {
                    "type":
                    "object",
                    "properties": {
                        "thinking": {
                            "type": "string"
                        },
                        "reasoning": {
                            "type": "string"
                        },
                        "reflection": {
                            "type": "string"
                        },
                        "adjustment": {
                            "type": "string"
                        },
                        "output": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "thinking", "reasoning", "reflection", "adjustment",
                        "output"
                    ]
                }
            },
            "required": ["instructions", "format"]
        },
        "inspiration": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "example": {
            "type":
            "object",
            "properties": {
                "objective": {
                    "type": "string"
                },
                "arguments": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "action_requested": {
                    "type": "string"
                },
                "background_information": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "classification": {
                    "type": "string"
                },
                "distribution_list": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "closing": {
                    "type": "string"
                },
                "stakeholders": {
                    "type":
                    "object",
                    "properties": {
                        "government_officials": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "ngos": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "private_sector": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "international_bodies": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": [
                        "government_officials", "ngos", "private_sector",
                        "international_bodies"
                    ]
                }
            },
            "required": [
                "objective", "arguments", "action_requested",
                "background_information", "classification",
                "distribution_list", "closing", "stakeholders"
            ]
        },
        "output_format": {
            "type": "object",
            "properties": {
                "thinking": {
                    "type": "string"
                },
                "reflection": {
                    "type": "string"
                },
                "output_format": {
                    "type": "object",
                    "properties": {
                        "thinking": {
                            "type": "string"
                        },
                        "reflection": {
                            "type": "string"
                        },
                        "output": {
                            "type": "string"
                        }
                    },
                    "required": ["thinking", "reflection", "output"]
                }
            },
            "required": ["thinking", "reflection", "output_format"]
        }
    }
