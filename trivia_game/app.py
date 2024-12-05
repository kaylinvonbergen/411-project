from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256
from flask import Flask, jsonify, make_response, Response, request
import sqlite3

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)







