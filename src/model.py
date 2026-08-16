import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import shap

def train_and_evaluate(data_path="Dataset/synthetic_marketing_data.csv", model_dir="src/models", plots_dir="reports/static"):
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    categorical_features = ['Industry', 'Platform', 'Content_Type', 'Content_Topic', 'Posting_Day', 'Posting_Time']
    numeric_features = ['Ad_Spend']
    target = 'Performance_Score'
    
    X = df[categorical_features + numeric_features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', StandardScaler(), numeric_features)
        ]
    )
    
    baseline_model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', DecisionTreeRegressor(max_depth=6, random_state=42))
    ])
    
    champion_model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1))
    ])
    
    print("Training Baseline model...")
    baseline_model.fit(X_train, y_train)
    y_pred_base = baseline_model.predict(X_test)
    
    mae_base = mean_absolute_error(y_test, y_pred_base)
    rmse_base = np.sqrt(mean_squared_error(y_test, y_pred_base))
    r2_base = r2_score(y_test, y_pred_base)
    print(f"Baseline - MAE: {mae_base:.3f}, RMSE: {rmse_base:.3f}, R2: {r2_base:.3f}")
    
    print("Training Champion model...")
    champion_model.fit(X_train, y_train)
    y_pred_champ = champion_model.predict(X_test)
    
    mae_champ = mean_absolute_error(y_test, y_pred_champ)
    rmse_champ = np.sqrt(mean_squared_error(y_test, y_pred_champ))
    r2_champ = r2_score(y_test, y_pred_champ)
    print(f"Champion - MAE: {mae_champ:.3f}, RMSE: {rmse_champ:.3f}, R2: {r2_champ:.3f}")
    
    best_pipeline = champion_model if r2_champ >= r2_base else baseline_model
    best_name = "Random Forest" if r2_champ >= r2_base else "Decision Tree"
    print(f"Selected Model: {best_name}")
    
    model_path = os.path.join(model_dir, "marketing_intelligence_pipeline.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(best_pipeline, f)
    
    ohe = best_pipeline.named_steps['preprocessor'].named_transformers_['cat']
    encoded_cat_features = list(ohe.get_feature_names_out(categorical_features))
    feature_names = encoded_cat_features + numeric_features
    
    importances = best_pipeline.named_steps['regressor'].feature_importances_
    feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False)
    
    plt.figure(figsize=(10, 8))
    feat_imp.head(15).plot(kind='barh', color='teal')
    plt.title("Top 15 Encoded Feature Importances")
    plt.xlabel("Importance Score")
    plt.ylabel("Encoded Feature")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "feature_importances.png"))
    plt.close()
    
    X_train_transformed = best_pipeline.named_steps['preprocessor'].transform(X_train)
    explainer = shap.TreeExplainer(best_pipeline.named_steps['regressor'])
    
    shap_data = {
        'explainer': explainer,
        'feature_names': feature_names,
        'categorical_features': categorical_features,
        'numeric_features': numeric_features,
        'cat_encoder': ohe
    }
    shap_path = os.path.join(model_dir, "shap_explainer_data.pkl")
    with open(shap_path, 'wb') as f:
        pickle.dump(shap_data, f)
    
    X_test_transformed = best_pipeline.named_steps['preprocessor'].transform(X_test)
    shap_values = explainer(X_test_transformed)
    
    plt.figure()
    shap.summary_plot(shap_values, X_test_transformed, feature_names=feature_names, show=False)
    plt.title("SHAP Feature Impact Summary (Test Set)", fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "shap_summary_plot.png"))
    plt.close()

def get_local_explanation(input_df, model_pipeline_path="src/models/marketing_intelligence_pipeline.pkl", shap_data_path="src/models/shap_explainer_data.pkl"):
    with open(model_pipeline_path, 'rb') as f:
        pipeline = pickle.load(f)
        
    with open(shap_data_path, 'rb') as f:
        sd = pickle.load(f)
        
    explainer = sd['explainer']
    feature_names = sd['feature_names']
    categorical_features = sd['categorical_features']
    numeric_features = sd['numeric_features']
    ohe = sd['cat_encoder']
    
    predicted_score = pipeline.predict(input_df)[0]
    X_transformed = pipeline.named_steps['preprocessor'].transform(input_df)
    
    shap_vals = explainer.shap_values(X_transformed)[0]
    base_val = explainer.expected_value
    if isinstance(base_val, np.ndarray):
        base_val = base_val[0]
        
    mapped_shap = {}
    for num_col in numeric_features:
        idx = feature_names.index(num_col)
        mapped_shap[num_col] = float(shap_vals[idx])
        
    for cat_col in categorical_features:
        prefix = f"{cat_col}_"
        cat_shap_sum = 0.0
        for idx, col_name in enumerate(feature_names):
            if col_name.startswith(prefix):
                cat_shap_sum += shap_vals[idx]
        mapped_shap[cat_col] = float(cat_shap_sum)
        
    sorted_factors = sorted(mapped_shap.items(), key=lambda x: abs(x[1]), reverse=True)
    
    explanation_details = {
        'predicted_score': float(predicted_score),
        'base_value': float(base_val),
        'feature_contributions': mapped_shap,
        'top_factors': [
            {
                'factor': k, 
                'impact': v, 
                'direction': 'positive' if v >= 0 else 'negative',
                'description': f"{'Increased' if v >= 0 else 'Decreased'} score by {abs(v):.2f} points"
            } for k, v in sorted_factors
        ]
    }
    return explanation_details

if __name__ == "__main__":
    train_and_evaluate()
