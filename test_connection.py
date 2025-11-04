# test_connection.py
import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    st.title("🏨 Supabase Connection Test")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    st.write("### Credentials Check:")
    st.write(f"URL: `{supabase_url}`")
    st.write(f"Key: `{supabase_key[:20]}...`")
    
    try:
        # Initialize Supabase
        supabase = create_client(supabase_url, supabase_key)
        st.success("✅ Supabase client created successfully!")
        
        # Test rooms table
        st.write("### Testing Rooms Table:")
        response = supabase.table('rooms').select('*').execute()
        st.success(f"✅ Found {len(response.data)} rooms")
        st.dataframe(response.data)
        
        # Test vendors table
        st.write("### Testing Vendors Table:")
        response = supabase.table('vendors').select('*').execute()
        st.success(f"✅ Found {len(response.data)} vendors")
        st.dataframe(response.data)
        
        # Test inserting a sample booking (FIXED)
        st.write("### Testing Data Insertion:")
        sample_booking = {
            'room_number': '101',
            'room_type': 'single',
            'check_in': '2024-01-15',
            'check_out': '2024-01-18',
            'num_guests': 2,
            'total_amount': 450.00,
            'status': 'pending',
            'guest_name': 'Test Guest',  # This column now exists
            'special_requests': 'Test booking'
        }
        
        insert_response = supabase.table('bookings').insert(sample_booking).execute()
        if insert_response.data:
            st.success("✅ Sample booking inserted successfully!")
            st.dataframe(insert_response.data)
        
        # Test reading the booking back
        st.write("### Testing Bookings Table:")
        bookings_response = supabase.table('bookings').select('*').execute()
        st.success(f"✅ Found {len(bookings_response.data)} bookings")
        st.dataframe(bookings_response.data)
        
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.info("Make sure you've run the updated SQL schema in Supabase SQL Editor")

if __name__ == "__main__":
    main()