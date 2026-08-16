import os
import pickle
import pandas as pd
import numpy as np
from itertools import product
from src.model import get_local_explanation

def get_all_combinations(industry):
    platforms = ["Instagram", "LinkedIn", "Facebook", "YouTube"]
    topics = [
        "Product Education", 
        "Behind the Scenes", 
        "Customer Testimonial", 
        "Promotional/Discount", 
        "Industry News", 
        "Lifestyle/Aesthetic", 
        "Meme/Trending"
    ]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = ["Morning (08:00-12:00)", "Afternoon (12:00-17:00)", "Evening (17:00-21:00)", "Night (21:00-08:00)"]
    
    valid_combos = []
    for platform, topic, day, time in product(platforms, topics, days, times):
        if platform == "YouTube":
            content_types = ["Video", "Shorts"]
        elif platform == "Instagram":
            content_types = ["Image", "Carousel", "Reel", "Video"]
        elif platform == "LinkedIn":
            content_types = ["Image", "Text", "Carousel", "Video"]
        else:
            content_types = ["Image", "Video", "Text", "Carousel", "Reel"]
            
        for content_type in content_types:
            valid_combos.append({
                "Industry": industry,
                "Platform": platform,
                "Content_Type": content_type,
                "Content_Topic": topic,
                "Posting_Day": day,
                "Posting_Time": time,
                "Ad_Spend": 0.0
            })
            
    return pd.DataFrame(valid_combos)

def recommend_best_content(industry, model_pipeline_path="src/models/marketing_intelligence_pipeline.pkl", shap_data_path="src/models/shap_explainer_data.pkl", top_n=3):
    if not os.path.exists(model_pipeline_path):
        raise FileNotFoundError(f"Model file not found at {model_pipeline_path}.")
        
    with open(model_pipeline_path, 'rb') as f:
        pipeline = pickle.load(f)
        
    combos_df = get_all_combinations(industry)
    combos_df['Predicted_Score'] = pipeline.predict(combos_df)
    top_combos = combos_df.sort_values(by='Predicted_Score', ascending=False).head(top_n).reset_index(drop=True)
    
    recommendations = []
    for idx, row in top_combos.iterrows():
        single_row = pd.DataFrame([row.drop('Predicted_Score').to_dict()])
        explanation = get_local_explanation(single_row, model_pipeline_path, shap_data_path)
        
        recommendations.append({
            'rank': idx + 1,
            'attributes': {
                'Platform': row['Platform'],
                'Content_Type': row['Content_Type'],
                'Content_Topic': row['Content_Topic'],
                'Posting_Day': row['Posting_Day'],
                'Posting_Time': row['Posting_Time']
            },
            'predicted_score': float(row['Predicted_Score']),
            'explanation': explanation
        })
        
    return recommendations

if __name__ == "__main__":
    test_industry = "B2B Tech/SaaS"
    print(f"Generating recommendations for: {test_industry}...")
    try:
        recs = recommend_best_content(test_industry, top_n=2)
        for r in recs:
            print(f"\nRank {r['rank']}: Score = {r['predicted_score']:.2f}")
            print(f"Attributes: {r['attributes']}")
    except FileNotFoundError as e:
        print(e)
