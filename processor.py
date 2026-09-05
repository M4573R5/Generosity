import os
from pydantic import BaseModel
from google import genai
from google.genai import types

api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

class StructuredVoiceReport(BaseModel):
    title: str
    inferred_category: str
    estimated_cost_usd: float
    urgency_rating: float  
    justification_summary: str

def process_raw_text(raw_transcript,model='gemini-3.6-flash'):
    validated_data = None 
    try:
        response = client.models.generate_content(
            model=model,
            contents=f"Analyze this field voice transmission and extract structured metadata: {raw_transcript}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StructuredVoiceReport,
                temperature=0.1
            ),
        )
        
        validated_data = StructuredVoiceReport.model_validate_json(response.text)
    except Exception as e:
        pass 
    
    return validated_data