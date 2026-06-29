from pydantic import BaseModel
from typing import List

class ICPConfig(BaseModel):
    industries: List[str] = ["SaaS", "Fintech", "Healthtech", "HR Tech"]
    min_headcount: int = 50
    max_headcount: int = 500
    funding_stages: List[str] = ["Series A", "Series B", "Series C"]
    countries: List[str] = ["US", "United States"]
    tech_stack_signals: List[str] = ["ADP", "Paychex", "Gusto", "BambooHR"]
    score_threshold: float = 0.6

class PersonaConfig(BaseModel):
    target_titles: List[str] = [
        "CHRO", "Chief Human Resources Officer",
        "VP of HR", "VP Human Resources",
        "Head of People", "Head of HR",
        "Director of People Operations",
    ]
    min_seniority: str = "director"

class TriggerConfig(BaseModel):
    keywords: List[str] = [
        "hiring HR", "head of HR", "CHRO appointed",
        "Series B funding", "people operations",
        "workforce expansion", "HR transformation",
    ]
    sources: List[str] = ["news", "jobs", "linkedin"]

class BusinessConfig(BaseModel):
    icp: ICPConfig = ICPConfig()
    personas: PersonaConfig = PersonaConfig()
    triggers: TriggerConfig = TriggerConfig()
    business_domain: str = "B2B SaaS HR/Payroll Software"
    value_proposition: str = "Modern payroll and HR platform replacing legacy ADP/Paychex"

DEFAULT_CONFIG = BusinessConfig()