import os
import numpy as np
import pandas as pd

np.random.seed(42)

def generate_marketing_dataset(num_records=1500):
    clients = [f"Client_{chr(65+i)}" for i in range(10)]
    client_industry_map = {
        "Client_A": "Fashion & Retail",
        "Client_B": "Fashion & Retail",
        "Client_C": "B2B Tech/SaaS",
        "Client_D": "B2B Tech/SaaS",
        "Client_E": "Food & Beverage",
        "Client_F": "Fintech & Finance",
        "Client_G": "Health & Fitness",
        "Client_H": "Real Estate",
        "Client_I": "E-Learning & Education",
        "Client_J": "Travel & Hospitality"
    }
    
    platforms = ["Instagram", "LinkedIn", "Facebook", "YouTube"]
    content_types = ["Image", "Carousel", "Video", "Reel", "Shorts", "Text"]
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
    
    records = []
    for i in range(num_records):
        record_id = f"REC{i+1:04d}"
        client = np.random.choice(clients)
        industry = client_industry_map[client]
        
        if industry == "B2B Tech/SaaS":
            platform_probs = [0.20, 0.65, 0.10, 0.05]
        elif industry in ["Fashion & Retail", "Food & Beverage"]:
            platform_probs = [0.65, 0.05, 0.20, 0.10]
        elif industry == "Fintech & Finance":
            platform_probs = [0.25, 0.45, 0.20, 0.10]
        elif industry == "Travel & Hospitality":
            platform_probs = [0.50, 0.10, 0.20, 0.20]
        else:
            platform_probs = [0.35, 0.25, 0.25, 0.15]
            
        platform = np.random.choice(platforms, p=platform_probs)
        
        if platform == "YouTube":
            content_type = np.random.choice(["Video", "Shorts"], p=[0.60, 0.40])
        elif platform == "Instagram":
            content_type = np.random.choice(["Image", "Carousel", "Reel", "Video"], p=[0.20, 0.40, 0.35, 0.05])
        elif platform == "LinkedIn":
            content_type = np.random.choice(["Image", "Text", "Carousel", "Video"], p=[0.30, 0.40, 0.20, 0.10])
        else:
            content_type = np.random.choice(["Image", "Video", "Text", "Carousel", "Reel"], p=[0.30, 0.30, 0.20, 0.10, 0.10])
            
        topic = np.random.choice(topics)
        day = np.random.choice(days)
        time = np.random.choice(times)
        
        is_paid = np.random.rand() < 0.40
        ad_spend = round(float(np.random.exponential(scale=150.0) + 10.0), 2) if is_paid else 0.0
            
        base_impressions = {
            "Instagram": 600, "LinkedIn": 350, "Facebook": 400, "YouTube": 700
        }[platform]
        
        content_multiplier = {
            "Image": 1.0, "Carousel": 1.3, "Video": 1.5, "Reel": 2.0, "Shorts": 1.8, "Text": 0.8
        }[content_type]
        
        noise = max(0.1, np.random.normal(loc=1.0, scale=0.18))
        impressions = int((base_impressions * content_multiplier * noise) + (ad_spend * 8.5))
        reach = int(impressions * np.random.uniform(0.65, 0.90))
        
        topic_multiplier = {
            "Meme/Trending": 1.7,
            "Lifestyle/Aesthetic": 1.3,
            "Behind the Scenes": 1.2,
            "Product Education": 1.0,
            "Customer Testimonial": 1.1,
            "Industry News": 0.9,
            "Promotional/Discount": 0.8
        }[topic]
        
        is_b2c = industry in ["Fashion & Retail", "Food & Beverage", "Travel & Hospitality", "Health & Fitness"]
        if is_b2c:
            day_multiplier = 1.35 if day in ["Friday", "Saturday", "Sunday"] else 0.85
        else:
            day_multiplier = 1.30 if day in ["Tuesday", "Wednesday", "Thursday"] else 0.70
            
        if is_b2c:
            if time == "Night (21:00-08:00)":
                time_multiplier = 1.50
            elif time == "Evening (17:00-21:00)":
                time_multiplier = 1.30
            elif time == "Morning (08:00-12:00)":
                time_multiplier = 0.80
            else:
                time_multiplier = 0.90
        else:
            if time == "Morning (08:00-12:00)":
                time_multiplier = 1.40
            elif time == "Afternoon (12:00-17:00)":
                time_multiplier = 1.10
            elif time == "Evening (17:00-21:00)":
                time_multiplier = 0.80
            else:
                time_multiplier = 0.40
        
        base_er = {
            "Instagram": 0.05, "LinkedIn": 0.03, "Facebook": 0.02, "YouTube": 0.04
        }[platform]
        
        er_noise = max(0.005, np.random.normal(loc=1.0, scale=0.15))
        actual_er = base_er * topic_multiplier * day_multiplier * time_multiplier * er_noise
        total_engagements = int(reach * actual_er)
        
        likes = int(total_engagements * np.random.uniform(0.70, 0.85))
        comments = int(total_engagements * np.random.uniform(0.05, 0.12))
        shares = int(total_engagements * np.random.uniform(0.03, 0.08))
        saves = int(total_engagements * np.random.uniform(0.02, 0.08))
        
        click_rate = 0.015 if topic == "Promotional/Discount" else 0.008
        clicks = int(impressions * click_rate * np.random.uniform(0.8, 1.2))
        if is_paid:
            clicks += int(ad_spend * 0.15)
            
        lead_conv_rate = np.random.uniform(0.02, 0.06)
        if topic in ["Product Education", "Customer Testimonial", "Promotional/Discount"]:
            lead_conv_rate += 0.03
        leads = int(clicks * lead_conv_rate)
        
        industry_lead_value = {
            "B2B Tech/SaaS": 150.0,
            "Real Estate": 300.0,
            "Fintech & Finance": 120.0,
            "Fashion & Retail": 45.0,
            "Food & Beverage": 25.0,
            "Health & Fitness": 60.0,
            "E-Learning & Education": 50.0,
            "Travel & Hospitality": 100.0
        }[industry]
        revenue = round(float(leads * industry_lead_value * np.random.uniform(0.9, 1.1)), 2)
        
        if content_type in ["Video", "Reel", "Shorts"]:
            video_views = int(impressions * np.random.uniform(0.35, 0.55))
            watch_time = round(float(video_views * np.random.uniform(3.0, 15.0)), 2)
        else:
            video_views = 0
            watch_time = 0.0
            
        er_target = 0.08
        eng_score = min(100.0, (actual_er / er_target) * 100)
        reach_score = min(100.0, (np.log1p(reach) / np.log1p(25000)) * 100)
        
        if is_paid and ad_spend > 0:
            roi = revenue / ad_spend
            conv_score = min(100.0, (roi / 4.0) * 50 + min(50.0, leads * 5))
        else:
            conv_score = min(100.0, (leads / 5.0) * 100)
            
        perf_score = round(float(0.40 * eng_score + 0.30 * reach_score + 0.30 * conv_score), 2)
        perf_score = min(100.0, max(0.0, perf_score))
        
        records.append({
            "Record_ID": record_id,
            "Client": client,
            "Industry": industry,
            "Platform": platform,
            "Content_Type": content_type,
            "Content_Topic": topic,
            "Posting_Day": day,
            "Posting_Time": time,
            "Ad_Spend": ad_spend,
            "Impressions": impressions,
            "Reach": reach,
            "Likes": likes,
            "Comments": comments,
            "Shares": shares,
            "Saves": saves,
            "Clicks": clicks,
            "Leads": leads,
            "Revenue": revenue,
            "Video_Views": video_views,
            "Watch_Time_Sec": watch_time,
            "Performance_Score": perf_score
        })
        
    df = pd.DataFrame(records)
    
    for idx in np.random.choice(range(num_records), size=10, replace=False):
        df.loc[idx, 'Ad_Spend'] = 0.0
        df.loc[idx, 'Impressions'] *= 15
        df.loc[idx, 'Reach'] = int(df.loc[idx, 'Impressions'] * 0.85)
        df.loc[idx, 'Likes'] *= 12
        df.loc[idx, 'Shares'] *= 15
        df.loc[idx, 'Saves'] *= 10
        df.loc[idx, 'Performance_Score'] = 98.50
        
    for idx in np.random.choice(range(num_records), size=10, replace=False):
        df.loc[idx, 'Ad_Spend'] = 500.0
        df.loc[idx, 'Impressions'] = 1500
        df.loc[idx, 'Reach'] = 1200
        df.loc[idx, 'Likes'] = 1
        df.loc[idx, 'Comments'] = 0
        df.loc[idx, 'Shares'] = 0
        df.loc[idx, 'Saves'] = 0
        df.loc[idx, 'Clicks'] = 0
        df.loc[idx, 'Leads'] = 0
        df.loc[idx, 'Revenue'] = 0.0
        df.loc[idx, 'Performance_Score'] = 5.20
        
    for idx in np.random.choice(range(num_records), size=5, replace=False):
        df.loc[idx, 'Client'] = 'Client_C' 
        df.loc[idx, 'Industry'] = 'B2B Tech/SaaS'
        df.loc[idx, 'Platform'] = 'Instagram'
        df.loc[idx, 'Content_Type'] = 'Reel'
        df.loc[idx, 'Content_Topic'] = 'Meme/Trending'
        df.loc[idx, 'Impressions'] = 45000
        df.loc[idx, 'Reach'] = 40000
        df.loc[idx, 'Likes'] = 5200
        df.loc[idx, 'Comments'] = 450
        df.loc[idx, 'Shares'] = 1200
        df.loc[idx, 'Saves'] = 800
        df.loc[idx, 'Clicks'] = 650
        df.loc[idx, 'Leads'] = 12
        df.loc[idx, 'Revenue'] = 1800.00
        df.loc[idx, 'Video_Views'] = 35000
        df.loc[idx, 'Watch_Time_Sec'] = 175000.00
        df.loc[idx, 'Performance_Score'] = 94.80

    return df

if __name__ == "__main__":
    os.makedirs("Dataset", exist_ok=True)
    df = generate_marketing_dataset(1500)
    output_path = os.path.join("Dataset", "synthetic_marketing_data.csv")
    df.to_csv(output_path, index=False)
    print(f"Dataset saved to: {output_path}")
