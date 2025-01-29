from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import requests
from keycloak import KeycloakOpenID
import os


app = Flask(__name__)
CORS(app)

# Keycloak configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM_NAME = os.getenv("REALM_NAME")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                 client_id=CLIENT_ID,
                                 realm_name=REALM_NAME,
                                 client_secret_key=CLIENT_SECRET)

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

s3_client = boto3.client('s3',
                         endpoint_url=MINIO_ENDPOINT,
                         aws_access_key_id=MINIO_ACCESS_KEY,
                         aws_secret_access_key=MINIO_SECRET_KEY)

BUCKET_NAME = "mybucket"


def verify_token(token):
    """Verify JWT token with Keycloak"""
    try:
        return keycloak_openid.introspect(token)
    except Exception as e:
        return None


@app.before_request
def authenticate():
    """Middleware to check authentication"""
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Missing token"}), 401
    token = token.replace("Bearer ", "")
    token_info = verify_token(token)
    if not token_info or not token_info.get("active"):
        return jsonify({"error": "Invalid token"}), 401


@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload file to MinIO"""
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    s3_client.upload_fileobj(file, BUCKET_NAME, file.filename)
    return jsonify({"message": "File uploaded successfully"})


@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download file from MinIO"""
    try:
        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': BUCKET_NAME, 'Key': file_id},
                                               ExpiresIn=3600)
        return jsonify({"url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/update/<file_id>', methods=['PUT'])
def update_file(file_id):
    """Update file in MinIO"""
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    s3_client.upload_fileobj(file, BUCKET_NAME, file_id)
    return jsonify({"message": "File updated successfully"})


@app.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete file from MinIO"""
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_id)
        return jsonify({"message": "File deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
