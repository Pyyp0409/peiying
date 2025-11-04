# test_setup.py
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def test_environment():
    st.title("Environment Setup Test")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    st.write("### Environment Variables Check:")
    st.write(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
    st.write(f"SUPABASE_KEY: {'✅ Set' if supabase_key else '❌ Missing'}")
    
    if supabase_url and supabase_key:
        st.success("Environment variables loaded successfully!")
        st.info("You can now run the main application.")
    else:
        st.error("Please check your .env file configuration.")

if __name__ == "__main__":
    test_environment()