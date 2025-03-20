import boto3
import numpy as np
import pandas as pd
import json

runtime = boto3.client('runtime.sagemaker')
s3_client = boto3.client("s3")
s3_resource=boto3.client("s3")

#Hard Coding
ENDPOINT_NAME= 'enter_model_endpoint_name_here'
bucket_name="mystockpriceprediction"
filename='latest_data.csv'
prefix = 'built-in-xgboost-algo'
latest_data_path_key='latest_data/latest_data.csv'



def get_resource():
    try:
        data = s3_client.get_object(Bucket=bucket_name, Key=latest_data_path_key)
        latest_data=pd.read_csv(data["Body"])

    except Exception as e:
        print("Error fetching S3 file:", e)

    return latest_data.tail(50)


def get_features(df):
    
    #Helps model detect long-term trends.
    df['SMA_10'] = df['Close'].rolling(window=10).mean()  # 10-day simple moving average
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()  # 50-day Exponential Moving Average
    df['High_Low_Range'] = df['High'] - df['Low']   #Measures daily volatility, which can indicate breakouts or trend reversals.
    df['Open_Close_Change'] = (df['Close'] - df['Open'])/df['Open']  #If the Close > Open, it suggests bullish momentum; otherwise, it's bearish.
    
    # Create lag features 
    df['Close_Lag_1'] = df['Close'].shift(1)    # previous day's closing price
    df['Volume_Lag_1'] = df['Volume'].shift(1)  # Previous day's volume
 
    # Drop NaN values created due to rolling calculations
    df.dropna(inplace=True)
    return df

def lambda_handler(event,context):
    # Parse the incoming request
    inputs = pd.DataFrame(event['data'],columns=['Close','High','Low','Open','Volume'])
    latest=get_resource()
    aug=pd.concat([latest,inputs],axis=0).reset_index(drop=True)
    aug=get_features(aug)
    X_unseen = np.array(aug[['SMA_10' ,'EMA_50','High_Low_Range', 'Open_Close_Change','Volume_Lag_1','Close_Lag_1']].tail(len(inputs)))
    result=[]

    for input in X_unseen:
        serialized_input=','.join(map(str,input))
        response=runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,ContentType='text/csv',Body=serialized_input)
        res=response['Body'].read().decode()
        result.append(round(float(res),2))

    return {
            "statusCode": 200,
            "body": json.dumps({"result": result})
        }

