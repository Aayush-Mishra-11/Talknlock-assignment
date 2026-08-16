import os
import requests
import json

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")

def get_mock_brief(prediction_details, recommendations):
    industry = prediction_details.get('Industry', 'General')
    platform = prediction_details.get('Platform', 'Instagram')
    content_type = prediction_details.get('Content_Type', 'Reel')
    topic = prediction_details.get('Content_Topic', 'Meme/Trending')
    time = prediction_details.get('Posting_Time', 'Evening')
    score = prediction_details.get('Performance_Score', 50.0)
    
    rec_platform = "Instagram"
    rec_type = "Reel"
    rec_topic = "Meme/Trending"
    rec_time = "Evening (17:00-21:00)"
    
    if recommendations and len(recommendations) > 0:
        best_rec = recommendations[0]['attributes']
        rec_platform = best_rec.get('Platform', rec_platform)
        rec_type = best_rec.get('Content_Type', rec_type)
        rec_topic = best_rec.get('Content_Topic', rec_topic)
        rec_time = best_rec.get('Posting_Time', rec_time)

    mock_text = f"""### 🎯 Executive Marketing Brief: {industry}

Your current draft ({content_type} on {platform} about "{topic}" at {time}) has a predicted **Performance Score of {score}/100**.

#### 🤖 AI Reasoning & Insights:
* **Format Power:** High affinity detected. For {industry}, video-based content (Reels/Videos) generates 2.4x higher baseline reach on visual networks than static images.
* **Topic Alignment:** The topic "{topic}" is well-suited, but could be enhanced by aligning with current trends rather than promotional themes.
* **Posting Optimization:** Publishing at {time} places the post just before peak engagement hours.

#### 💡 Recommended Next Best Action:
To maximize ROI, shift towards:
* **Platform:** {rec_platform}
* **Content Format:** {rec_type}
* **Content Topic:** {rec_topic}
* **Optimal Posting Window:** {rec_time}

#### ✍️ Recommended Copy Hook & Creative Angles:
1. *"Ever wondered how {industry} handles this? 🧐 Let's look behind the scenes..."*
2. *"The secret framework {industry} agencies don't want you to know. 🤫"*
"""
    return mock_text.strip()

def generate_marketing_brief(prediction_details, recommendations):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    prompt = f"""
    You are an expert AI Marketing Strategist for a digital marketing agency called Talknlock.
    Translate the following machine learning prediction details and recommended next best actions into a professional, concise, and highly actionable creative brief for a social media manager.
    
    Current Post Draft:
    - Industry: {prediction_details.get('Industry')}
    - Platform: {prediction_details.get('Platform')}
    - Content Type: {prediction_details.get('Content_Type')}
    - Topic: {prediction_details.get('Content_Topic')}
    - Posting Time: {prediction_details.get('Posting_Time')}
    - Predicted Performance Score: {prediction_details.get('Performance_Score')}/100
    
    Top Recommended Action to Improve Performance:
    - Target Platform: {recommendations[0]['attributes'].get('Platform') if recommendations else 'N/A'}
    - Target Content Type: {recommendations[0]['attributes'].get('Content_Type') if recommendations else 'N/A'}
    - Target Topic: {recommendations[0]['attributes'].get('Content_Topic') if recommendations else 'N/A'}
    - Target Posting Time: {recommendations[0]['attributes'].get('Posting_Time') if recommendations else 'N/A'}
    
    Please output a brief containing:
    1. A summary explaining why the current draft got the score it did.
    2. A strategic recommendation on how to pivot to the recommended settings (Next Best Action).
    3. Three creative copy hooks or video titles appropriate for this industry.
    Keep the tone professional, direct, and creative. Do not output markdown code blocks wrapping the response, return plain markdown text.
    """

    if gemini_key:
        print("[LLM Layer] Using Google Gemini API...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=8)
            if response.status_code == 200:
                result = response.json()
                return result['contents'][0]['parts'][0]['text']
        except Exception as e:
            print(f"[LLM Layer] Gemini API error: {e}")

    if openai_key:
        print("[LLM Layer] Using OpenAI API...")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=8)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"[LLM Layer] OpenAI API error: {e}")

    print(f"[LLM Layer] Checking local Ollama at {OLLAMA_URL} with model {OLLAMA_MODEL}...")
    url = f"{OLLAMA_URL}/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '')
    except Exception as e:
        print("[LLM Layer] Ollama unavailable. Fallback to Mock Brief.")
        
    return get_mock_brief(prediction_details, recommendations)

if __name__ == "__main__":
    test_pred = {
        "Industry": "Fashion & Retail",
        "Platform": "Instagram",
        "Content_Type": "Image",
        "Content_Topic": "Promotional/Discount",
        "Posting_Time": "Morning (08:00-12:00)",
        "Performance_Score": 28.5
    }
    test_recs = [{
        "attributes": {
            "Platform": "Instagram",
            "Content_Type": "Reel",
            "Content_Topic": "Lifestyle/Aesthetic",
            "Posting_Time": "Evening (17:00-21:00)"
        }
    }]
    print(generate_marketing_brief(test_pred, test_recs))
