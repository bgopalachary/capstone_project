import streamlit as st
import pandas as pd
import boto3

# Load secrets
aws_access_key = st.secrets["AWS_ACCESS_KEY_ID"]
aws_secret_key = st.secrets["AWS_SECRET_ACCESS_KEY"]
aws_region = st.secrets.get("AWS_REGION", "us-east-2")  # fallback region

# Create global DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

def get_cost_data():
    table = dynamodb.Table('AWS_Cost_Usage')

    # Scan entire table
    response = table.scan()
    items = response['Items']

    df = pd.DataFrame(items)
    df['cost'] = df['cost'].astype(float)
    return df

# Streamlit layout
st.set_page_config(layout="wide")
st.title("📊 AWS Cost Dashboard (From DynamoDB)")

df = get_cost_data()

st.subheader("📈 Total AWS Daily Cost")
st.line_chart(df.groupby('date')['cost'].sum())

st.subheader("📊 Daily Cost per AWS Service")
pivot_df = df.pivot(index='date', columns='service', values='cost').fillna(0)
st.bar_chart(pivot_df)

st.subheader("📋 Raw Cost Data")
st.dataframe(df.sort_values(by=['date', 'cost'], ascending=[False, False]))
