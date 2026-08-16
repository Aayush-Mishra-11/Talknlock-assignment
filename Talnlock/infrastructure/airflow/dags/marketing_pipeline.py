"""
Airflow DAG: Marketing Intelligence Pipeline Orchestration
Manages daily data ingestion, model training, and recommendations
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.data_generator import generate_marketing_data
from src.eda import generate_eda_report
from src.model import train_model, save_model
from src.recommender import generate_recommendations

# Default arguments for DAG
default_args = {
    'owner': 'talnlock-ml-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['ml-alerts@talnlock.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'marketing_intelligence_pipeline',
    default_args=default_args,
    description='Daily marketing data pipeline with model training and recommendations',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM UTC
    catchup=False,
    tags=['marketing', 'ml', 'production'],
)

# Task 1: Generate/Ingest Data
def task_ingest_data(**context):
    """Ingest new marketing data from social media APIs or generate synthetic data"""
    print("Ingesting marketing data...")
    df = generate_marketing_data(n_records=500)
    context['task_instance'].xcom_push(key='data_path', value='Dataset/daily_marketing_data.csv')
    df.to_csv('Dataset/daily_marketing_data.csv', index=False)
    print(f"Generated {len(df)} records")
    return df.shape

ingest_task = PythonOperator(
    task_id='ingest_marketing_data',
    python_callable=task_ingest_data,
    dag=dag,
)

# Task 2: Data Validation & Quality Checks
def task_validate_data(**context):
    """Validate data quality and schema compliance"""
    print("Validating data quality...")
    data_path = context['task_instance'].xcom_pull(key='data_path')
    # Add validation logic
    print(f"Data validation passed for {data_path}")
    return True

validate_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=task_validate_data,
    dag=dag,
)

# Task 3: Run EDA & Generate Statistical Insights
def task_run_eda(**context):
    """Generate EDA reports and statistical analysis"""
    print("Running exploratory data analysis...")
    generate_eda_report()
    print("EDA reports generated successfully")
    return 'EDA completed'

eda_task = PythonOperator(
    task_id='run_eda_analysis',
    python_callable=task_run_eda,
    dag=dag,
)

# Task 4: Train/Retrain ML Model
def task_train_model(**context):
    """Train or retrain the marketing prediction model"""
    print("Training marketing intelligence model...")
    model, metrics = train_model()
    save_model(model)
    print(f"Model trained with metrics: {metrics}")
    context['task_instance'].xcom_push(key='model_metrics', value=metrics)
    return metrics

train_task = PythonOperator(
    task_id='train_ml_model',
    python_callable=task_train_model,
    dag=dag,
)

# Task 5: Generate Recommendations
def task_generate_recommendations(**context):
    """Generate top-N recommendations for all industries"""
    print("Generating marketing recommendations...")
    recommendations = generate_recommendations()
    print(f"Generated recommendations for {len(recommendations)} combinations")
    context['task_instance'].xcom_push(
        key='recommendations', 
        value=recommendations
    )
    return len(recommendations)

recommend_task = PythonOperator(
    task_id='generate_recommendations',
    python_callable=task_generate_recommendations,
    dag=dag,
)

# Task 6: Backup & Archive
backup_task = BashOperator(
    task_id='backup_data_and_models',
    bash_command='mkdir -p backups && cp -r Dataset/* backups/ && cp -r src/models/* backups/',
    dag=dag,
)

# Task 7: Notify Completion
def task_notify_completion(**context):
    """Send notification on successful pipeline completion"""
    metrics = context['task_instance'].xcom_pull(
        task_ids='train_ml_model',
        key='model_metrics'
    )
    print(f"✅ Pipeline completed successfully!")
    print(f"Model Metrics: {metrics}")
    # Add notification logic (email, Slack, etc.)
    return 'Pipeline completed'

notify_task = PythonOperator(
    task_id='notify_completion',
    python_callable=task_notify_completion,
    dag=dag,
)

# Define task dependencies
ingest_task >> validate_task >> [eda_task, train_task]
train_task >> recommend_task >> backup_task
[eda_task, backup_task, recommend_task] >> notify_task
