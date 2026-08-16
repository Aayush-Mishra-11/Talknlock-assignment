import os
import sys
import pickle
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.model import get_local_explanation
from src.recommender import recommend_best_content
from src.llm_layer import generate_marketing_brief

app = FastAPI(title="Talknlock AI-Powered Marketing Intelligence System")

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

class PredictionRequest(BaseModel):
    Industry: str
    Platform: str
    Content_Type: str
    Content_Topic: str
    Posting_Day: str
    Posting_Time: str
    Ad_Spend: float

class RecommendationRequest(BaseModel):
    Industry: str

MODEL_PATH = "src/models/marketing_intelligence_pipeline.pkl"
SHAP_PATH = "src/models/shap_explainer_data.pkl"

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    industries = [
        "Fashion & Retail", "B2B Tech/SaaS", "Food & Beverage", 
        "Fintech & Finance", "Health & Fitness", "Real Estate", 
        "E-Learning & Education", "Travel & Hospitality"
    ]
    platforms = ["Instagram", "LinkedIn", "Facebook", "YouTube"]
    content_types = ["Image", "Carousel", "Video", "Reel", "Shorts", "Text"]
    topics = [
        "Product Education", "Behind the Scenes", "Customer Testimonial", 
        "Promotional/Discount", "Industry News", "Lifestyle/Aesthetic", "Meme/Trending"
    ]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = ["Morning (08:00-12:00)", "Afternoon (12:00-17:00)", "Evening (17:00-21:00)", "Night (21:00-08:00)"]
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "industries": industries,
            "platforms": platforms,
            "content_types": content_types,
            "topics": topics,
            "days": days,
            "times": times
        }
    )

@app.post("/api/predict")
async def predict_performance(req: PredictionRequest):
    try:
        input_data = pd.DataFrame([{
            "Industry": req.Industry,
            "Platform": req.Platform,
            "Content_Type": req.Content_Type,
            "Content_Topic": req.Content_Topic,
            "Posting_Day": req.Posting_Day,
            "Posting_Time": req.Posting_Time,
            "Ad_Spend": req.Ad_Spend
        }])
        explanation = get_local_explanation(input_data, MODEL_PATH, SHAP_PATH)
        return explanation
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Models not trained yet.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend")
async def recommend_content(req: RecommendationRequest):
    try:
        recs = recommend_best_content(req.Industry, MODEL_PATH, SHAP_PATH, top_n=3)
        baseline_pred = {
            "Industry": req.Industry,
            "Platform": "Facebook",
            "Content_Type": "Image",
            "Content_Topic": "Promotional/Discount",
            "Posting_Time": "Morning (08:00-12:00)",
            "Performance_Score": 25.0
        }
        if recs:
            best_score = recs[0]['predicted_score']
            baseline_pred["Performance_Score"] = round(best_score * 0.6, 2)
        
        brief = generate_marketing_brief(baseline_pred, recs)
        return {
            "recommendations": recs,
            "brief": brief
        }
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Models not trained yet.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
