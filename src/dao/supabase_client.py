# src/dao/supabase_client.py
import os
import sys
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load .env from project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
env_path = os.path.join(project_root, '.env')

print(f"🔍 Looking for .env at: {env_path}")

if os.path.exists(env_path):
    load_dotenv(env_path)
    print("✅ .env file loaded successfully")
else:
    print("❌ .env file not found at expected location")
    # Try loading from current directory as fallback
    load_dotenv()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

print(f"🔍 Supabase URL: {SUPABASE_URL}")
print(f"🔍 Supabase Key: {'*' * 20 if SUPABASE_KEY else 'NOT FOUND'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ SUPABASE_URL and SUPABASE_KEY must be set in .env file")

try:
    client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Supabase client: {e}")
    client = None