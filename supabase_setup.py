# supabase_setup.py
import supabase
import streamlit as st
import pandas as pd
from datetime import datetime

class GrandStaySupabase:
    def __init__(self, url, key):
        self.client = supabase.create_client(url, key)
    
    # User Management
    def create_user(self, email, password, role, name):
        try:
            result = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if result.user:
                # Store additional user data in a separate table
                user_data = {
                    "user_id": result.user.id,
                    "email": email,
                    "role": role,
                    "name": name,
                    "created_at": datetime.now().isoformat()
                }
                self.client.table("profiles").insert(user_data).execute()
                return True
            return False
        except Exception as e:
            st.error(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, email, password):
        try:
            result = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return result.user
        except Exception as e:
            return None
    
    # Booking Management
    def create_booking(self, booking_data):
        try:
            result = self.client.table("bookings").insert(booking_data).execute()
            return result.data
        except Exception as e:
            st.error(f"Error creating booking: {e}")
            return None
    
    def get_bookings(self, user_id=None, status=None):
        try:
            query = self.client.table("bookings").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            if status:
                query = query.eq("status", status)
                
            result = query.execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching bookings: {e}")
            return []
    
    # Room Management
    def get_rooms(self, status=None, room_type=None):
        try:
            query = self.client.table("rooms").select("*")
            
            if status:
                query = query.eq("status", status)
            if room_type:
                query = query.eq("room_type", room_type)
                
            result = query.execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching rooms: {e}")
            return []
    
    def update_room_status(self, room_number, new_status):
        try:
            result = self.client.table("rooms").update({
                "status": new_status,
                "updated_at": datetime.now().isoformat()
            }).eq("room_number", room_number).execute()
            return result.data
        except Exception as e:
            st.error(f"Error updating room status: {e}")
            return None
    
    # Task Management
    def create_task(self, task_data):
        try:
            result = self.client.table("tasks").insert(task_data).execute()
            return result.data
        except Exception as e:
            st.error(f"Error creating task: {e}")
            return None
    
    def get_tasks(self, assigned_to=None, status=None):
        try:
            query = self.client.table("tasks").select("*")
            
            if assigned_to:
                query = query.eq("assigned_to", assigned_to)
            if status:
                query = query.eq("status", status)
                
            result = query.execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching tasks: {e}")
            return []
    
    def update_task_status(self, task_id, new_status, notes=None):
        try:
            update_data = {
                "status": new_status,
                "updated_at": datetime.now().isoformat()
            }
            if notes:
                update_data["completion_notes"] = notes
                
            result = self.client.table("tasks").update(update_data).eq("id", task_id).execute()
            return result.data
        except Exception as e:
            st.error(f"Error updating task: {e}")
            return None
    
    # Invoice Management
    def create_invoice(self, invoice_data):
        try:
            result = self.client.table("invoices").insert(invoice_data).execute()
            return result.data
        except Exception as e:
            st.error(f"Error creating invoice: {e}")
            return None
    
    def get_invoices(self, user_id=None, status=None):
        try:
            query = self.client.table("invoices").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            if status:
                query = query.eq("status", status)
                
            result = query.execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching invoices: {e}")
            return []
    
    # Vendor Management
    def register_vendor(self, vendor_data):
        try:
            result = self.client.table("vendors").insert(vendor_data).execute()
            return result.data
        except Exception as e:
            st.error(f"Error registering vendor: {e}")
            return None
    
    def get_vendors(self, status=None):
        try:
            query = self.client.table("vendors").select("*")
            
            if status:
                query = query.eq("approval_status", status)
                
            result = query.execute()
            return result.data
        except Exception as e:
            st.error(f"Error fetching vendors: {e}")
            return []

# Database initialization function
def initialize_database(supabase_client):
    """Initialize the database with sample data"""
    try:
        # Create tables (this would normally be done via Supabase SQL)
        st.info("Initializing Grand Stay Hotel Database...")
        
        # Sample rooms data
        sample_rooms = [
            {"room_number": "101", "room_type": "Single", "status": "vacant", "rate_per_night": 150},
            {"room_number": "102", "room_type": "Double", "status": "vacant", "rate_per_night": 200},
            {"room_number": "103", "room_type": "Suite", "status": "occupied", "rate_per_night": 350},
            {"room_number": "201", "room_type": "Single", "status": "cleaning", "rate_per_night": 150},
            {"room_number": "202", "room_type": "Double", "status": "maintenance", "rate_per_night": 200},
            {"room_number": "203", "room_type": "Deluxe", "status": "vacant", "rate_per_night": 500},
        ]
        
        for room in sample_rooms:
            supabase_client.client.table("rooms").upsert(room).execute()
        
        st.success("Database initialized successfully!")
        
    except Exception as e:
        st.error(f"Error initializing database: {e}")

# Example usage
if __name__ == "__main__":
    # Replace with your Supabase credentials
    SUPABASE_URL = "your_supabase_project_url"
    SUPABASE_KEY = "your_supabase_anon_key"
    
    # Initialize Supabase client
    db = GrandStaySupabase(SUPABASE_URL, SUPABASE_KEY)
    
    # Initialize database with sample data
    initialize_database(db)