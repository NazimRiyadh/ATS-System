"""
Data models for ATS Pipeline using Pydantic for validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProficiencyLevel(str, Enum):
    """Skill proficiency levels"""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"

class Skill(BaseModel):
    """Skill with proficiency level"""
    name: str = Field(..., description="Skill name (e.g., Python, Machine Learning)")
    proficiency: str = Field(default="Intermediate", description="Proficiency level")
    years_experience: Optional[float] = Field(None, description="Years of experience with this skill")

class WorkExperience(BaseModel):
    """Work experience entry"""
    company: str = Field(..., description="Company name")
    role: str = Field(..., description="Job title/role")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM format)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM format or 'Present')")
    years_duration: float = Field(..., description="Duration in years")
    description: str = Field(default="", description="Job description and achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")

class Education(BaseModel):
    """Education entry"""
    degree: str = Field(..., description="Degree name (e.g., Bachelor of Science)")
    field: str = Field(..., description="Field of study (e.g., Computer Science)")
    institution: str = Field(..., description="University/Institution name")
    graduation_year: Optional[int] = Field(None, description="Year of graduation")
    gpa: Optional[float] = Field(None, description="GPA if available")

class CandidateProfile(BaseModel):
    """Complete candidate profile"""
    name: str = Field(..., description="Full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Current location")
    summary: str = Field(..., description="Professional summary/bio")
    skills: List[Skill] = Field(default_factory=list, description="List of skills")
    experience: List[WorkExperience] = Field(default_factory=list, description="Work history")
    education: List[Education] = Field(default_factory=list, description="Education history")
    total_years_experience: Optional[float] = Field(None, description="Total years of work experience")
    
    def calculate_total_experience(self) -> float:
        """Calculate total years of experience"""
        if self.total_years_experience:
            return self.total_years_experience
        return sum(exp.years_duration for exp in self.experience)

class JobRequirement(BaseModel):
    """Parsed job description requirements"""
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Full job description")
    required_skills: List[str] = Field(default_factory=list, description="Must-have skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have skills")
    min_years_experience: int = Field(default=0, description="Minimum years of experience")
    education_level: Optional[str] = Field(None, description="Required education level")
    location: Optional[str] = Field(None, description="Job location")

class SearchFilters(BaseModel):
    """Filters for candidate search"""
    required_skills: Optional[List[str]] = Field(None, description="Skills that must be present")
    min_years_experience: int = Field(default=0, description="Minimum total experience")
    max_years_experience: Optional[int] = Field(None, description="Maximum total experience")
    education_level: Optional[str] = Field(None, description="Minimum education level")
    location: Optional[str] = Field(None, description="Preferred location")
    companies: Optional[List[str]] = Field(None, description="Specific companies worked at")

class CandidateMatch(BaseModel):
    """Search result with scoring"""
    candidate_id: str
    name: str
    summary: str
    total_experience: float
    matched_skills: List[str] = Field(default_factory=list)
    
    # Scores
    vector_score: float = Field(default=0.0, description="Vector similarity score")
    skill_match_score: float = Field(default=0.0, description="Skill match percentage")
    experience_score: float = Field(default=0.0, description="Experience relevance score")
    education_score: float = Field(default=0.0, description="Education match score")
    final_score: float = Field(default=0.0, description="Combined final score")
    
    # Explanation
    match_reason: Optional[str] = Field(None, description="LLM-generated explanation")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "candidate_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Jane Doe",
                "summary": "Senior Python Developer with 8 years experience",
                "total_experience": 8.0,
                "matched_skills": ["Python", "Django", "PostgreSQL"],
                "vector_score": 0.92,
                "skill_match_score": 0.85,
                "final_score": 0.88
            }
        }
