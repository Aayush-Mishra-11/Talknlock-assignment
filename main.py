import os
import sys
import pandas as pd
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root directory is on Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.model import get_local_explanation
from src.recommender import recommend_best_content
from src.llm_layer import generate_marketing_brief

app = FastAPI(
    title="Talknlock AI Marketing Intelligence API",
    description="Backend API for Content Performance Prediction, Next Best Action Recommendations & Generative LLM Briefs",
    version="1.0.0"
)

# Configure CORS to allow requests from Vercel frontend and local development
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
allowed_origins = [
    "https://talknlock-assignment.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]

if allowed_origins_env:
    if allowed_origins_env.strip() == "*":
        allowed_origins = ["*"]
    else:
        extra_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
        allowed_origins.extend(extra_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in allowed_origins else list(set(allowed_origins)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PostDraftRequest(BaseModel):
    Industry: str = Field(..., example="B2B Tech/SaaS")
    Platform: str = Field(..., example="LinkedIn")
    Content_Type: str = Field(..., example="Carousel")
    Content_Topic: str = Field(..., example="Product Education")
    Posting_Day: str = Field(..., example="Tuesday")
    Posting_Time: str = Field(..., example="Morning (08:00-12:00)")
    Ad_Spend: float = Field(0.0, example=150.0)

class RecommendationRequest(BaseModel):
    Industry: str = Field(..., example="B2B Tech/SaaS")
    top_n: Optional[int] = Field(3, example=3)

class FullAnalysisRequest(PostDraftRequest):
    top_n: Optional[int] = Field(3, example=3)

@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "service": "Talknlock AI Marketing Intelligence API",
        "version": "1.0.0",
        "llm_provider": "Google Gemini API" if os.environ.get("GEMINI_API_KEY") else (
            "OpenAI API" if os.environ.get("OPENAI_API_KEY") else "Rule-based Engine / Ollama"
        )
    }

@app.post("/predict")
def predict_performance(draft: PostDraftRequest):
    try:
        input_df = pd.DataFrame([draft.dict()])
        explanation = get_local_explanation(input_df)
        return {
            "success": True,
            "prediction": explanation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/recommend")
def recommend_content(req: RecommendationRequest):
    try:
        recs = recommend_best_content(industry=req.Industry, top_n=req.top_n)
        return {
            "success": True,
            "recommendations": recs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

@app.post("/generate-brief")
def generate_brief(data: Dict[str, Any]):
    try:
        pred_details = data.get("prediction_details", {})
        recs = data.get("recommendations", [])
        brief = generate_marketing_brief(pred_details, recs)
        return {
            "success": True,
            "brief": brief
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brief generation error: {str(e)}")

@app.post("/analyze")
def full_analysis(req: FullAnalysisRequest):
    try:
        input_dict = {
            "Industry": req.Industry,
            "Platform": req.Platform,
            "Content_Type": req.Content_Type,
            "Content_Topic": req.Content_Topic,
            "Posting_Day": req.Posting_Day,
            "Posting_Time": req.Posting_Time,
            "Ad_Spend": req.Ad_Spend
        }
        input_df = pd.DataFrame([input_dict])
        
        explanation = get_local_explanation(input_df)
        recs = recommend_best_content(industry=req.Industry, top_n=req.top_n)
        
        pred_details_for_brief = {
            **input_dict,
            "Performance_Score": round(explanation['predicted_score'], 2)
        }
        brief = generate_marketing_brief(pred_details_for_brief, recs)
        
        return {
            "success": True,
            "prediction": explanation,
            "recommendations": recs,
            "brief": brief
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
