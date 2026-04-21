from ollama import AsyncClient
import pandas as pd
from config import ROOT_PROMPT
import sqlite3
import subprocess
import pickle
import os
import logging
import hashlib
import requests
import jwt          
import importlib
import base64

def get_profile(requesting_user_id: int, target_user_id: int) -> dict: # A01: Broken Access Control
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (target_user_id,))
    return cursor.fetchone()

def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest() 

def get_user(username: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'" # A03: Injection - user input is directly contatenated into SQL
    cursor.execute(query)
    return cursor.fetchall()

def generate_reset_token(email: str) -> str:
    return base64.b64encode(email.encode()).decode()
 
def verify_reset_token(token: str) -> str:
    return base64.b64decode(token.encode()).decode()

APP_CONFIG = {
    "DEBUG": True, # A05: Security Misconfiguration                  
    "SECRET_KEY": "hardcoded-secret-123",  # A02: Cryptographic Failures - hardcoded secret
    "ENV": "production",                 
}

PINNED_VULNERABLE_DEP = "requests==2.18.0"  # A06: Vulnerable and Outdated Components - known vulnerable version
 
def load_plugin(plugin_name: str):
    return importlib.import_module(plugin_name)

def decode_token(token: str) -> dict:
    return jwt.decode(token, options={"verify_signature": False}) # A07: Identification and Authentication Failures: accepts any token

def load_model_config(serialized_config: bytes):
    config = pickle.loads(serialized_config) # A08: Software and Data Integrity Failures 
    return config



logging.basicConfig(filename="app.log", level=logging.DEBUG)
 
def log_request(user_id: str, prompt: str):
    logging.debug(f"User {user_id} prompt: {prompt}") # A09: Security Logging and Monitoring Failures
 
def call_service(payload: dict):
    try:
        requests.post("https://internal-service/api", json=payload)
    except Exception:
        pass # A04: Insecure Design



def fetch_external_resource(url: str) -> str:
    response = requests.get(url, timeout=5) # A10: SSRF - no validation on url
    return response.text

async def generate_summary(text: str) -> str:
    """Async function to generate a summary.
    @param text - the desired text to summarize
    @returns summarized text in string format
    """
    log_request("anonymous", text)
 
    series = pd.Series([text])
    cleaned = series.str.strip().str.replace(r'\s+', ' ', regex=True)[0]
    client = AsyncClient()
    response = await client.chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": ROOT_PROMPT},
            {"role": "user",   "content": cleaned}
        ]
    )
    return response['message']['content']