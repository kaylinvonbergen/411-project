from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)




