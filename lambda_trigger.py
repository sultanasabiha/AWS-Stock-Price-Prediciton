import boto3
import json
import pandas as pd
import yfinance as yf

sns_client = boto3.client("sns")
lambda_client = boto3.client("lambda")

SNS_TOPIC_ARN = "enter_topic_arn_here"
CONTENT_GENERATOR_LAMBDA_ARN = "enter_endpoint_lambda_arn_here"

start_date = "2024-01-05"
duration=1
real_time_data = yf.download('AAPL', start=start_date, end=pd.Timestamp(start_date)+pd.Timedelta(days=duration))
real_time_data.columns = real_time_data.columns.droplevel(1)
real_time_data=real_time_data.reset_index(drop=True)
input_data={"data":real_time_data.values.tolist()}


def lambda_handler(event, context):
    # Invoke Content Generator Lambda with input
    response = lambda_client.invoke(
              FunctionName=CONTENT_GENERATOR_LAMBDA_ARN,
              InvocationType="RequestResponse",
              Payload=json.dumps(input_data)  # Send inputs
              )
    responsePayload=json.load(response['Payload'])
    body_data=responsePayload['body']
    body=json.loads(body_data)

    # Publish to SNS
    sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message='Prediction is $'+','.join([str(n) for n in body['result']]),
            Subject="Stock Price Prediction Alert"
            )
            
    return {
            "statusCode": 200,
            "message": "Notification sent successfully!"
            }

