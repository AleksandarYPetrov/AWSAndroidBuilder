import json
import boto3
import zipfile
import tempfile
import requests

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    
    s3_client = boto3.client('s3')
    codebuild = boto3.client('codebuild')
    webhook_url = 'https://webhook.site/bae7f351-2546-43f5-b75b-da984e05221d'
    
    # Check if the event comes from API Gateway and adjust the structure
    if 'httpMethod' in event:
        # Assuming body is a stringified JSON for simplicity, parse it:
        body = json.loads(event.get('body', '{}'))
        bucket = body.get('bucket')
        key = body.get('key')
    else:
        # Process normally for S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

    try:
        # Download the zip file from S3
        with tempfile.TemporaryFile() as tmp_file:
            s3_client.download_fileobj(bucket, key, tmp_file)
            tmp_file.seek(0)

            # Extract the zip file
            with zipfile.ZipFile(tmp_file, 'r') as zip_ref:
                zip_ref.extractall('/tmp/extracted')

        # Start the build process in AWS CodeBuild
        response = codebuild.start_build(
            projectName='AndroidAppBuildProject',
            sourceVersion='master',
            artifactsOverride={'type': 'NO_ARTIFACTS'},
            environmentVariablesOverride=[
                {'name': 'PACKAGE_PATH', 'value': '/tmp/extracted', 'type': 'PLAINTEXT'}
            ]
        )

        build_id = response['build']['id']
        print(f"Started build with ID: {build_id}")

        # Send build start notification to webhook.site
        webhook_data = {
            'message': 'Build started',
            'build_id': build_id
        }
        requests.post(webhook_url, json=webhook_data)

        return {
            'statusCode': 200,
            'body': json.dumps(f'Build started successfully with ID {build_id}')
        }

    except Exception as e:
        # Send error notification to webhook.site
        error_data = {
            'error': str(e),
            'build_id': 'None',
            'message': 'Build failed to start'
        }
        requests.post(webhook_url, json=error_data)
        print(e)
        raise e
