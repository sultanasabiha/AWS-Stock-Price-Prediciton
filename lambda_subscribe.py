import json
import boto3

sns_client = boto3.client("sns")

SNS_TOPIC_ARN = "enter_topic_arn_here"

def lambda_handler(event, context):
    try:
        # Parse the incoming request
        email=event['email']
       
        # Subscribe email to SNS topic
        response = sns_client.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol="email",
            Endpoint=email
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Subscription request sent!"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e),"body":event["body"]})
        }
