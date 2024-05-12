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

    # Handling POST request for generating pre-signed URLs
    if 'httpMethod' in event and event['httpMethod'] == 'POST':
        try:
            # Attempt to parse the JSON body and extract a filename
            body = json.loads(event.get('body', '{}'))
            filename = body.get('filename', 'default.zip')  # Provide a default filename
            key = f'uploads/{filename}'  # Construct the key with the provided filename

            # Generate the pre-signed URL for uploading directly to S3
            response = s3_client.generate_presigned_url('put_object',
                                                        Params={'Bucket': 'android-app-builds-aypetrov', 'Key': key},
                                                        ExpiresIn=3600,  # URL expires in 1 hour
                                                        HttpMethod='PUT')

            return {
                'statusCode': 200,
                'body': json.dumps({'upload_url': response})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }

    # Handling S3 bucket notification for build triggering
    elif 'Records' in event:  # This block handles S3 event notifications
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        try:
            # Download the zip file from S3 to a temporary file
            with tempfile.TemporaryFile() as tmp_file:
                s3_client.download_fileobj(bucket, key, tmp_file)
                tmp_file.seek(0)

                # Extract the zip file to a temporary directory
                with zipfile.ZipFile(tmp_file, 'r') as zip_ref:
                    zip_ref.extractall('/tmp/extracted')

            # Start the AWS CodeBuild project
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

            # Notify via webhook
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
            error_data = {
                'error': str(e),
                'build_id': 'None',
                'message': 'Build failed to start'
            }
            requests.post(webhook_url, json=error_data)
            print(e)
            raise e
