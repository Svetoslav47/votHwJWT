# Project Setup

This project uses Docker Compose to orchestrate three services: Minio, Keycloak, and the app. Follow the steps below to set up and run the project.

## Prerequisites

- Docker and Docker Compose should be installed on your machine.

## Step 1: Clone the repository

Clone the repository to your local machine:

```bash
git clone <repository-url>
cd <project-directory>
```

## Step 2: Configure environment variables
Create a .env file in the root of the project directory and add the following environment variables:

```
MINIO_ENDPOINT=http://localhost:9001/login
REALM_NAME=testvot
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=admin123
CLIENT_ID=ClientTest
KEYCLOAK_URL=http://localhost:8080/
CLIENT_SECRET=DCtnh4dmAznGhRQ8tVPzkLRcBulgcWwP
```

Step 3: Start the Docker containers
``` bash
docker-compose up -d
```

## Step 4: Configure Keycloak
Open Keycloak in your browser: http://localhost:8080.

Log in with the following credentials:

Username: admin
Password: admin
Once logged in, create the following configurations:

Create a Realm:
Navigate to the "Realms" section.
Click "Add realm".
Name the realm "testvot" (matching the REALM_NAME variable from the .env file).
Create a Client:
Go to the "Clients" section under your newly created realm.
Click "Create" and fill in the following fields:
Client ID: ClientTest (matching the CLIENT_ID variable from the .env file)
Root URL: (Leave blank)
Access Type: confidential
Standard Flow Enabled: ON
Client Authentication: ON
Email: "some random email"
EmailVerified: TRUE
After creating the client, you'll be able to find the Client Secret. Use this to configure your application.
Create a User:
Go to the "Users" section under your realm.
Click "Add User" and create a new user:
Username: admin
Password: admin
Enable the user and set their password.

## Step 5: Get the Bearer Token
Once the services are up and running and the client and user have been created, you can retrieve a bearer token to authenticate your API requests.

Run the following curl command to obtain the token (replace the client secret with you client's secret):
```bash
curl -X POST "http://localhost:8080/realms/testvot/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=ClientTest" \
  -d "client_secret=DCtnh4dmAznGhRQ8tVPzkLRcBulgcWwP" \
  -d "grant_type=password" \
  -d "username=admin" \
  -d "password=admin"
```

## Step 6: Use the api.
Now you can use the api from the app.py app. it has 
1. POST /upload: Качва файл в S3 bucket.
2. GET /download/{file_id}: Сваля файл по идентификатор.
3. PUT /update/{file_id}: Обновява съществуващ файл.
4. DELETE /delete/{file_id}: Изтрива файл по идентификатор.