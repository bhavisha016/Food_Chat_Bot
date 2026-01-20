# Food_Chat_Bot
The Food Ordering and Tracking Chatbot is a conversational application designed to help users place food orders and track their order status using natural language. The chatbot uses Dialogflow to understand user queries such as placing a new order or tracking an existing order.

Directory structure
===================
backend: Contains Python FastAPI backend code
db: contains the dump of the database. you need to import this into your MySQL db by using MySQL workbench tool
frontend: website code

Install these modules
======================

pip install mysql-connector
pip install "fastapi[all]"

OR just run pip install -r backend/requirements.txt to install both in one shot

To start fastapi backend server
================================
1. Go to backend directory in your command prompt
2. Run this command: uvicorn main:app --reload

ngrok for https tunneling
================================
1. To install ngrok, go to https://ngrok.com/download and install ngrok version that is suitable for your OS
2. Extract the zip file and place ngrok.exe in a folder.
3. Open windows command prompt, go to that folder and run this command: ngrok http 80000

**TRY IT OUT**
https://lambent-cassata-701efb.netlify.app/

