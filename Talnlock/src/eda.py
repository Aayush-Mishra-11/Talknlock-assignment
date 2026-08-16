import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16,
    'figure.figsize': (10, 6)
})

def run_eda(data_path="Dataset/synthetic_marketing_data.csv", output_dir="reports/static"):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(data_path)
    
    print("Dataset Records:", len(df))
    print(df['Performance_Score'].describe())
    
    plt.figure()
    sns.histplot(df['Performance_Score'], kde=True, color="royalblue")
    plt.title("Distribution of Content Performance Score")
    plt.xlabel("Performance Score (0 - 100)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "performance_score_dist.png"))
    plt.close()
    
    platform_perf = df.groupby('Platform')['Performance_Score'].mean().sort_values(ascending=False)
    plt.figure()
    sns.barplot(x=platform_perf.index, y=platform_perf.values, hue=platform_perf.index, palette="Blues_r", legend=False)
    plt.title("Average Performance Score by Platform")
    plt.ylabel("Average Score")
    plt.xlabel("Platform")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "perf_by_platform.png"))
    plt.close()
    
    type_perf = df.groupby('Content_Type')['Performance_Score'].mean().sort_values(ascending=False)
    topic_perf = df.groupby('Content_Topic')['Performance_Score'].mean().sort_values(ascending=False)
    
    plt.figure()
    sns.barplot(x=topic_perf.values, y=topic_perf.index, hue=topic_perf.index, palette="viridis", legend=False)
    plt.title("Average Performance Score by Content Topic")
    plt.xlabel("Average Score")
    plt.ylabel("Content Topic")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "perf_by_topic.png"))
    plt.close()

    numerical_cols = ['Ad_Spend', 'Impressions', 'Reach', 'Likes', 'Comments', 
                      'Shares', 'Saves', 'Clicks', 'Leads', 'Revenue', 
                      'Video_Views', 'Watch_Time_Sec', 'Performance_Score']
    corr_matrix = df[numerical_cols].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation Matrix of Marketing Metrics")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "correlation_matrix.png"))
    plt.close()
    
    platforms_groups = [df[df['Platform'] == p]['Performance_Score'] for p in df['Platform'].unique()]
    f_stat_p, p_val_p = stats.f_oneway(*platforms_groups)
    print(f"Platform ANOVA: F-stat = {f_stat_p:.3f}, p-val = {p_val_p:.3e}")
        
    industries_groups = [df[df['Industry'] == ind]['Performance_Score'] for ind in df['Industry'].unique()]
    f_stat_i, p_val_i = stats.f_oneway(*industries_groups)
    print(f"Industry ANOVA: F-stat = {f_stat_i:.3f}, p-val = {p_val_i:.3e}")
        
    plt.figure(figsize=(12, 7))
    sns.pointplot(data=df, x="Platform", y="Performance_Score", hue="Industry", 
                  dodge=0.3, errorbar=None)
    plt.title("Platform vs Industry Interaction on Performance Score")
    plt.ylabel("Average Performance Score")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "platform_industry_interaction.png"))
    plt.close()
    
    viral_organic = df[(df['Ad_Spend'] == 0) & (df['Impressions'] > 20000)]
    ad_waste = df[(df['Ad_Spend'] > 300) & (df['Performance_Score'] < 10)]
        
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="Ad_Spend", y="Performance_Score", alpha=0.5, color="gray", label="Standard Posts")
    if not viral_organic.empty:
        sns.scatterplot(data=viral_organic, x="Ad_Spend", y="Performance_Score", color="green", s=100, label="Viral Organic Posts", marker="^")
    if not ad_waste.empty:
        sns.scatterplot(data=ad_waste, x="Ad_Spend", y="Performance_Score", color="red", s=100, label="High Ad Spend Waste", marker="v")
        
    plt.title("Ad Spend vs. Performance Score (Anomalies)")
    plt.xlabel("Ad Spend ($)")
    plt.ylabel("Performance Score")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "spend_vs_performance_anomalies.png"))
    plt.close()
    
    print("EDA completed. Plots saved to:", output_dir)

if __name__ == "__main__":
    run_eda()
