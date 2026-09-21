"""
Groq AI service for MediLedger Nexus
"""

import json
import logging
from typing import Dict, List, Optional, Any

import httpx
from pydantic import BaseModel

from mediledger_nexus.core.config import get_settings
from mediledger_nexus.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class GroqMessage(BaseModel):
    """Groq chat message"""
    role: str  # "system", "user", "assistant"
    content: str


class GroqResponse(BaseModel):
    """Groq API response"""
    id: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    model: str


class GroqAIService:
    """Service for interacting with Groq AI API"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.temperature = settings.GROQ_TEMPERATURE
        self.base_url = "https://api.groq.com/openai/v1"
        
        if not self.api_key:
            logger.warning("Groq API key not configured")
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to Groq API"""
        if not self.api_key:
            raise ValueError("Groq API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                raise Exception(f"Groq API error: {response.status_code}")
            
            return response.json()
    
    async def chat_completion(
        self,
        messages: List[GroqMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Get chat completion from Groq"""
        try:
            data = {
                "model": self.model,
                "messages": [msg.dict() for msg in messages],
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
                "stream": False
            }
            
            response = await self._make_request("chat/completions", data)
            
            if response["choices"]:
                return response["choices"][0]["message"]["content"]
            else:
                raise Exception("No response from Groq API")
        
        except Exception as e:
            logger.error(f"Groq chat completion error: {e}")
            raise
    
    async def analyze_symptoms(self, symptoms: List[str], medical_history: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze symptoms and provide diagnostic insights"""
        try:
            system_prompt = """You are a medical AI assistant specializing in symptom analysis. 
            Provide diagnostic insights based on symptoms and medical history. 
            Always include disclaimers about consulting healthcare professionals.
            Respond in JSON format with: diagnosis, confidence, recommendations, urgency_level."""
            
            user_prompt = f"""
            Patient presents with symptoms: {', '.join(symptoms)}
            Medical history: {json.dumps(medical_history, indent=2)}
            
            Please analyze and provide diagnostic insights.
            """
            
            messages = [
                GroqMessage(role="system", content=system_prompt),
                GroqMessage(role="user", content=user_prompt)
            ]
            
            response = await self.chat_completion(messages)
            
            # Try to parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If not JSON, return structured response
                return {
                    "diagnosis": "Analysis completed",
                    "analysis": response,
                    "confidence": 0.7,
                    "recommendations": ["Consult with healthcare provider"],
                    "urgency_level": "moderate"
                }
        
        except Exception as e:
            logger.error(f"Symptom analysis error: {e}")
            return {
                "diagnosis": "Analysis unavailable",
                "error": str(e),
                "confidence": 0.0,
                "recommendations": ["Please consult with a healthcare provider"],
                "urgency_level": "unknown"
            }
    
    async def generate_health_insights(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized health insights"""
        try:
            system_prompt = """You are a health insights AI that provides personalized health recommendations 
            based on aggregated health data. Focus on preventive care and lifestyle recommendations.
            Respond with a list of insights in JSON format."""
            
            user_prompt = f"""
            Based on the following health data, provide personalized health insights:
            {json.dumps(health_data, indent=2)}
            
            Generate 3-5 actionable health insights.
            """
            
            messages = [
                GroqMessage(role="system", content=system_prompt),
                GroqMessage(role="user", content=user_prompt)
            ]
            
            response = await self.chat_completion(messages)
            
            try:
                insights = json.loads(response)
                if isinstance(insights, list):
                    return insights
                elif isinstance(insights, dict) and "insights" in insights:
                    return insights["insights"]
                else:
                    return [{"insight": response, "category": "general"}]
            except json.JSONDecodeError:
                return [{"insight": response, "category": "general"}]
        
        except Exception as e:
            logger.error(f"Health insights generation error: {e}")
            return [{"insight": "Health insights temporarily unavailable", "category": "system"}]
    
    async def analyze_research_data(self, research_query: str, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze research data for insights"""
        try:
            system_prompt = """You are a medical research AI that analyzes anonymized health data 
            to provide research insights. Focus on population health trends and patterns.
            Respond in JSON format with findings, statistical_significance, and recommendations."""
            
            user_prompt = f"""
            Research Query: {research_query}
            Data Summary: {json.dumps(data_summary, indent=2)}
            
            Provide research analysis and insights.
            """
            
            messages = [
                GroqMessage(role="system", content=system_prompt),
                GroqMessage(role="user", content=user_prompt)
            ]
            
            response = await self.chat_completion(messages)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "findings": response,
                    "statistical_significance": "unknown",
                    "recommendations": ["Further analysis needed"]
                }
        
        except Exception as e:
            logger.error(f"Research data analysis error: {e}")
            return {
                "findings": "Analysis unavailable",
                "error": str(e),
                "statistical_significance": "unknown",
                "recommendations": ["Please try again later"]
            }
    
    async def generate_emergency_summary(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate emergency medical summary"""
        try:
            system_prompt = """You are an emergency medical AI that creates concise medical summaries 
            for emergency responders. Focus on critical information: allergies, medications, conditions, blood type.
            Respond in JSON format with critical_info, allergies, medications, conditions, emergency_contacts."""
            
            user_prompt = f"""
            Generate emergency medical summary for:
            {json.dumps(patient_data, indent=2)}
            
            Focus on information critical for emergency responders.
            """
            
            messages = [
                GroqMessage(role="system", content=system_prompt),
                GroqMessage(role="user", content=user_prompt)
            ]
            
            response = await self.chat_completion(messages, temperature=0.1)  # Lower temperature for accuracy
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "critical_info": response,
                    "allergies": [],
                    "medications": [],
                    "conditions": [],
                    "emergency_contacts": []
                }
        
        except Exception as e:
            logger.error(f"Emergency summary generation error: {e}")
            return {
                "critical_info": "Emergency summary unavailable",
                "error": str(e),
                "allergies": [],
                "medications": [],
                "conditions": [],
                "emergency_contacts": []
            }
    
    async def federated_learning_insights(self, model_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze federated learning model updates for insights"""
        try:
            system_prompt = """You are a federated learning AI that analyzes model updates 
            to provide insights about population health trends while preserving privacy.
            Respond in JSON format with trends, patterns, and recommendations."""
            
            user_prompt = f"""
            Analyze federated learning model updates:
            {json.dumps(model_updates, indent=2)}
            
            Provide insights about health trends and patterns.
            """
            
            messages = [
                GroqMessage(role="system", content=system_prompt),
                GroqMessage(role="user", content=user_prompt)
            ]
            
            response = await self.chat_completion(messages)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "trends": response,
                    "patterns": [],
                    "recommendations": []
                }
        
        except Exception as e:
            logger.error(f"Federated learning insights error: {e}")
            return {
                "trends": "Analysis unavailable",
                "error": str(e),
                "patterns": [],
                "recommendations": []
            }
