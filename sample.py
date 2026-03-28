import boto3
import json

print("Hi")
client = boto3.client('bedrock-runtime', region_name='us-east-1')
model_id = 'amazon.titan-embed-text-v2:0'
text = 'Your input text here'
body = json.dumps({'inputText': text, 'dimensions': 1024, 'normalize': True})
response = client.invoke_model(modelId=model_id, body=body, accept='application/json', contentType='application/json')
embedding = json.loads(response['body'].read())['embedding']
print(embedding[:10])  # First 10 dims
