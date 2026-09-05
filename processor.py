import os
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

class StructuredVoiceReport(BaseModel):
    title: str
    inferred_category: str
    estimated_cost_usd: float
    urgency_rating: float  
    justification_summary: str

def process_raw_text(raw_transcript,model='gemini-3.6-flash'):
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
    return {
        "title" : validated_data.title,
        "inferred_category" : validated_data.inferred_category,
        "estimated_cost_usd" : validated_data.estimated_cost_usd,
        "urgency_rating" : validated_data.urgency_rating,
        "justification_summary" : validated_data.title
    } 