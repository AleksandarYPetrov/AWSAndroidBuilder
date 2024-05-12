
# DevOps Challenge: Android Build Automation

## Project Overview
This project automates the build process for Android applications using AWS services. It integrates several AWS services to set up a robust DevOps environment that compiles Android applications, checks compilation success, and reports the status to a remote webhook.

## Architecture
The solution utilizes the following AWS services:
- **Amazon S3**: For storing Android application ZIP files.
- **AWS Lambda**: To handle events triggered by new files uploaded to S3 and to manage the build process.
- **AWS CodeBuild**: For compiling the Android applications.
- **Amazon API Gateway**: Provides a REST API endpoint to trigger builds manually.
- **AWS IAM**: Manages permissions for AWS services interacting with each other.
- **Amazon CloudWatch**: Logs the process for monitoring and troubleshooting.

## Files Description
- `Simple-Calculator.zip`: Sample Android application source code in ZIP format.
- `lambda_function.py`: The Python script that AWS Lambda executes. It handles file processing, initiates the build in AWS CodeBuild, and communicates with the webhook.
- `lambda_function.zip`: The deployment package for the AWS Lambda function.
- `requirements.txt`: Lists the Python packages that the Lambda function depends on.
- `package_and_update.sh`: Bash script to package the Lambda function and update it on AWS.
- `lambda_package/`: Directory containing additional dependencies and scripts used in the deployment process.

## Packaging and Updating Lambda Function
Use the `package_and_update.sh` script to package and update the Lambda function. This script performs the following actions:
- Activates the virtual environment.
- Installs necessary dependencies listed in `requirements.txt`.
- Packages the Lambda function and its dependencies into a zip file.
- Updates the Lambda function on AWS with the new package.

## Setup Instructions
1. **Prepare AWS Environment**:
    - Create an S3 bucket for storing Android app builds.
    - Set up the necessary IAM roles and policies for Lambda and CodeBuild to access S3 and other resources.
    - Deploy the Lambda function using the provided script and Lambda deployment package.

2. **Deploy API Gateway**:
    - Set up an API Gateway to trigger the Lambda function via HTTP requests.

3. **Configure Webhook**:
    - Set up a webhook on `https://webhook.site` to receive build notifications.

4. **Running the build**:
    - Upload an Android ZIP file to the designated S3 bucket.
    - Alternatively, trigger a build manually using the API Gateway endpoint.

## Usage
### Generating a Pre-signed URL for Uploads
To generate a pre-signed URL for uploading files, make a POST request to the API Gateway endpoint. Specify the desired filename in the JSON payload:


curl -X POST 'https://ss1a8ro038.execute-api.eu-west-1.amazonaws.com/prod/build' \
-H 'Content-Type: application/json' \
-d '{"filename": "test.zip"}'


This command returns a pre-signed URL:


{"upload_url": "https://android-app-builds-aypetrov.s3.amazonaws.com/uploads/test.zip?AWSAccessKeyId=ASIAZI2LCRGH7K3Y4FSO&Signature=lV%2BUDxqk4fkSyfNaCx57khOtZxs%3D&x-amz-security-token=...&Expires=1715515482"}


### Uploading a File Using the Pre-signed URL
To upload a file using the obtained pre-signed URL:


curl -X PUT -T "/mnt/c/Users/aleks/Desktop/task/test.zip" "https://android-app-builds-aypetrov.s3.amazonaws.com/uploads/test.zip?AWSAccessKeyId=ASIAZI2LCRGH7K3Y4FSO&Signature=lV%2BUDxqk4fkSyfNaCx57khOtZxs%3D&x-amz-security-token=...&Expires=1715515482"


## Scalability and Best Practices
- **Auto-Scaling**: AWS Lambda and AWS CodeBuild inherently support scaling. Lambda can handle increasing invocation rates and CodeBuild can manage multiple builds simultaneously.
- **Decoupling**: Using S3 as a trigger for Lambda decouples storage from processing, allowing for independent scaling and management of each service.
- **Security and Compliance**: Using AWS IAM, strict permissions ensure that only necessary operations are allowed, adhering to the principle of least privilege.
- **Monitoring and Logging**: Integration with CloudWatch offers real-time monitoring of logs, which is crucial for diagnosing issues and ensuring the reliability of the build pipeline.

## Monitoring and Logs
Check the AWS CloudWatch logs for detailed information on the Lambda function's execution and any issues during the build process.

