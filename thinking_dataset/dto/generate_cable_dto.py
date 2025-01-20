# @file generate_cable_dto.py
# @description Data Transfer Object (DTO) for Generate Cable Schema
# @version 1.0.1
# @license MIT

from pydantic import BaseModel
from typing import List


class InitialThought(BaseModel):
    initial_thought: str


class Rationales(BaseModel):
    steps: List[str]


class Reasoning(BaseModel):
    rationales: List[Rationales]


class Reflections(BaseModel):
    reflection_steps: List[str]


class Stakeholders(BaseModel):
    government_officials: List[str]
    organizations: List[str]
    private_sector: List[str]
    international_bodies: List[str]


class Response(BaseModel):
    objective: str
    arguments: List[str]
    action_requested: str
    background_information: List[str]
    classification: str
    distribution_list: List[str]
    closing: str
    stakeholders: Stakeholders


class Output(BaseModel):
    thinking: InitialThought
    reasoning: Reasoning
    reflections: List[Reflections]
    response: Response


class GenerateCableSchema(BaseModel):
    output: Output
