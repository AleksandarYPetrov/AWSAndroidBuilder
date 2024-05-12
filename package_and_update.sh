#!/bin/bash

# Define the project root path
PROJECT_ROOT="/mnt/c/Users/aleks/Desktop/task"
LAMBDA_FUNCTION_PATH="${PROJECT_ROOT}/lambda_function.py"
VENV_PATH="${PROJECT_ROOT}/lambda-env"
SITE_PACKAGES="${VENV_PATH}/lib/python3.10/site-packages"

# Activate virtual environment
source "${VENV_PATH}/bin/activate"

# Install necessary packages
pip install -r "${PROJECT_ROOT}/requirements.txt"

# Deactivate virtual environment
deactivate

# Package the Lambda function
cd "${SITE_PACKAGES}"
zip -r9 "${PROJECT_ROOT}/lambda_function.zip" .

# Add the Lambda function script to the zip
cd "${PROJECT_ROOT}"
zip -g lambda_function.zip lambda_function.py

# Update Lambda function code
aws lambda update-function-code \
    --function-name HandleAndroidAppBuild \
    --zip-file fileb://lambda_function.zip \
    --profile admin

echo "Lambda function updated successfully."
