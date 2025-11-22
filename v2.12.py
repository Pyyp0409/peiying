# app.py
import streamlit as st
import supabase
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import json
from io import BytesIO
import requests


def enforce_auto_cancels():
    now = datetime.now()
    for inv in st.session_state.invoices:
        if inv["status"] == "Pending":
            due = datetime.strptime(inv["due_date"], "%Y-%m-%d %H:%M:%S")
            if now > due:
                booking = next((b for b in st.session_state.bookings if b["id"] == inv["booking_id"]), None)
                if booking:
                    booking["status"] = "Cancelled"
                    booking["cancellation_status"] = "Auto-cancelled"
                    
                    # Log cancellation request
                    st.session_state.cancellation_requests.append({
                        "booking_id": booking["id"],
                        "guest": booking["guest"],
                        "guest_email": booking["guest_email"],
                        "amount": booking["amount"],
                        "amount_paid": booking.get("amount_paid", 0),
                        "status": "Processed",
                        "request_date": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "refund_amount": 0,
                        "processing_fee": 0
                    })

                inv["status"] = "Cancelled"
                add_notification(
                    f"Booking {inv['booking_id']} auto-cancelled due to unpaid invoice",
                    "cancellation",
                    ["Hotel Manager", "Billing Officer"]
                )

# Page configuration
st.set_page_config(
    page_title="Grand Stay Hotel Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with classic neutral color scheme
st.markdown("""
<style>
    :root {
        --dark-green: #283618;
        --light-gray-green: #B7B7A4;
        --soft-gray: #D4D4D4;
        --off-white: #F0EFEB;
        --accent: #A5A58D;
    }
    
    .stApp {
        background-color: var(--off-white);
    }
    
    .main .block-container {
        padding-top: 2rem;
        background-color: var(--off-white);
    }
    
    .main-header {
        font-size: 3.5rem;
        color: var(--dark-green);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
        font-family: 'Playfair Display', serif;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(145deg, var(--off-white), var(--soft-gray));
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 2px solid var(--light-gray-green);
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: var(--dark-green);
        margin-bottom: 1.5rem;
        font-weight: 500;
        border-bottom: 3px solid var(--accent);
        padding-bottom: 0.8rem;
        font-family: 'Montserrat', sans-serif;
    }
    
    .card {
        background: white;
        color: var(--dark-green);
        padding: 1.8rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border-left: 5px solid var(--accent);
        border: 1px solid var(--soft-gray);
    }
    
    .success-card {
        border-left: 5px solid #27AE60;
        background: white;
        color: var(--dark-green);
    }
    
    .warning-card {
        border-left: 5px solid #F39C12;
        background: white;
        color: var(--dark-green);
    }
    
    .critical-card {
        border-left: 5px solid #E74C3C;
        background: white;
        color: var(--dark-green);
    }
    
    .login-container {
        background: white;
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 2px solid var(--light-gray-green);
        margin-bottom: 2rem;
    }
    
    .demo-account {
        background: linear-gradient(135deg, var(--light-gray-green) 0%, var(--accent) 100%);
        color: var(--dark-green);
        padding: 1.2rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        border: 1px solid var(--soft-gray);
    }
    
    .notification-badge {
        background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%);
        color: white;
        border-radius: 50%;
        width: 25px;
        height: 25px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, var(--dark-green) 0%, var(--accent) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stButton button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--dark-green) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, var(--dark-green) 0%, var(--accent) 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .elegant-cover {
        background: linear-gradient(135deg, var(--dark-green) 0%, var(--accent) 100%);
        padding: 4rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .elegant-title {
        font-size: 4rem;
        font-weight: 300;
        font-family: 'Playfair Display', serif;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .elegant-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        opacity: 0.9;
        font-family: 'Montserrat', sans-serif;
    }
    
    .room-status-occupied {
        background-color: #E74C3C;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 8px; 
        text-align: center;
    }
    
    .room-status-vacant {
        background-color: #27AE60;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 8px; 
        text-align: center;
    }
    
    .room-status-pending {
        background-color: #00A8FF;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 8px;
        text-align: center;
    }
    
    .room-status-cleaning {
        background-color: #F39C12;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 8px;
        text-align: center;
    }
    
    .room-status-maintenance {
        background-color: #95A5A6;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 8px;
        text-align: center;
    }
    
    .registration-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 2px solid var(--light-gray-green);
        margin: 2rem auto;
        max-width: 800px;
    }
    </style>
""", unsafe_allow_html=True)

# Supabase configuration
SUPABASE_URL = "https://qgzirsnzykluunthmiog.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFnemlyc256eWtsdXVudGhtaW9nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIxMDIxMzUsImV4cCI6MjA3NzY3ODEzNX0.VmPPTYrvSK-L9WdpZ9qGXFp-ZzxfiYBnFqiMJroW9jI"

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    try:
        client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        st.error(f"Supabase connection error: {e}")
        return None

# Enhanced demo accounts with new roles
DEMO_ACCOUNTS = {
    "Guest": [
        {"email": "guest1@demo.com", "password": "guest123", "name": "John Traveler"},
        {"email": "guest2@demo.com", "password": "guest123", "name": "Sarah Visitor"}
    ],
    "Front Desk Officer": [
        {"email": "frontdesk@demo.com", "password": "frontdesk123", "name": "Emily Frontdesk"}
    ],
    "Housekeeping Staff": [
        {"email": "housekeeping@demo.com", "password": "house123", "name": "Maria Cleaner"}
    ],
    "Maintenance Staff": [
        {"email": "maintenance@demo.com", "password": "maintain123", "name": "Mike Technician"}
    ],
    "Hotel Manager": [
        {"email": "manager@demo.com", "password": "manager123", "name": "David Manager"}
    ],
    "Billing Officer": [
        {"email": "billing@demo.com", "password": "billing123", "name": "Lisa Accountant"}
    ],
    "Vendor": [
        {"email": "vendor@demo.com", "password": "vendor123", "name": "Tom Suppliers"}
    ],
    "Catering Staff": [
        {"email": "catering@demo.com", "password": "catering123", "name": "Sarah Catering"}
    ],
    "Event & Concierge Staff": [
        {"email": "events@demo.com", "password": "events123", "name": "Emma Events"}
    ]
}

# Initialize session data
def init_session_data():
    # Initialize all session state variables
    defaults = {
        'authenticated': False,
        'current_user': None,
        'current_role': None,
        'modification_requests': [],
        'supabase': init_supabase(),
        'system_logs':[],
        'last_activity': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'bookings': [
            # Sample bookings with real data - UPDATED TO 2025
            {"id": "BK001", "guest": "John Traveler", "guest_email": "guest1@demo.com", "room_type": "Deluxe", 
             "check_in": "2025-10-15", "check_out": "2025-10-18", "status": "Completed", "payment_status": "Paid", 
             "amount": 1500, "amount_paid": 1500, "room_number": "301", "timestamp": "2025-10-15 14:30:00"},
            {"id": "BK002", "guest": "Sarah Visitor", "guest_email": "guest2@demo.com", "room_type": "Suite", 
             "check_in": "2025-10-25", "check_out": "2025-10-30", "status": "Completed", "payment_status": "Paid", 
             "amount": 1750, "amount_paid": 1750, "room_number": "203", "timestamp": "2025-10-25 15:45:00"},
            {"id": "BK003", "guest": "Mike Brown", "guest_email": "mike@example.com", "room_type": "Double", 
             "check_in": "2025-11-05", "check_out": "2025-11-10", "status": "Confirmed", "payment_status": "Paid", 
             "amount": 1000, "amount_paid": 1000, "room_number": "102", "timestamp": "2025-11-05 12:15:00"},
            {"id": "BK004", "guest": "Emma Wilson", "guest_email": "emma@example.com", "room_type": "Single", 
             "check_in": "2025-11-20", "check_out": "2025-11-25", "status": "Confirmed", "payment_status": "Pending", 
             "amount": 750, "amount_paid": 0, "room_number": "401", "timestamp": "2025-11-20 10:00:00"},
        ],
        'rooms': [
            {"number": "101", "type": "Single", "status": "occupied", "guest": "John Smith", "price": 150},
            {"number": "102", "type": "Double", "status": "occupied", "guest": "Mike Brown", "price": 200},
            {"number": "103", "type": "Suite", "status": "cleaning", "guest": "", "price": 350},
            {"number": "201", "type": "Single", "status": "occupied", "guest": "Sarah Johnson", "price": 150},
            {"number": "202", "type": "Double", "status": "maintenance", "guest": "", "price": 200},
            {"number": "203", "type": "Suite", "status": "vacant", "guest": "", "price": 350},
            {"number": "301", "type": "Deluxe", "status": "vacant", "guest": "", "price": 500},
            {"number": "302", "type": "Deluxe", "status": "vacant", "guest": "", "price": 500},
            {"number": "401", "type": "Single", "status": "vacant", "guest": "", "price": 150},
            {"number": "402", "type": "Single", "status": "vacant", "guest": "", "price": 150},
            {"number": "501", "type": "Double", "status": "occupied", "guest": "Robert Wilson", "price": 200},
            {"number": "502", "type": "Double", "status": "vacant", "guest": "", "price": 200},
            {"number": "601", "type": "Suite", "status": "vacant", "guest": "", "price": 350},
            {"number": "602", "type": "Suite", "status": "maintenance", "guest": "", "price": 350},
            {"number": "701", "type": "Deluxe", "status": "vacant", "guest": "", "price": 500},
            {"number": "702", "type": "Deluxe", "status": "occupied", "guest": "Lisa Davis", "price": 500},
            {"number": "801", "type": "Single", "status": "cleaning", "guest": "", "price": 150},
            {"number": "802", "type": "Double", "status": "vacant", "guest": "", "price": 200},
            {"number": "901", "type": "Suite", "status": "vacant", "guest": "", "price": 350},
            {"number": "902", "type": "Deluxe", "status": "occupied", "guest": "James Anderson", "price": 500}
        ],
        'service_requests': [],
        'invoices': [
            # UPDATED TO 2025
            {"id": "INV001", "booking_id": "BK001", "guest": "John Traveler", "amount": 1500, "status": "Paid", 
             "payment_method": "Credit Card", "due_date": "2025-10-15 16:30:00"},
            {"id": "INV002", "booking_id": "BK002", "guest": "Sarah Visitor", "amount": 1750, "status": "Paid", 
             "payment_method": "Online Banking", "due_date": "2025-10-25 17:45:00"},
            {"id": "INV003", "booking_id": "BK003", "guest": "Mike Brown", "amount": 1000, "status": "Paid", 
             "payment_method": "Debit Card", "due_date": "2025-11-05 14:15:00"},
            {"id": "INV004", "booking_id": "BK004", "guest": "Emma Wilson", "amount": 750, "status": "Pending", 
             "payment_method": "Credit Card", "due_date": "2025-11-20 12:00:00"},
        ],
        'notifications': [],
        'staff_applications': [],
        'vendor_applications': [],
        'guest_applications': [],
        'registered_users': [
            # UPDATED REGISTRATION DATES TO 2025
            {"email": "guest1@demo.com", "name": "John Traveler", "role": "Guest", "status": "Active", "registration_date": "2025-01-15", "password": "guest123"},
            {"email": "guest2@demo.com", "name": "Sarah Visitor", "role": "Guest", "status": "Active", "registration_date": "2025-01-20", "password": "guest123"},
            {"email": "frontdesk@demo.com", "name": "Emily Frontdesk", "role": "Front Desk Officer", "status": "Active", "registration_date": "2025-01-01", "password": "frontdesk123"},
            {"email": "housekeeping@demo.com", "name": "Maria Cleaner", "role": "Housekeeping Staff", "status": "Active", "registration_date": "2025-01-01", "password": "house123"},
            {"email": "maintenance@demo.com", "name": "Mike Technician", "role": "Maintenance Staff", "status": "Active", "registration_date": "2025-01-01", "password": "maintain123"},
            {"email": "manager@demo.com", "name": "David Manager", "role": "Hotel Manager", "status": "Active", "registration_date": "2025-01-01", "password": "manager123"},
            {"email": "billing@demo.com", "name": "Lisa Accountant", "role": "Billing Officer", "status": "Active", "registration_date": "2025-01-01", "password": "billing123"},
            {"email": "vendor@demo.com", "name": "Tom Suppliers", "role": "Vendor", "status": "Approved", "registration_date": "2025-01-01", "password": "vendor123"},
            {"email": "catering@demo.com", "name": "Sarah Catering", "role": "Catering Staff", "status": "Active", "registration_date": "2025-01-01", "password": "catering123"},
            {"email": "events@demo.com", "name": "Emma Events", "role": "Event & Concierge Staff", "status": "Active", "registration_date": "2025-01-01", "password": "events123"},
        ],
        'reviews': [
            # UPDATED TO 2025
            {"guest": "John Traveler", "room": "301", "ratings": {"overall": 5, "cleanliness": 5, "service": 4, "comfort": 5}, "comments": "Excellent stay! The room was spacious and clean.", "timestamp": "2025-10-18 10:30:00"},
            {"guest": "Sarah Visitor", "room": "203", "ratings": {"overall": 4, "cleanliness": 4, "service": 5, "comfort": 4}, "comments": "Great service and comfortable beds. Will come back!", "timestamp": "2025-10-30 14:45:00"},
        ],
        'tasks': [],
        'vendors': [
            # UPDATED REGISTRATION DATES TO 2025
            {"name": "ABC Laundry", "service": "Laundry", "status": "Approved", "contact": "vendor@demo.com", 
             "registration_date": "2025-01-01", "service_fee": 5.0, "monthly_earnings": 2850, "services_completed": 38,
             "contact_person": "Tom Suppliers", "phone": "+1-555-0123", "description": "Professional laundry services for hotels"},
            {"name": "XYZ Catering", "service": "Food Service", "status": "Approved", "contact": "catering@demo.com", 
             "registration_date": "2025-01-02", "service_fee": 7.5, "monthly_earnings": 4200, "services_completed": 28}
        ],
        'vendor_services': [
            # UPDATED TO 2025 - October services for ABC Laundry
            {"id": "VS001", "vendor_name": "ABC Laundry", "service_type": "Laundry", "location": "All Rooms", 
             "amount": 1500, "service_fee": 75, "date": "2025-10-31", "status": "Completed", "description": "Monthly laundry service"},
            {"id": "VS002", "vendor_name": "ABC Laundry", "service_type": "Laundry", "location": "Linen", 
             "amount": 500, "service_fee": 25, "date": "2025-10-15", "status": "Completed", "description": "Extra linen service"},
            # UPDATED TO 2025 - November services for ABC Laundry
            {"id": "VS003", "vendor_name": "ABC Laundry", "service_type": "Laundry", "location": "All Rooms", 
             "amount": 1600, "service_fee": 80, "date": "2025-11-30", "status": "Completed", "description": "Monthly laundry service"},
            {"id": "VS004", "vendor_name": "ABC Laundry", "service_type": "Laundry", "location": "Towels", 
             "amount": 350, "service_fee": 17.5, "date": "2025-11-20", "status": "Completed", "description": "Emergency towel service"},
        ],
        'vendor_statements': [
            # UPDATED TO 2025 - October payment to ABC Laundry
            {"id": "VS001", "vendor_name": "ABC Laundry", "month": "2025-10", "amount": 1900, 
             "services_count": 2, "service_fee_total": 100, "payment_date": "2025-11-05", 
             "payment_method": "Bank Transfer", "status": "Paid"},
            # UPDATED TO 2025 - November payment to ABC Laundry
            {"id": "VS002", "vendor_name": "ABC Laundry", "month": "2025-11", "amount": 1852.5, 
             "services_count": 2, "service_fee_total": 97.5, "payment_date": "2025-12-05", 
             "payment_method": "Bank Transfer", "status": "Paid"},
        ],
        'cancellation_requests': [],
        'refund_requests': [],
        'completed_bookings': [
            # UPDATED TO 2025
            {"id": "BK001", "guest": "John Traveler", "guest_email": "guest1@demo.com", "room_type": "Deluxe", 
             "check_in": "2025-10-15", "check_out": "2025-10-18", "status": "Completed", "payment_status": "Paid", 
             "amount": 1500, "amount_paid": 1500, "room_number": "301", "timestamp": "2025-10-15 14:30:00"},
            {"id": "BK002", "guest": "Sarah Visitor", "guest_email": "guest2@demo.com", "room_type": "Suite", 
             "check_in": "2025-10-25", "check_out": "2025-10-30", "status": "Completed", "payment_status": "Paid", 
             "amount": 1750, "amount_paid": 1750, "room_number": "203", "timestamp": "2025-10-25 15:45:00"},
        ]
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
def check_session_timeout():
    """Check if session has timed out (30 minutes)"""
    if st.session_state.authenticated and 'last_activity' in st.session_state:
        last_activity = datetime.strptime(st.session_state.last_activity, "%Y-%m-%d %H:%M:%S")
        time_diff = datetime.now() - last_activity
        if time_diff.total_seconds() > 1800:  # 30 minutes timeout
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.current_role = None
            st.warning("Session timed out due to inactivity. Please login again.")
            st.rerun()
    st.session_state.last_activity = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Notification system
def add_notification(message, category="info", target_roles=None, target_user=None):
    """Enhanced notification system with better targeting"""
    # Ensure target_roles is always a list (not None)
    if target_roles is None:
        target_roles = []
    
    notification = {
        "id": len(st.session_state.notifications) + 1,
        "message": message,
        "category": category,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False,
        "target_roles": target_roles,  # This will never be None now
        "target_user": target_user
    }
    st.session_state.notifications.append(notification)

# ADD this new function right after add_notification:
def get_user_notifications():
    """Get notifications relevant to current user with proper role-based filtering"""
    user_notifications = []
    current_role = st.session_state.current_role
    current_email = st.session_state.current_user['email']
    
    for notification in st.session_state.notifications:
        if notification['read']:
            continue
            
        target_roles = notification.get('target_roles', [])
        target_user = notification.get('target_user')
        
        # Enhanced role-based filtering with better logic
        show_notification = False
        
        # 1. Specifically targeted to this user (by email)
        if target_user and target_user == current_email:
            show_notification = True
        
        # 2. Targeted to user's role 
        elif target_roles and current_role in target_roles:
            show_notification = True
        
        # 3. No specific targeting (broadcast to all) - REMOVE THIS for role-based
        # We don't want to show broadcast notifications to everyone
        # elif not target_roles and not target_user:
        #    show_notification = True
        
        # 4. Special case: Hotel Manager sees all notifications except login messages
        elif current_role == "Hotel Manager" and notification['category'] != "login":
            show_notification = True
            
        if show_notification:
            user_notifications.append(notification)
    
    return user_notifications[-10:][::-1]  # Return last 10 notifications, reversed

def log_activity(user, action, details, level="INFO"):
    """Add an entry to system logs"""
    if 'system_logs' not in st.session_state:
        st.session_state.system_logs = []
    
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "action": action,
        "details": details,
        "level": level
    }
    st.session_state.system_logs.append(log_entry)

def show_system_logs():
    st.markdown('<div class="sub-header">📋 System Activity Logs</div>', unsafe_allow_html=True)
    
    # Initialize if not exists
    if 'system_logs' not in st.session_state:
        st.session_state.system_logs = []
    
    if not st.session_state.system_logs:
        st.info("No system logs available.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        log_level = st.selectbox("Filter by Level", ["ALL", "INFO", "WARNING", "ERROR"])
    with col2:
        search_user = st.text_input("Search by User")
    with col3:
        date_filter = st.date_input("Filter by Date")
    
    # Display logs
    filtered_logs = st.session_state.system_logs[::-1]  # Show latest first
    
    if log_level != "ALL":
        filtered_logs = [log for log in filtered_logs if log["level"] == log_level]
    
    if search_user:
        filtered_logs = [log for log in filtered_logs if search_user.lower() in log["user"].lower()]
    
    # Date filter implementation
    if date_filter:
        filtered_logs = [log for log in filtered_logs if log["timestamp"].startswith(date_filter.strftime("%Y-%m-%d"))]
    
    # Show limited logs with pagination info
    display_logs = filtered_logs[:50]  # Show last 50 logs
    
    st.info(f"Showing {len(display_logs)} of {len(filtered_logs)} logs")
    
    for log in display_logs:
        level_color = {
            "INFO": "card",
            "WARNING": "warning-card", 
            "ERROR": "critical-card"
        }.get(log["level"], "card")
        
        st.markdown(f"""
        <div class="card {level_color}">
            <p><strong>{log['timestamp']} | {log['level']} | {log['user']}</strong></p>
            <p><strong>Action:</strong> {log['action']}</p>
            <p><strong>Details:</strong> {log['details']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Clear logs button
    if st.button("🗑️ Clear All Logs", type="secondary"):
        st.session_state.system_logs = []
        st.rerun()

def show_past_work(role):
    st.markdown(f'<div class="sub-header">📋 Completed Tasks - {role}</div>', unsafe_allow_html=True)
    
    # Get completed tasks for this role
    if role == "Maintenance Staff":
        completed_items = [r for r in st.session_state.service_requests if r["type"] == "Maintenance" and r["status"] == "Completed"]
    else:
        completed_items = [t for t in st.session_state.tasks if t["assigned_to"] == role and t["status"] == "Completed"]
    
    if not completed_items:
        st.info("No completed work found.")
        return
    
    # Display completed work
    for item in completed_items[::-1]:  # Show latest first
        if role == "Maintenance Staff":
            # For maintenance, use service requests
            st.markdown(f"""
            <div class="card success-card">
                <h4>🔧 Maintenance - Room {item['room']}</h4>
                <p><strong>Issue:</strong> {item['details']}</p>
                <p><strong>Guest:</strong> {item['guest']}</p>
                <p><strong>Urgency:</strong> {item['urgency']}</p>
                <p><strong>Completed On:</strong> {item.get('completed_at', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # For other roles, use tasks
            st.markdown(f"""
            <div class="card success-card">
                <h4>{item['type']} - {item.get('room', 'N/A')}</h4>
                <p><strong>Description:</strong> {item['description']}</p>
                <p><strong>Assigned:</strong> {item['timestamp']}</p>
                <p><strong>Completed By:</strong> {item.get('completed_by', st.session_state.current_user['name'])}</p>
                <p><strong>Completed At:</strong> {item.get('completed_at', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Completed", len(completed_items))
    with col2:
        # Calculate completion rate (for tasks only)
        if role != "Maintenance Staff":
            total_tasks = len([t for t in st.session_state.tasks if t["assigned_to"] == role])
            if total_tasks > 0:
                completion_rate = (len(completed_items) / total_tasks) * 100
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
            else:
                st.metric("Completion Rate", "0%")
    with col3:
        # Recent activity
        recent_count = len([item for item in completed_items if datetime.strptime(item.get('completed_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S').date() == datetime.now().date()])
        st.metric("Today's Completions", recent_count)


def show_calendar(role="General"):
    st.markdown('<div class="sub-header">📅 Hotel Calendar</div>', unsafe_allow_html=True)
    
    # Initialize meetings if not exists
    if 'meetings' not in st.session_state:
        st.session_state.meetings = []
    
    # Add demo meeting data for 2025
    demo_meetings = [
        {"title": "Corporate Conference", "date": "2025-10-15", "time": "09:00", "venue": "Grand Ballroom", "department": "Event & Concierge Staff", "remarks": "AV setup required", "guest": "Tech Corp", "room": "Conference Hall"},
        {"title": "Wedding Reception", "date": "2025-10-20", "time": "18:00", "venue": "Garden Pavilion", "department": "Catering Staff", "remarks": "Vegetarian menu required", "guest": "Smith Wedding", "room": "Outdoor"},
        {"title": "Board Meeting", "date": "2025-11-05", "time": "14:00", "venue": "Executive Room", "department": "Event & Concierge Staff", "remarks": "Projector and whiteboard", "guest": "ABC Company", "room": "Executive Room"},
        {"title": "Product Launch", "date": "2025-11-15", "time": "10:00", "venue": "Main Hall", "department": "All Staff", "remarks": "Large event - all hands", "guest": "Innovate Inc", "room": "Main Hall"},
        {"title": "Birthday Party", "date": "2025-10-25", "time": "16:00", "venue": "Poolside", "department": "Event & Concierge Staff", "remarks": "Decorations needed", "guest": "Johnson Family", "room": "Pool Area"},
    ]
    
    # Add demo data if empty
    if not st.session_state.meetings:
        st.session_state.meetings.extend(demo_meetings)
    
    # Combine demo and actual meetings
    all_meetings = st.session_state.meetings
    
    # For Event & Concierge, show specialized view
    if role == "Event & Concierge Staff":
        st.markdown("#### 🎊 Event & Concierge Schedule")
        
        # Filter only events for this department
        department_meetings = [m for m in all_meetings if m["department"] in ["Event & Concierge Staff", "All Staff"]]
        
        # Upcoming events
        st.markdown("##### Upcoming Events")
        today = datetime.now().strftime("%Y-%m-%d")
        upcoming_events = [m for m in department_meetings if m["date"] >= today]
        
        if upcoming_events:
            for event in sorted(upcoming_events, key=lambda x: x['date'])[:5]:
                st.markdown(f"""
                <div class="card success-card">
                    <h4>🎉 {event['title']}</h4>
                    <p><strong>📅 Date:</strong> {event['date']} | <strong>⏰ Time:</strong> {event['time']}</p>
                    <p><strong>📍 Venue:</strong> {event['venue']}</p>
                    <p><strong>👤 Guest:</strong> {event['guest']}</p>
                    <p><strong>📝 Remarks:</strong> {event['remarks']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No upcoming events scheduled.")
        
        # Event statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Events", len(department_meetings))
        with col2:
            st.metric("Upcoming Events", len(upcoming_events))
        with col3:
            completed_events = len([m for m in department_meetings if m["date"] < today])
            st.metric("Completed Events", completed_events)
    
    else:
        # General calendar view for other staff
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_month = st.selectbox("Select Month", 
                                        ["October 2025", "November 2025", "December 2025"])
            
            # Filter meetings for selected month
            month_map = {"October 2025": "2025-10", "November 2025": "2025-11", "December 2025": "2025-12"}
            selected_month_prefix = month_map[selected_month]
            month_meetings = [m for m in all_meetings if m["date"].startswith(selected_month_prefix)]
            
            if month_meetings:
                for meeting in month_meetings:
                    st.markdown(f"""
                    <div class="card">
                        <h4>📅 {meeting['title']}</h4>
                        <p><strong>Date:</strong> {meeting['date']} | <strong>Time:</strong> {meeting['time']}</p>
                        <p><strong>Venue:</strong> {meeting['venue']} | <strong>Department:</strong> {meeting['department']}</p>
                        <p><strong>Guest:</strong> {meeting['guest']} | <strong>Room:</strong> {meeting['room']}</p>
                        <p><strong>Remarks:</strong> {meeting['remarks']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No meetings scheduled for this month.")
        
        with col2:
            st.markdown("#### Quick Stats")
            st.metric("Total Meetings", len(all_meetings))
            st.metric(f"Meetings in {selected_month}", len(month_meetings))
            
            # Department filter
            departments = list(set(m["department"] for m in all_meetings))
            selected_dept = st.selectbox("Filter by Department", ["All"] + departments)
            if selected_dept != "All":
                dept_meetings = [m for m in all_meetings if m["department"] == selected_dept]
                st.metric(f"{selected_dept} Meetings", len(dept_meetings))

# Authentication system
def authenticate_user(email, password, role):
    # Check demo accounts first
    for account_role, accounts in DEMO_ACCOUNTS.items():
        if role == account_role:
            for account in accounts:
                if account["email"] == email and account["password"] == password:
                    return account
    
    # Check registered users
    for user in st.session_state.registered_users:
        if user["email"] == email and user["role"] == role:
            if user["status"] == "Active" and user.get("password") == password:
                return {"email": user["email"], "password": password, "name": user["name"]}
    
    return None

# UPDATED LOGIN FORM - REPLACE THE EXISTING show_login_form FUNCTION
def show_login_form():
    # Centered login container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="sub-header" style="text-align: center;">🔐 System Login</div>', unsafe_allow_html=True)
        
        role = st.selectbox(
            "Select Your Role",
            list(DEMO_ACCOUNTS.keys()),
            key="login_role"
        )
        
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("🚀 Login to System", use_container_width=True):
            if not email or not password:
                st.error("Please enter both email and password")
                return
                
            user = authenticate_user(email, password, role)
            if user:
                st.session_state.authenticated = True
                st.session_state.current_user = user
                st.session_state.current_role = role
                add_notification(f"User {user['name']} logged in as {role}", "success")
                # ADD LOG ENTRY:
                log_activity(user['name'], "User Login", f"Logged in as {role}")
                st.success(f"Welcome back, {user['name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please check your email, password, and role selection.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
def validate_user_access():
    """Validate that the current user has proper access to their role"""
    if not st.session_state.authenticated:
        return False
    
    current_user = st.session_state.current_user
    current_role = st.session_state.current_role
    
    # Check if current_user exists
    if current_user is None or current_role is None:
        return False
    
    # Check if user exists in registered users with matching role
    for user in st.session_state.registered_users:
        if user["email"] == current_user["email"] and user["role"] == current_role:
            if user["status"] == "Active":
                return True
    
    # If not found, check demo accounts
    for account_role, accounts in DEMO_ACCOUNTS.items():
        if account_role == current_role:
            for account in accounts:
                if account["email"] == current_user["email"] and account["password"] == current_user["password"]:
                    return True
    
    return False

    
def enforce_auto_cancels():
    """Auto-cancel unpaid bookings after 2 hours"""
    try:
        # Check if invoices and bookings exist in session state
        if 'invoices' not in st.session_state or 'bookings' not in st.session_state:
            return
            
        current_time = datetime.now()
        for inv in st.session_state.invoices:
            if inv["status"] == "Pending":
                due_date = datetime.strptime(inv["due_date"], "%Y-%m-%d %H:%M:%S")
                if current_time > due_date:
                    # Cancel the invoice
                    inv["status"] = "Cancelled"
                    # Find and cancel the corresponding booking
                    for booking in st.session_state.bookings:
                        if booking["id"] == inv["booking_id"]:
                            booking["status"] = "Cancelled"
                            booking["cancellation_status"] = "Auto-cancelled (Payment not received)"
                            add_notification(f"Booking #{booking['id']} auto-cancelled due to non-payment", "cancellation")
                            break
    except Exception as e:
        # Silently handle errors during auto-cancellation
        pass
    
# Main application
def main():
    # Initialize session data
    init_session_data()
    
    # Check session timeout
    check_session_timeout()
    
    if st.session_state.get('debug_mode', False):
        st.sidebar.write("🔍 Debug Info:")
        st.sidebar.write(f"Authenticated: {st.session_state.get('authenticated', 'Not set')}")
        st.sidebar.write(f"Current User: {st.session_state.get('current_user', 'Not set')}")
        st.sidebar.write(f"Current Role: {st.session_state.get('current_role', 'Not set')}")
   
    # Show login page if not authenticated
    if not st.session_state.authenticated:
        show_login_page()
    else:
        # Validate user access on every page load
        if not validate_user_access():
            st.error("⚠️ Access validation failed. Please login again.")
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.current_role = None
            st.rerun()
        
        # Additional safety check - ensure current_user exists
        if st.session_state.current_user is None:
            st.error("Session error: User data missing. Please login again.")
            st.session_state.authenticated = False
            st.rerun()
        
        # Move enforce_auto_cancels here so it only runs when user is authenticated
        enforce_auto_cancels()
        show_main_application()

def show_login_page():
    # Elegant cover section
    st.markdown("""
    <div class="elegant-cover">
        <div class="elegant-title">🏨 Grand Stay Hotel</div>
        <div class="elegant-subtitle">Classic Luxury & Timeless Hospitality</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for Login and Registration
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "👤 Guest Registration", "🤝 Vendor Registration"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_guest_registration()
    
    with tab3:
        show_vendor_registration()
    
    # Demo accounts section
    st.markdown("---")
    st.markdown('<div class="sub-header" style="text-align: center;">👥 Demo Accounts</div>', unsafe_allow_html=True)
    st.info("Use these demo accounts to explore the system. Login credentials are provided below:")
    
    # Display demo accounts in a clean layout
    for role_name, accounts in DEMO_ACCOUNTS.items():
        with st.expander(f"{role_name} Accounts", expanded=False):
            for account in accounts:
                st.markdown(f"""
                <div class="demo-account">
                    <strong>👤 {account['name']}</strong><br>
                    <strong>📧 Email:</strong> {account['email']}<br>
                    <strong>🔑 Password:</strong> {account['password']}<br>
                    <strong>🎯 Role:</strong> {role_name}
                </div>
                """, unsafe_allow_html=True)

def show_login_form():
    # Centered login container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="sub-header" style="text-align: center;">🔐 System Login</div>', unsafe_allow_html=True)
        
        role = st.selectbox(
            "Select Your Role",
            list(DEMO_ACCOUNTS.keys()),
            key="login_role"
        )
        
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("🚀 Login to System", use_container_width=True):
            if not email or not password:
                st.error("Please enter both email and password")
                return
                
            user = authenticate_user(email, password, role)
            if user:
                # Ensure user data is properly set
                st.session_state.authenticated = True
                st.session_state.current_user = user
                st.session_state.current_role = role
                st.session_state.last_activity = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                add_notification(f"User {user['name']} logged in as {role}", "success")
                log_activity(user['name'], "User Login", f"Logged in as {role}")
                st.success(f"Welcome back, {user['name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please check your email, password, and role selection.")
        
        st.markdown('</div>', unsafe_allow_html=True)
            # Add password recovery
    st.markdown("---")
    if st.button("🔒 Forgot Password?"):
        st.session_state.show_password_recovery = True
    
    if st.session_state.get('show_password_recovery', False):
        with st.form("password_recovery"):
            st.markdown("#### Password Recovery")
            recovery_email = st.text_input("Enter your email address")
            recovery_role = st.selectbox("Your Role", list(DEMO_ACCOUNTS.keys()))
            
            if st.form_submit_button("Send Password Reset"):
                # Find user and show password (in real app, would send email)
                user_found = False
                for user in st.session_state.registered_users:
                    if user["email"] == recovery_email and user["role"] == recovery_role:
                        st.success(f"Password recovery email sent to {recovery_email}")
                        st.info(f"Your password is: {user['password']}")
                        user_found = True
                        break
                
                if not user_found:
                    st.error("No account found with these details.")
        

def show_guest_registration():
    st.markdown('<div class="sub-header" style="text-align: center;">👤 New Guest Registration</div>', unsafe_allow_html=True)
    
    with st.form("guest_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name *")
            email = st.text_input("Email Address *")
            phone = st.text_input("Phone Number *")
            id_type = st.selectbox("ID Type *", ["Passport", "Driver's License", "National ID"])
        
        with col2:
            id_number = st.text_input("ID Number *")
            address = st.text_area("Home Address *")
            emergency_contact = st.text_input("Emergency Contact")
            preferred_payment = st.selectbox("Preferred Payment Method", ["Credit Card", "Debit Card", "Online Banking", "E-Wallet", "Cash"])
        
        
        # NEW: Password fields for guest registration
        st.markdown("#### Account Security")
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input("Create Password *", type="password", help="Minimum 8 characters")
        with col2:
            confirm_password = st.text_input("Confirm Password *", type="password")
        
        # Terms and conditions
        agree_terms = st.checkbox("I agree to the terms and conditions *")
        
        submitted = st.form_submit_button("📝 Register as Guest")
        
        if submitted:
            # Validation
            if not all([full_name, email, phone, id_type, id_number, address, password, confirm_password]):
                st.error("Please fill in all required fields (*)")
            elif password != confirm_password:
                st.error("Passwords do not match!")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters long")
            elif not agree_terms:
                st.error("Please agree to the terms and conditions")
            else:
                # Check if email already exists
                existing_user = any(user["email"] == email for user in st.session_state.registered_users)
                if existing_user:
                    st.error("This email is already registered. Please use a different email.")
                else:
                    # Add new guest to registered users
                    new_guest = {
                        "email": email,
                        "name": full_name,
                        "role": "Guest",
                        "status": "Active",
                        "registration_date": datetime.now().strftime("%Y-%m-%d"),
                        "phone": phone,
                        "id_type": id_type,
                        "id_number": id_number,
                        "address": address,
                        "emergency_contact": emergency_contact,
                        "preferred_payment": preferred_payment,
                        "password": password  # Store password
                    }
                    st.session_state.registered_users.append(new_guest)
                    
                    log_activity("System", "New User Registration", 
                            f"New Guest registered: {full_name} ({email})")
                    
                    # Add to guest applications for record
                    st.session_state.guest_applications.append({
                        **new_guest,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    add_notification(f"New guest registered: {full_name}", "registration", ["Hotel Manager"])
                    st.success(f"🎉 Registration successful! You can now login as a Guest with your email and password.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_vendor_registration():
    st.markdown('<div class="sub-header" style="text-align: center;">🤝 New Vendor Registration</div>', unsafe_allow_html=True)
    
    with st.form("vendor_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *")
            contact_person = st.text_input("Contact Person *")
            email = st.text_input("Email Address *")
            phone = st.text_input("Phone Number *")
        
        with col2:
            service_type = st.selectbox("Service Type *", 
                                      ["Laundry", "Catering", "Transportation", "Maintenance", 
                                       "Entertainment", "Security", "Cleaning Supplies", "Other"])
            service_description = st.text_area("Service Description *")
            years_experience = st.number_input("Years of Experience", min_value=0, max_value=50)
        
        # Service fee agreement
        st.markdown("#### Service Agreement")
        service_fee = st.number_input("Proposed Service Fee (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.5,
                                     help="Percentage fee charged for each service engagement")
        
        # Documents upload
        st.markdown("#### Business Documents")
        col1, col2 = st.columns(2)
        with col1:
            business_license = st.file_uploader("Business License", type=['pdf', 'jpg', 'png'])
        with col2:
            insurance_cert = st.file_uploader("Insurance Certificate", type=['pdf', 'jpg', 'png'])
        
        # Terms and conditions
        agree_terms = st.checkbox("I agree to the terms and conditions and understand approval is required *")
        
        submitted = st.form_submit_button("📝 Register as Vendor")
        
        if submitted:
            if not all([company_name, contact_person, email, phone, service_type, service_description]):
                st.error("Please fill in all required fields (*)")
            elif not agree_terms:
                st.error("Please agree to the terms and conditions")
            else:
                # Check if vendor already exists
                existing_vendor = any(vendor["name"] == company_name for vendor in st.session_state.vendors)
                if existing_vendor:
                    st.error("This company is already registered. Please contact support if this is an error.")
                else:
                    # Add new vendor to applications
                    new_vendor = {
                        "name": company_name,
                        "contact_person": contact_person,
                        "email": email,
                        "phone": phone,
                        "service": service_type,
                        "description": service_description,
                        "experience": years_experience,
                        "service_fee": service_fee,
                        "status": "Pending",
                        "registration_date": datetime.now().strftime("%Y-%m-%d"),
                        "monthly_earnings": 0,
                        "services_completed": 0,
                        "documents": {
                            "business_license": business_license is not None,
                            "insurance_cert": insurance_cert is not None
                        }
                    }
                    st.session_state.vendor_applications.append(new_vendor)
                    
                    # Add contact person as registered user with Vendor role
                    st.session_state.registered_users.append({
                        "email": email,
                        "name": contact_person,
                        "role": "Vendor",
                        "status": "Pending",
                        "registration_date": datetime.now().strftime("%Y-%m-%d"),
                        "password": "vendor123"  # Default password
                    })
                    
                    # ADD LOG ENTRY HERE:
                    log_activity("System", "New User Registration", 
                            f"New Vendor application: {company_name} - {contact_person} ({email})")
                
                    add_notification(f"New vendor application: {company_name}", "vendor", ["Hotel Manager"])
                    st.success(f"📋 Vendor application submitted! {company_name} is now pending approval. You will be notified once approved.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_main_application():
    with st.sidebar:
        # FIX: Add safety check for current_user
        if st.session_state.current_user is None:
            st.error("User session error. Please login again.")
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown(f"""
        <div class="sidebar-header">
            <h3>👋 Welcome, {st.session_state.current_user['name']}</h3>
            <p><strong>Role:</strong> {st.session_state.current_role}</p>
            <p>🔔 Notifications </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Notifications section
        user_notifications = get_user_notifications()
        if user_notifications:
            with st.expander("📋 Recent Notifications", expanded=False):
                for notification in user_notifications:
                    st.write(f"🔔 {notification['message']}")
                    st.caption(notification['timestamp'])
                
                if st.button("Mark All as Read", use_container_width=True):
                    for notification in st.session_state.notifications:
                        notification['read'] = True
                    st.rerun()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.current_role = None
            st.rerun()
    
    # Main application based on role
    if st.session_state.current_role == "Guest":
        show_guest_portal()
    elif st.session_state.current_role == "Front Desk Officer":
        show_front_desk_portal()
    elif st.session_state.current_role == "Housekeeping Staff":
        show_housekeeping_portal()
    elif st.session_state.current_role == "Maintenance Staff":
        show_maintenance_portal()
    elif st.session_state.current_role == "Hotel Manager":
        show_manager_portal()
    elif st.session_state.current_role == "Billing Officer":
        show_billing_portal()
    elif st.session_state.current_role == "Vendor":
        show_vendor_portal()
    elif st.session_state.current_role == "Catering Staff":
        show_catering_portal()
    elif st.session_state.current_role == "Event & Concierge Staff":
        show_event_concierge_portal()

# ==================== GUEST PORTAL ====================
def show_guest_portal():
    st.markdown('<div class="main-header">👤 Guest Portal - Grand Stay Hotel</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([  
        "🏠 Book Room", "📋 My Bookings", "🛎️ Service Requests", 
        "⭐ Leave Review", "📝 Recent Reviews", "👤 My Profile", "✏️ Modify Booking", "🔔 Notifications"  
    ])
    
    with tab1:
        show_guest_booking()
    with tab2:
        show_guest_bookings()
    with tab3:
        show_guest_service_requests()
    with tab4:
        show_guest_reviews()
    with tab5:
        show_recent_reviews()
    with tab6:
        show_guest_profile_management()
    with tab7:  
        show_booking_modification()
    with tab8:  
        show_guest_notifications()

def show_guest_booking():
    st.markdown('<div class="sub-header">📅 Room Reservation</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        room_type = st.selectbox("Room Type", ["Single", "Double", "Suite", "Deluxe"])
        check_in = st.date_input("Check-in Date", datetime.now())
        num_guests = st.number_input("Number of Guests", min_value=1, max_value=4, value=2)
        duration_type = st.selectbox("Booking Type", ["Daily", "Weekly", "Monthly"])
    
    with col2:
        check_out = st.date_input("Check-out Date", datetime.now() + timedelta(days=1))
        meal_package = st.selectbox("Meal Package", ["None", "Breakfast Only", "Half Board", "Full Board"])
        special_requests = st.text_area("Special Requests")
    
    # Additional services
    st.markdown("#### Additional Services")
    col1, col2, col3 = st.columns(3)
    with col1:
        airport_pickup = st.checkbox("Airport Pickup ($50)")
        spa_access = st.checkbox("Spa Access ($75)")
    with col2:
        gym_access = st.checkbox("Gym Access (Complimentary)")
        guided_tours = st.checkbox("Guided City Tour ($100)")
    
    # Price calculation
    room_prices = {"Single": 150, "Double": 200, "Suite": 350, "Deluxe": 500}
    base_price = room_prices[room_type]
    nights = max(1, (check_out - check_in).days)
    total_price = base_price * nights
    
    if airport_pickup:
        total_price += 50
    if spa_access:
        total_price += 75
    if guided_tours:
        total_price += 100
    
    # Display price summary
    st.markdown("#### Price Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card">
            <h4>Booking Details</h4>
            <p><strong>Room:</strong> {room_type}</p>
            <p><strong>Duration:</strong> {nights} nights</p>
            <p><strong>Base Price:</strong> ${base_price * nights}</p>
            <p><strong>Additional Services:</strong> ${total_price - (base_price * nights)}</p>
            <hr>
            <h4>Total: ${total_price}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Payment options
    st.markdown("#### Payment Method")
    payment_method = st.selectbox("Select Payment Method", 
                                 ["Credit Card", "Debit Card", "Online Banking", "E-Wallet", "Cash"])
    
    # Cancellation policy
    st.markdown("#### Cancellation Policy")
    st.info("""
    - **Free cancellation**: Up to 2 hours after booking confirmation
    - **Standard cancellation**: 48 hours before check-in - 50% refund
    - **Late cancellation**: Less than 48 hours - No refund
    - **Processing fee**: 2% of refund amount for successful bookings
    """)
    
    # Payment confirmation
    if st.button("💳 Confirm Booking & Proceed to Payment", use_container_width=True):
        booking_id = f"BK{len(st.session_state.bookings) + 1:03d}"
        new_booking = {
            "id": booking_id,
            "guest": st.session_state.current_user['name'],
            "guest_email": st.session_state.current_user['email'],
            "room_type": room_type,
            "check_in": check_in.strftime("%Y-%m-%d"),
            "check_out": check_out.strftime("%Y-%m-%d"),
            "status": "Confirmed",
            "payment_status": "Pending",  # NEW: Track payment status separately
            "amount": total_price,
            "amount_paid": 0,  # NEW: Track paid amount
            "special_requests": special_requests,
            "payment_method": payment_method,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cancellation_status": "Not Requested"  # NEW: Track cancellation
        }
        st.session_state.bookings.append(new_booking)
        
        # Create invoice
        invoice_id = f"INV{len(st.session_state.invoices) + 1:03d}"
        new_invoice = {
            "id": invoice_id,
            "booking_id": booking_id,
            "guest": st.session_state.current_user['name'],
            "amount": total_price,
            "status": "Pending",
            "payment_method": payment_method,
            "due_date": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.invoices.append(new_invoice)
        
        # Send notifications
        add_notification(f"New booking #{booking_id} from {st.session_state.current_user['name']}", "booking", ["Front Desk Officer", "Hotel Manager"])
        add_notification(f"Payment required for booking #{booking_id} - ${total_price}", "payment", ["Billing Officer"])
        
        # If special requests, notify front desk
        if special_requests:
            add_notification(f"Special requirements for booking #{booking_id}: {special_requests}", "special_request", ["Front Desk Officer"])
        
        st.success(f"🎉 Booking confirmed! Your booking ID is {booking_id}. Please complete payment within 2 hours.")
        
        # Show provisional invoice
        st.markdown(f"""
        <div class="card success-card">
            <h4>📄 Provisional Invoice #{invoice_id}</h4>
            <p><strong>Booking ID:</strong> {booking_id}</p>
            <p><strong>Guest:</strong> {st.session_state.current_user['name']}</p>
            <p><strong>Amount Due:</strong> ${total_price}</p>
            <p><strong>Payment Method:</strong> {payment_method}</p>
            <p><strong>Payment Deadline:</strong> {(datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="color: #E74C3C;"><strong>⚠️ Important:</strong> Booking will auto-cancel if payment not completed in 2 hours</p>
        </div>
        """, unsafe_allow_html=True)

def show_guest_booking():
    st.markdown('<div class="sub-header">📅 Room Reservation</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # UPDATED: Added new room types
        room_type = st.selectbox("Room Type", ["Single", "Double", "Suite", "Deluxe"])
        check_in = st.date_input("Check-in Date", datetime.now())
        num_guests = st.number_input("Number of Guests", min_value=1, max_value=4, value=2)  # Increased max to 6 for family rooms
        duration_type = st.selectbox("Booking Type", ["Hourly","Daily", "Weekly", "Monthly"])
    
    with col2:
        check_out = st.date_input("Check-out Date", datetime.now() + timedelta(days=1))
        meal_package = st.selectbox("Meal Package", ["None", "Breakfast Only", "Half Board", "Full Board"])
        special_requests = st.text_area("Special Requests")
    
    if check_in and check_out and room_type:
        if check_out <= check_in:
            st.error("Check-out date must be after check-in date")
        else:
            show_room_availability_for_guest(
                check_in.strftime("%Y-%m-%d"), 
                check_out.strftime("%Y-%m-%d"), 
                room_type
            )
    
    # Additional services
    st.markdown("#### Additional Services")
    col1, col2, col3 = st.columns(3)
    with col1:
        airport_pickup = st.checkbox("Airport Pickup ($50)")
        spa_access = st.checkbox("Spa Access ($75)")
    with col2:
        gym_access = st.checkbox("Gym Access (Complimentary)")
        guided_tours = st.checkbox("Guided City Tour ($100)")
    
    # PRICE CALCULATION - THIS WAS MISSING
    room_prices = {"Single": 150, "Double": 200, "Suite": 350, "Deluxe": 500}
    base_price = room_prices[room_type]
    nights = max(1, (check_out - check_in).days)
    total_price = base_price * nights
    
    if airport_pickup:
        total_price += 50
    if spa_access:
        total_price += 75
    if guided_tours:
        total_price += 100
    
    # Display price summary
    st.markdown("#### Price Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card">
            <h4>Booking Details</h4>
            <p><strong>Room:</strong> {room_type}</p>
            <p><strong>Duration:</strong> {nights} nights</p>
            <p><strong>Base Price:</strong> ${base_price * nights}</p>
            <p><strong>Additional Services:</strong> ${total_price - (base_price * nights)}</p>
            <hr>
            <h4>Total: ${total_price}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # PAYMENT METHOD - THIS WAS MISSING
    st.markdown("#### Payment Method")
    payment_method = st.selectbox("Select Payment Method", 
                                 ["Credit Card", "Debit Card", "Online Banking", "E-Wallet", "Cash"])
    
    # Cancellation policy
    st.markdown("#### Cancellation Policy")
    st.info("""
    - **Free cancellation**: Up to 2 hours after booking confirmation
    - **Standard cancellation**: 48 hours before check-in - 50% refund
    - **Late cancellation**: Less than 48 hours - No refund
    - **Processing fee**: 2% of refund amount for successful bookings
    """)
    
    # Payment confirmation
    if st.button("💳 Confirm Booking & Proceed to Payment", use_container_width=True):
        assigned_room = assign_room_automatically(room_type, check_in.strftime("%Y-%m-%d"), check_out.strftime("%Y-%m-%d"))
        
        booking_id = f"BK{len(st.session_state.bookings) + 1:03d}"
        new_booking = {
            "id": booking_id,
            "guest": st.session_state.current_user['name'],
            "guest_email": st.session_state.current_user['email'],
            "room_type": room_type,
            "room_number": assigned_room,
            "check_in": check_in.strftime("%Y-%m-%d"),
            "check_out": check_out.strftime("%Y-%m-%d"),
            "status": "Confirmed",
            "payment_status": "Pending",
            "amount": total_price,
            "amount_paid": 0,
            "special_requests": special_requests,
            "payment_method": payment_method,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cancellation_status": "Not Requested"
        }
        
        # Update room status to "pending" instead of "occupied"
        if assigned_room:
            for room in st.session_state.rooms:
                if room["number"] == assigned_room:
                    room["status"] = "pending"  # CHANGED FROM "occupied" to "pending"
                    room["guest"] = st.session_state.current_user['name']
                    break
        
        st.session_state.bookings.append(new_booking)
        
        # ADD LOG ENTRY:
        log_activity(st.session_state.current_user['name'], "Booking Created", 
                f"Booking {booking_id} for ${total_price} - Room {assigned_room}")
    
        # Create invoice
        invoice_id = f"INV{len(st.session_state.invoices) + 1:03d}"
        new_invoice = {
            "id": invoice_id,
            "booking_id": booking_id,
            "guest": st.session_state.current_user['name'],
            "amount": total_price,
            "status": "Pending",
            "payment_method": payment_method,
            "due_date": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.invoices.append(new_invoice)
        
        # Send notifications
        add_notification(f"New booking #{booking_id} from {st.session_state.current_user['name']}", "booking", ["Front Desk Officer", "Hotel Manager"])
        add_notification(f"Payment required for booking #{booking_id} - ${total_price}", "payment", ["Billing Officer"])
        
        # If special requests, notify front desk
        if special_requests:
            add_notification(f"Special requirements for booking #{booking_id}: {special_requests}", "special_request", ["Front Desk Officer"])
        
        st.success(f"🎉 Booking confirmed! Your booking ID is {booking_id}. Room {assigned_room} has been reserved for you. Please complete payment within 2 hours.")
        
        # Show provisional invoice
        st.markdown(f"""
        <div class="card success-card">
        <h4>📄 Provisional Invoice #{invoice_id}</h4>
        <p><strong>Booking ID:</strong> {booking_id}</p>
        <p><strong>Guest:</strong> {st.session_state.current_user['name']}</p>
        <p><strong>Room Type:</strong> {room_type}</p>
        <p><strong>Room Number:</strong> {assigned_room}</p>
        <p><strong>Amount Due:</strong> ${total_price}</p>
        <p><strong>Payment Method:</strong> {payment_method}</p>
        <p><strong>Payment Deadline:</strong> {(datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p style="color: #E74C3C;"><strong>⚠️ Important:</strong> Booking will auto-cancel if payment not completed in 2 hours</p>
        </div>
        """, unsafe_allow_html=True)
        

def show_booking_modification():
    st.markdown('<div class="sub-header">✏️ Modify Booking</div>', unsafe_allow_html=True)
    
    # Get guest's confirmed bookings - FIXED: Include bookings with room numbers
    guest_bookings = [
        b for b in st.session_state.bookings 
        if b["guest_email"] == st.session_state.current_user['email'] 
        and b["status"] in ["Confirmed", "Pending"]
        and datetime.strptime(b["check_in"], "%Y-%m-%d") > datetime.now()
    ]
    
    if not guest_bookings:
        st.info("No modifiable bookings found.")
        return
    
    selected_booking_id = st.selectbox(
        "Select Booking to Modify",
        [f"{b['id']} - {b['room_type']} ({b['check_in']} to {b['check_out']})" for b in guest_bookings]
    )
    
    if selected_booking_id:
        booking_id = selected_booking_id.split(" - ")[0]
        booking = next(b for b in guest_bookings if b['id'] == booking_id)
        
        st.markdown("#### Current Booking Details")
        st.write(f"**Booking ID:** {booking['id']}")
        st.write(f"**Room Type:** {booking['room_type']}")
        st.write(f"**Current Dates:** {booking['check_in']} to {booking['check_out']}")
        st.write(f"**Room Number:** {booking.get('room_number', 'Will be assigned after payment')}")
        st.write(f"**Special Requests:** {booking.get('special_requests', 'None')}")
        
        st.markdown("#### Modify Booking")
        col1, col2 = st.columns(2)
        
        with col1:
            new_check_in = st.date_input("New Check-in Date", 
                                       value=datetime.strptime(booking['check_in'], "%Y-%m-%d"))
            # FIXED: Use only 4 room types
            new_room_type = st.selectbox("New Room Type", ["Single", "Double", "Suite", "Deluxe"],
                                       index=["Single", "Double", "Suite", "Deluxe"].index(booking['room_type']))
        
        with col2:
            new_check_out = st.date_input("New Check-out Date", 
                                        value=datetime.strptime(booking['check_out'], "%Y-%m-%d"))
            new_special_requests = st.text_area("New Special Requests", value=booking.get('special_requests', ''))
        
        # Price recalculation - FIXED: Use only 4 room types
        room_prices = {"Single": 150, "Double": 200, "Suite": 350, "Deluxe": 500}
        base_price = room_prices[new_room_type]
        nights = max(1, (new_check_out - new_check_in).days)
        new_total_price = base_price * nights
        
        st.markdown(f"**New Total Price:** ${new_total_price}")
        st.markdown(f"**Price Difference:** ${new_total_price - booking['amount']}")
        
        if st.button("📝 Submit Modification Request", use_container_width=True):
            # Create modification request
            modification_request = {
                "booking_id": booking_id,
                "guest": booking['guest'],
                "original_room_type": booking['room_type'],
                "new_room_type": new_room_type,
                "original_dates": f"{booking['check_in']} to {booking['check_out']}",
                "new_dates": f"{new_check_in.strftime('%Y-%m-%d')} to {new_check_out.strftime('%Y-%m-%d')}",
                "original_amount": booking['amount'],
                "new_amount": new_total_price,
                "status": "Pending",
                "request_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "special_requests": new_special_requests
            }
            
            # Add to a new session state list for modification requests
            if 'modification_requests' not in st.session_state:
                st.session_state.modification_requests = []
            st.session_state.modification_requests.append(modification_request)
            
            add_notification(f"Modification request for booking #{booking_id}", "modification", ["Front Desk Officer"])
            st.success("Modification request submitted! Front desk will contact you to confirm changes.")
        
def show_guest_bookings():
    st.markdown('<div class="sub-header">📋 My Bookings</div>', unsafe_allow_html=True)
    
    guest_bookings = [b for b in st.session_state.bookings if b["guest_email"] == st.session_state.current_user['email']]
    
    # Also include completed bookings for historical records
    completed_bookings = [b for b in st.session_state.completed_bookings if b["guest_email"] == st.session_state.current_user['email']]
    
    if not guest_bookings and not completed_bookings:
        st.info("You have no current or past bookings.")
        return
    
    # Current bookings
    if guest_bookings:
        st.markdown("#### Current Bookings")
        for booking in guest_bookings:
            # Determine status color
            if booking["status"] == "Confirmed" and booking["payment_status"] == "Paid":
                status_color = "success-card"
            elif booking["status"] == "Confirmed" and booking["payment_status"] == "Pending":
                status_color = "warning-card"
            elif booking["status"] == "Cancelled":
                status_color = "critical-card"
            else:
                status_color = "card"
            
            st.markdown(f"""
            <div class="card {status_color}">
                <h4>Booking #{booking['id']} - {booking['room_type']}</h4>
                <p><strong>Dates:</strong> {booking['check_in']} to {booking['check_out']}</p>
                <p><strong>Status:</strong> {booking['status']} | <strong>Payment:</strong> {booking.get('payment_status', 'Pending')}</p>
                <p><strong>Amount:</strong> ${booking['amount']} | <strong>Paid:</strong> ${booking.get('amount_paid', 0)}</p>
                <p><strong>Special Requests:</strong> {booking.get('special_requests', 'None')}</p>
                <p><strong>Cancellation Status:</strong> {booking.get('cancellation_status', 'Not Requested')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Cancellation button for active bookings
            if booking["status"] == "Confirmed" and booking.get("cancellation_status") == "Not Requested":
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write("Need to cancel this booking?")
                with col2:
                    if st.button("Request Cancellation", key=f"cancel_{booking['id']}"):
                        # Create cancellation request
                        cancellation_request = {
                            "booking_id": booking["id"],
                            "guest": booking["guest"],
                            "guest_email": booking["guest_email"],
                            "amount": booking["amount"],
                            "amount_paid": booking.get("amount_paid", 0),
                            "status": "Pending",
                            "request_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "refund_amount": 0,
                            "processing_fee": 0
                        }
                        st.session_state.cancellation_requests.append(cancellation_request)
                        
                        # Update booking status
                        booking["cancellation_status"] = "Requested"
                        
                        # Notify billing officer
                        add_notification(f"Cancellation requested for booking #{booking['id']}", "cancellation", ["Billing Officer"])
                        st.success("Cancellation request submitted! Our billing team will process your request.")
                        st.rerun()
                st.markdown("---")
    
    # Completed bookings (historical records)
    if completed_bookings:
        st.markdown("#### Past Bookings")
        for booking in completed_bookings:
            st.markdown(f"""
            <div class="card">
                <h4>Completed Booking #{booking['id']} - {booking['room_type']}</h4>
                <p><strong>Dates:</strong> {booking['check_in']} to {booking['check_out']}</p>
                <p><strong>Status:</strong> {booking['status']} | <strong>Payment:</strong> {booking.get('payment_status', 'Completed')}</p>
                <p><strong>Amount Paid:</strong> ${booking.get('amount_paid', booking['amount'])}</p>
                <p><strong>Room Number:</strong> {booking.get('room_number', 'Not assigned')}</p>
                <p><em>This booking has been completed. Thank you for staying with us!</em></p>
            </div>
            """, unsafe_allow_html=True)

def show_guest_service_requests():
    st.markdown('<div class="sub-header">🛎️ Service Requests</div>', unsafe_allow_html=True)
    
    service_type = st.selectbox("Service Type", 
                               ["Housekeeping", "Maintenance", "Event & Concierge", "Meeting"])
    
    col1, col2 = st.columns(2)
    with col1:
        urgency = st.select_slider("Urgency Level", ["Low", "Medium", "High", "Critical"])
        room_number = st.text_input("Your Room Number")
    
    with col2:
        preferred_time = st.time_input("Preferred Service Time")
        contact_method = st.selectbox("Contact Method", ["Phone", "Room Visit", "No Contact"])
    
    service_details = st.text_area("Service Details Description")
    
    if st.button("📨 Submit Service Request", use_container_width=True):
        request_id = f"SR{len(st.session_state.service_requests) + 1:03d}"
        new_request = {
            "id": request_id,
            "guest": st.session_state.current_user['name'],
            "room": room_number,
            "type": service_type,
            "urgency": urgency,
            "details": service_details,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.service_requests.append(new_request)
        
        # Notify relevant staff
        if service_type == "Housekeeping":
            add_notification(f"New housekeeping request from Room {room_number}", "service", ["Housekeeping Staff"])
        elif service_type == "Maintenance":
            add_notification(f"New maintenance request from Room {room_number}", "service", ["Maintenance Staff"])
        elif service_type == "Room Service":
            add_notification(f"New room service request from Room {room_number}", "service", ["Catering Staff"])
        elif service_type in ["Concierge", "Transportation"]:
            add_notification(f"New {service_type} request from Room {room_number}", "service", ["Event & Concierge Staff"])
        else:
            add_notification(f"New {service_type} request from Room {room_number}", "service", ["Front Desk Officer"])
        
        st.success("Service request submitted! Our staff will attend to it shortly.")

def show_guest_profile_management():
    st.markdown('<div class="sub-header">👤 Profile Management</div>', unsafe_allow_html=True)
    
    # Find current guest in registered users
    current_email = st.session_state.current_user['email']
    guest_profile = None
    
    for user in st.session_state.registered_users:
        if user["email"] == current_email and user["role"] == "Guest":
            guest_profile = user
            break
    
    if not guest_profile:
        st.error("Profile not found.")
        return
    
    with st.form("profile_management_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name *", value=guest_profile.get("name", ""))
            phone = st.text_input("Phone Number *", value=guest_profile.get("phone", ""))
            id_type = st.selectbox("ID Type *", ["Passport", "Driver's License", "National ID"], 
                                 index=["Passport", "Driver's License", "National ID"].index(guest_profile.get("id_type", "Passport")))
        
        with col2:
            id_number = st.text_input("ID Number *", value=guest_profile.get("id_number", ""))
            address = st.text_area("Home Address *", value=guest_profile.get("address", ""))
            emergency_contact = st.text_input("Emergency Contact", value=guest_profile.get("emergency_contact", ""))
            preferred_payment = st.selectbox("Preferred Payment Method", 
                                           ["Credit Card", "Debit Card", "Online Banking", "E-Wallet", "Cash"],
                                           index=["Credit Card", "Debit Card", "Online Banking", "E-Wallet", "Cash"].index(guest_profile.get("preferred_payment", "Credit Card")))
        
        # Password change section
        st.markdown("#### Change Password")
        col1, col2 = st.columns(2)
        with col1:
            new_password = st.text_input("New Password", type="password", placeholder="Leave blank to keep current")
        with col2:
            confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("💾 Update Profile")
        
        if submitted:
            # Validation
            if not all([full_name, phone, id_type, id_number, address]):
                st.error("Please fill in all required fields (*)")
            elif new_password and new_password != confirm_password:
                st.error("New passwords do not match!")
            elif new_password and len(new_password) < 8:
                st.error("Password must be at least 8 characters long")
            else:
                # Update profile
                guest_profile.update({
                    "name": full_name,
                    "phone": phone,
                    "id_type": id_type,
                    "id_number": id_number,
                    "address": address,
                    "emergency_contact": emergency_contact,
                    "preferred_payment": preferred_payment
                })
                
                # Update password if provided
                if new_password:
                    guest_profile["password"] = new_password
                
                # Update current user name in session
                st.session_state.current_user['name'] = full_name
                
                st.success("✅ Profile updated successfully!")


def show_guest_profile_management():
    st.markdown('<div class="sub-header">👤 Profile Management</div>', unsafe_allow_html=True)
    
    # Find current guest in registered users
    current_email = st.session_state.current_user['email']
    guest_profile = None
    
    for user in st.session_state.registered_users:
        if user["email"] == current_email and user["role"] == "Guest":
            guest_profile = user
            break
    
    if not guest_profile:
        st.error("Profile not found.")
        return
    
    with st.form("profile_management_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name *", value=guest_profile.get("name", ""))
            phone = st.text_input("Phone Number *", value=guest_profile.get("phone", ""))
            id_type = st.selectbox("ID Type *", ["Passport", "Driver's License", "National ID"], 
                                 index=["Passport", "Driver's License", "National ID"].index(guest_profile.get("id_type", "Passport")))
        
        with col2:
            id_number = st.text_input("ID Number *", value=guest_profile.get("id_number", ""))
            address = st.text_area("Home Address *", value=guest_profile.get("address", ""))
            emergency_contact = st.text_input("Emergency Contact", value=guest_profile.get("emergency_contact", ""))
            preferred_payment = st.selectbox("Preferred Payment Method", 
                                           ["Credit Card", "Debit Card", "Online Banking", "E-Wallet", "Cash"],
                                           index=["Credit Card", "Debit Card", "Online Banking", "E-Wallet", "Cash"].index(guest_profile.get("preferred_payment", "Credit Card")))
        
        # Password change section
        st.markdown("#### Change Password")
        col1, col2 = st.columns(2)
        with col1:
            new_password = st.text_input("New Password", type="password", placeholder="Leave blank to keep current")
        with col2:
            confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("💾 Update Profile")
        
        if submitted:
            # Validation
            if not all([full_name, phone, id_type, id_number, address]):
                st.error("Please fill in all required fields (*)")
            elif new_password and new_password != confirm_password:
                st.error("New passwords do not match!")
            elif new_password and len(new_password) < 8:
                st.error("Password must be at least 8 characters long")
            else:
                # Update profile
                guest_profile.update({
                    "name": full_name,
                    "phone": phone,
                    "id_type": id_type,
                    "id_number": id_number,
                    "address": address,
                    "emergency_contact": emergency_contact,
                    "preferred_payment": preferred_payment
                })
                
                # Update password if provided
                if new_password:
                    guest_profile["password"] = new_password
                
                # Update current user name in session
                st.session_state.current_user['name'] = full_name
                
                st.success("✅ Profile updated successfully!")
# Add these NEW FUNCTIONS after show_guest_profile_management()


def to_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()

def show_room_availability_for_guest(check_in, check_out, room_type):
    """Show available rooms of specified type for the selected dates"""

    ci = to_date(check_in)
    co = to_date(check_out)

    # Rooms of selected type
    rooms = [
        room for room in st.session_state.rooms 
        if room["type"] == room_type
    ]

    # Find rooms with date conflicts
    booked_room_numbers = set()

    for booking in st.session_state.bookings:
        if booking["room_type"] == room_type and booking["status"] == "Confirmed":
            bci = to_date(booking["check_in"])
            bco = to_date(booking["check_out"])

            # Overlapping period?
            if not (co <= bci or ci >= bco):
                booked_room_numbers.add(booking["room_number"])

    # Filter rooms NOT conflicting
    available_rooms = [
        room for room in rooms if room["number"] not in booked_room_numbers
    ]

    if available_rooms:
        st.success(f"✅ {len(available_rooms)} {room_type} room(s) available for your dates")
        return True
    else:
        st.error(f"❌ No {room_type} rooms available for your selected dates")
        return False

def assign_room_automatically(room_type, check_in, check_out):
    """Automatically assign an available room of the specified type"""

    ci = to_date(check_in)
    co = to_date(check_out)

    for room in st.session_state.rooms:
        if room["type"] == room_type:

            # Check if room has booking conflicts
            conflict = False
            for booking in st.session_state.bookings:
                if booking["room_number"] == room["number"] and booking["status"] == "Confirmed":
                    bci = to_date(booking["check_in"])
                    bco = to_date(booking["check_out"])

                    if not (co <= bci or ci >= bco):  # overlap
                        conflict = True
                        break

            if not conflict:
                return room["number"]

    return None

def show_guest_notifications():
    """Show notifications specifically for the current guest"""
    st.markdown('<div class="sub-header">🔔 My Notifications</div>', unsafe_allow_html=True)
    
    guest_notifications = get_user_notifications()
    
    if not guest_notifications:
        st.info("No new notifications.")
        return
    
    for notification in guest_notifications:
        status_color = {
            "payment_reminder": "warning-card",
            "booking": "success-card", 
            "payment": "warning-card",
            "cancellation": "critical-card"
        }.get(notification['category'], 'card')
        
        st.markdown(f"""
        <div class="card {status_color}">
            <h5>🔔 {notification['message']}</h5>
            <p><small>{notification['timestamp']}</small></p>
        </div>
        """, unsafe_allow_html=True)
                
def show_guest_reviews():
    st.markdown('<div class="sub-header">⭐ Share Your Experience</div>', unsafe_allow_html=True)
    
    # Check if user has completed stays to review
    completed_stays = [b for b in st.session_state.completed_bookings 
                      if b["guest_email"] == st.session_state.current_user['email']]
    
    if not completed_stays:
        st.info("You need to complete a stay before you can leave a review.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Select which stay to review
        stay_options = [f"{b['id']} - {b['room_type']} ({b['check_in']})" for b in completed_stays]
        selected_stay = st.selectbox("Select Your Stay to Review", stay_options)
        booking_id = selected_stay.split(" - ")[0]
        
        selected_booking = next(b for b in completed_stays if b['id'] == booking_id)
        room_number = st.text_input("Room Number", value=selected_booking.get('room_number', ''))
        
        st.markdown("#### Rate Your Experience")
        overall_rating = st.slider("Overall Rating ★", 1, 5, 5)
        cleanliness = st.slider("Cleanliness ★", 1, 5, 5)
        service = st.slider("Service Quality ★", 1, 5, 5)
        comfort = st.slider("Room Comfort ★", 1, 5, 5)
        value = st.slider("Value for Money ★", 1, 5, 5)
    
    with col2:
        avg_rating = (overall_rating + cleanliness + service + comfort + value) / 5
        st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
        
        # Recommendation
        would_recommend = st.radio("Would you recommend us?", ["Yes", "No"], horizontal=True)
    
    # Enhanced review categories
    st.markdown("#### Detailed Feedback")
    col1, col2 = st.columns(2)
    with col1:
        staff_friendliness = st.select_slider("Staff Friendliness", ["Poor", "Fair", "Good", "Very Good", "Excellent"])
        location_rating = st.select_slider("Location & Accessibility", ["Poor", "Fair", "Good", "Very Good", "Excellent"])
    with col2:
        amenities_rating = st.select_slider("Amenities & Facilities", ["Poor", "Fair", "Good", "Very Good", "Excellent"])
        breakfast_quality = st.select_slider("Food & Breakfast", ["Poor", "Fair", "Good", "Very Good", "Excellent"])
    
    review_text = st.text_area("Detailed Review Comments", placeholder="Share your experience in detail...")
    
    # Travel purpose and visitor type
    col1, col2 = st.columns(2)
    with col1:
        travel_purpose = st.selectbox("Purpose of Travel", ["Business", "Leisure", "Family Vacation", "Romantic Getaway", "Other"])
    with col2:
        visitor_type = st.selectbox("You traveled as", ["Solo Traveler", "Couple", "Family with Children", "Group of Friends", "Business Colleagues"])
    
    if st.button("📤 Submit Review", use_container_width=True):
        review = {
            "guest": st.session_state.current_user['name'],
            "booking_id": booking_id,
            "room": room_number,
            "ratings": {
                "overall": overall_rating,
                "cleanliness": cleanliness,
                "service": service,
                "comfort": comfort,
                "value": value
            },
            "categories": {
                "staff_friendliness": staff_friendliness,
                "location": location_rating,
                "amenities": amenities_rating,
                "food_quality": breakfast_quality
            },
            "recommendation": would_recommend,
            "travel_purpose": travel_purpose,
            "visitor_type": visitor_type,
            "comments": review_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.reviews.append(review)
        add_notification(f"New review submitted by {st.session_state.current_user['name']}", "review", ["Hotel Manager"])
        st.success("Thank you for your valuable feedback! Your review helps us improve our services.")

def show_recent_reviews():
    st.markdown('<div class="sub-header">📝 Recent Guest Reviews</div>', unsafe_allow_html=True)
    
    if not st.session_state.reviews:
        st.info("No reviews available yet.")
        return
    
    # Display recent reviews (last 10)
    recent_reviews = st.session_state.reviews[-10:][::-1]
    
    for review in recent_reviews:
        avg_rating = sum(review['ratings'].values()) / len(review['ratings'])
        
        # Create star rating display
        stars = "★" * int(avg_rating) + "☆" * (5 - int(avg_rating))
        
        st.markdown(f"""
        <div class="card">
            <h4>{review['guest']} - Room {review['room']}</h4>
            <p><strong>Rating:</strong> {stars} ({avg_rating:.1f}/5)</p>
            <p><strong>Comments:</strong> {review['comments']}</p>
            <p><strong>Travel Purpose:</strong> {review.get('travel_purpose', 'Not specified')} | 
            <strong>Visitor Type:</strong> {review.get('visitor_type', 'Not specified')}</p>
            <p><strong>Would Recommend:</strong> {review.get('recommendation', 'Not specified')}</p>
            <p><small>Posted: {review['timestamp']}</small></p>
        </div>
        """, unsafe_allow_html=True)

# ==================== VENDOR PORTAL ====================
def show_vendor_portal():
    st.markdown('<div class="main-header">🤝 Vendor Portal</div>', unsafe_allow_html=True)
    
    # Find vendor details - FIXED: Use contact field instead of email
    vendor_email = st.session_state.current_user['email']
    vendor_info = None
    
    for vendor in st.session_state.vendors:
        # FIX: Check both contact and email fields
        if vendor.get("contact") == vendor_email or vendor.get("email") == vendor_email:
            vendor_info = vendor
            break
    
    if vendor_info:
        if vendor_info["status"] == "Approved":
            tab1, tab2, tab3, tab4 = st.tabs(["🏢 Dashboard", "💰 Statements & Payments", "📊 Performance", "📄 Generate Report"])
            
            with tab1:
                show_vendor_dashboard(vendor_info)
            with tab2:
                show_vendor_statements(vendor_info)
            with tab3:
                show_vendor_performance(vendor_info)
            with tab4:
                show_vendor_report_generator(vendor_info)
        else:
            st.warning("⏳ Your vendor application is pending approval. You will gain access to the vendor portal once approved.")
            st.info("Please check back later or contact the hotel management for updates.")
    else:
        st.error("Vendor account not found or not approved. Please contact support.")

def show_vendor_dashboard(vendor_info):
    st.markdown('<div class="sub-header">🏢 Vendor Dashboard</div>', unsafe_allow_html=True)
    
    # Vendor overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Services Completed", vendor_info["services_completed"])
    with col2:
        st.metric("Monthly Earnings", f"${vendor_info['monthly_earnings']:,.2f}")
    with col3:
        st.metric("Service Fee", f"{vendor_info['service_fee']}%")
    with col4:
        st.metric("Status", vendor_info["status"])
    
    st.markdown(f"""
    <div class="card success-card">
        <h4>Welcome, {vendor_info['name']}</h4>
        <p><strong>Service Type:</strong> {vendor_info['service']}</p>
        <p><strong>Contact:</strong> {vendor_info['contact']} | {vendor_info.get('phone', 'N/A')}</p>
        <p><strong>Registered Since:</strong> {vendor_info['registration_date']}</p>
        <p><strong>Service Description:</strong> {vendor_info.get('description', 'No description provided')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Recent services
    st.markdown("#### Recent Service Engagements")
    vendor_services = [s for s in st.session_state.vendor_services if s["vendor_name"] == vendor_info["name"]]
    
    if vendor_services:
        recent_services = vendor_services[-5:][::-1]
        for service in recent_services:
            status_color = "success-card" if service["status"] == "Completed" else "warning-card"
            st.markdown(f"""
            <div class="card {status_color}">
                <h5>Service #{service['id']}</h5>
                <p><strong>Type:</strong> {service['service_type']}</p>
                <p><strong>Location:</strong> {service.get('location', 'N/A')}</p>
                <p><strong>Amount:</strong> ${service['amount']:.2f}</p>
                <p><strong>Service Fee ({vendor_info['service_fee']}%):</strong> ${service['service_fee']:.2f}</p>
                <p><strong>Net Earnings:</strong> ${service['amount'] - service['service_fee']:.2f}</p>
                <p><strong>Status:</strong> {service['status']} | <strong>Date:</strong> {service['date']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent service engagements.")

def show_vendor_statements(vendor_info):
    st.markdown('<div class="sub-header">💰 Monthly Statements</div>', unsafe_allow_html=True)
    
    # Generate current month statement
    current_month = datetime.now().strftime("%Y-%m")
    vendor_services = [s for s in st.session_state.vendor_services 
                      if s["vendor_name"] == vendor_info["name"] 
                      and s["date"].startswith(current_month)
                      and s["status"] == "Completed"]
    
    total_earnings = sum(s["amount"] for s in vendor_services)
    total_service_fees = sum(s["service_fee"] for s in vendor_services)
    net_amount = total_earnings - total_service_fees
    
    st.markdown(f"""
    <div class="card">
        <h4>Statement for {current_month}</h4>
        <p><strong>Total Services Completed:</strong> {len(vendor_services)}</p>
        <p><strong>Gross Earnings:</strong> ${total_earnings:,.2f}</p>
        <p><strong>Service Fees ({vendor_info['service_fee']}%):</strong> ${total_service_fees:,.2f}</p>
        <hr>
        <h5><strong>Net Payment Due:</strong> ${net_amount:,.2f}</h5>
    </div>
    """, unsafe_allow_html=True)
    
    # Payment status
    st.markdown("#### Payment Status")
    paid_statements = [s for s in st.session_state.vendor_statements 
                      if s["vendor_name"] == vendor_info["name"] 
                      and s["month"] == current_month]
    
    if paid_statements:
        statement = paid_statements[0]
        st.markdown(f"""
        <div class="card success-card">
            <h5>Payment Processed</h5>
            <p><strong>Payment Date:</strong> {statement['payment_date']}</p>
            <p><strong>Amount Paid:</strong> ${statement['amount']:,.2f}</p>
            <p><strong>Payment Method:</strong> {statement['payment_method']}</p>
            <p><strong>Reference:</strong> {statement['id']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Payment for {current_month} will be processed by the end of the month.")
    
    # Previous statements
    st.markdown("#### Payment History")
    all_statements = [s for s in st.session_state.vendor_statements 
                     if s["vendor_name"] == vendor_info["name"]]
    
    if all_statements:
        for statement in all_statements[-5:][::-1]:
            st.markdown(f"""
            <div class="card">
                <p><strong>{statement['month']}:</strong> ${statement['amount']:,.2f} - {statement['payment_date']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No previous payment history.")

def show_vendor_performance(vendor_info):
    st.markdown('<div class="sub-header">📊 Performance Analytics</div>', unsafe_allow_html=True)
    
    vendor_services = [s for s in st.session_state.vendor_services 
                      if s["vendor_name"] == vendor_info["name"]]
    
    if vendor_services:
        # Monthly earnings chart
        monthly_data = {}
        for service in vendor_services:
            month = service["date"][:7]  # YYYY-MM
            if month not in monthly_data:
                monthly_data[month] = 0
            monthly_data[month] += service["amount"]
        
        if monthly_data:
            months = list(monthly_data.keys())
            earnings = list(monthly_data.values())
            
            fig = px.bar(x=months, y=earnings, 
                        title="Monthly Earnings Trend",
                        labels={"x": "Month", "y": "Earnings ($)"})
            st.plotly_chart(fig, use_container_width=True)
        
        # Service type distribution
        service_types = {}
        for service in vendor_services:
            service_type = service["service_type"]
            if service_type not in service_types:
                service_types[service_type] = 0
            service_types[service_type] += 1
        
        if service_types:
            fig = px.pie(values=list(service_types.values()), 
                        names=list(service_types.keys()),
                        title="Service Type Distribution")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No performance data available yet.")

def show_vendor_report_generator(vendor_info):
    st.markdown('<div class="sub-header">📄 Generate Financial Report</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        report_type = st.selectbox("Report Type", ["Detailed Earnings", "Service Summary", "Payment History"])
    
    with col2:
        end_date = st.date_input("End Date", datetime.now())
        format_type = st.selectbox("Download Format", ["CSV", "PDF"])
    
    if st.button("📥 Generate Report", use_container_width=True):
        # Filter vendor services for the date range
        vendor_services = [s for s in st.session_state.vendor_services 
                          if s["vendor_name"] == vendor_info["name"]
                          and datetime.strptime(s["date"], "%Y-%m-%d").date() >= start_date
                          and datetime.strptime(s["date"], "%Y-%m-%d").date() <= end_date]
        
        if vendor_services:
            # Create report data
            report_data = []
            for service in vendor_services:
                report_data.append({
                    "Service ID": service["id"],
                    "Date": service["date"],
                    "Service Type": service["service_type"],
                    "Location": service.get("location", "N/A"),
                    "Amount": service["amount"],
                    "Service Fee": service["service_fee"],
                    "Net Earnings": service["amount"] - service["service_fee"],
                    "Status": service["status"]
                })
            
            df = pd.DataFrame(report_data)
            
            # Calculate summary
            total_services = len(vendor_services)
            total_earnings = sum(s["amount"] for s in vendor_services)
            total_fees = sum(s["service_fee"] for s in vendor_services)
            net_earnings = total_earnings - total_fees
            
            st.markdown(f"""
            <div class="card success-card">
                <h4>Report Summary</h4>
                <p><strong>Period:</strong> {start_date} to {end_date}</p>
                <p><strong>Total Services:</strong> {total_services}</p>
                <p><strong>Total Earnings:</strong> ${total_earnings:,.2f}</p>
                <p><strong>Total Fees:</strong> ${total_fees:,.2f}</p>
                <p><strong>Net Earnings:</strong> ${net_earnings:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display data table
            st.dataframe(df, use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label=f"⬇️ Download {report_type} Report (CSV)",
                data=csv,
                file_name=f"{vendor_info['name']}_report_{start_date}_to_{end_date}.csv",
                mime="text/csv",
            )
        else:
            st.info("No services found for the selected date range.")

# ==================== BILLING PORTAL ====================
def show_billing_portal():
    st.markdown('<div class="main-header">💰 Billing & Invoicing Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Pending Invoices", "💰 Payment Processing", "📝 Cancellation Refunds", "🤝 Vendor Payments", "📊 Vendor Payment History", "📅 Calendar"])
    
    with tab1:
        show_pending_invoices()
    with tab2:
        show_payment_processing()
    with tab3:
        show_cancellation_refunds()
    with tab4:
        show_vendor_payments()
    with tab5:
        show_vendor_payment_history()
    with tab6:
        show_calendar()
        
def show_pending_invoices():
    st.markdown('<div class="sub-header">📋 Outstanding Invoices</div>', unsafe_allow_html=True)
    
    pending_invoices = [inv for inv in st.session_state.invoices if inv["status"] == "Pending"]
    
    if not pending_invoices:
        st.info("No pending invoices.")
        return
    
    for invoice in pending_invoices:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])  # ADDED 4th COLUMN
        with col1:
            st.markdown(f"""
            <div class="card warning-card">
                <h4>Invoice #{invoice['id']}</h4>
                <p><strong>Booking ID:</strong> {invoice['booking_id']}</p>
                <p><strong>Guest:</strong> {invoice['guest']}</p>
                <p><strong>Amount:</strong> ${invoice['amount']}</p>
                <p><strong>Due Date:</strong> {invoice['due_date']}</p>
                <p><strong>Payment Method:</strong> {invoice['payment_method']}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("✅ Mark Paid", key=f"paid_{invoice['id']}"):
                invoice["status"] = "Paid"
        # Update corresponding booking
            for booking in st.session_state.bookings:
                if booking["id"] == invoice["booking_id"]:
                    booking["payment_status"] = "Paid"
                    booking["amount_paid"] = invoice["amount"]
                    break
        
        # ADD LOG ENTRY:
        log_activity(st.session_state.current_user['name'], "Payment Processed", 
                    f"Invoice {invoice['id']} for ${invoice['amount']} marked as paid")
        
        add_notification(f"Invoice {invoice['id']} marked as paid", "payment")
        st.success(f"Invoice {invoice['id']} marked as paid!")
        st.rerun()
        with col3:
            guest_email = None
            for booking in st.session_state.bookings:
                if booking["id"] == invoice["booking_id"]:
                    guest_email = booking["guest_email"]
                    break
            
            if st.button("📧 Send Reminder", key=f"remind_{invoice['id']}"):
                if guest_email:
                    add_notification(
                        f"Payment reminder for invoice {invoice['id']}. Amount: ${invoice['amount']} due by {invoice['due_date']}",
                        "payment_reminder", 
                        target_roles=["Guest"],
                        target_user=guest_email
                    )
                    st.success(f"Payment reminder sent to guest for invoice {invoice['id']}!")
                else:
                    st.error("Could not find guest email for this invoice.")
        
        # NEW: Update/Remove button for cancelled invoices
        with col4:
            # Check if booking is cancelled
            booking_cancelled = any(
                b["id"] == invoice["booking_id"] and b.get("cancellation_status") in ["Requested", "Processed", "Auto-cancelled"]
                for b in st.session_state.bookings
            )
            
            if booking_cancelled:
                if st.button("🗑️ Remove", key=f"remove_{invoice['id']}"):
                    invoice["status"] = "Cancelled"
                    st.success(f"Invoice {invoice['id']} removed (booking cancelled)!")
                    st.rerun()

def show_payment_processing():
    st.markdown('<div class="sub-header">💰 Payment Processing</div>', unsafe_allow_html=True)
    
    # Show recent payments
    paid_invoices = [inv for inv in st.session_state.invoices if inv["status"] == "Paid"][-10:][::-1]
    
    if not paid_invoices:
        st.info("No recent payments.")
        return
    
    for invoice in paid_invoices:
        st.markdown(f"""
        <div class="card success-card">
            <h5>Payment Processed - #{invoice['id']}</h5>
            <p><strong>Booking:</strong> {invoice['booking_id']} | <strong>Guest:</strong> {invoice['guest']}</p>
            <p><strong>Amount:</strong> ${invoice['amount']} | <strong>Method:</strong> {invoice['payment_method']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_cancellation_refunds():
    st.markdown('<div class="sub-header">📝 Cancellation & Refund Requests</div>', unsafe_allow_html=True)
    
    pending_requests = [r for r in st.session_state.cancellation_requests if r["status"] == "Pending"]
    
    if not pending_requests:
        st.info("No pending cancellation requests.")
        return
    
    for request in pending_requests:
        # Find the booking details
        booking = next((b for b in st.session_state.bookings if b["id"] == request["booking_id"]), None)
        
        if booking:
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown(f"""
                <div class="card warning-card">
                    <h4>Cancellation Request - {request['booking_id']}</h4>
                    <p><strong>Guest:</strong> {request['guest']}</p>
                    <p><strong>Booking Amount:</strong> ${request['amount']}</p>
                    <p><strong>Amount Paid:</strong> ${request['amount_paid']}</p>
                    <p><strong>Request Date:</strong> {request['request_date']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### Refund Calculation")
                
                # Calculate refund based on cancellation timing
                check_in_date = datetime.strptime(booking["check_in"], "%Y-%m-%d")
                days_until_checkin = (check_in_date - datetime.now()).days
                
                if days_until_checkin >= 2:
                    refund_percentage = 0.5  # 50% refund for 48+ hours notice
                    refund_reason = "Standard cancellation (48+ hours notice)"
                elif request["amount_paid"] == 0:
                    refund_percentage = 1.0  # Full refund if not paid
                    refund_reason = "Free cancellation (not paid)"
                else:
                    refund_percentage = 0.0  # No refund for late cancellation
                    refund_reason = "Late cancellation (no refund)"
                
                refund_amount = request["amount_paid"] * refund_percentage
                processing_fee = refund_amount * 0.02  # 2% processing fee
                net_refund = refund_amount - processing_fee
                
                st.write(f"**Refund Reason:** {refund_reason}")
                st.write(f"**Refund Amount:** ${refund_amount:.2f}")
                st.write(f"**Processing Fee (2%):** ${processing_fee:.2f}")
                st.write(f"**Net Refund:** ${net_refund:.2f}")
                
                # Update request with calculated values
                request["refund_amount"] = net_refund
                request["processing_fee"] = processing_fee
                request["refund_reason"] = refund_reason
                
                if st.button("✅ Process Refund", key=f"refund_{request['booking_id']}"):
                    # Process refund
                    request["status"] = "Processed"
                    request["processed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    request["processed_by"] = st.session_state.current_user['name']
                    
                    # Update booking status
                    booking["status"] = "Cancelled"
                    booking["cancellation_status"] = "Processed"
                    
                    # ADD LOG ENTRY HERE:
                    log_activity(st.session_state.current_user['name'], "Booking Cancelled", 
                            f"Booking {request['booking_id']} cancelled - Refund: ${net_refund}")
                    
                    # Create refund record
                    refund_request = {
                        "booking_id": request["booking_id"],
                        "guest": request["guest"],
                        "original_amount": request["amount_paid"],
                        "refund_amount": net_refund,
                        "processing_fee": processing_fee,
                        "status": "Completed",
                        "processed_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.refund_requests.append(refund_request)
                    
                    add_notification(f"Refund processed for booking #{request['booking_id']} - ${net_refund:.2f}", "refund")
                    st.success(f"Refund of ${net_refund:.2f} processed successfully!")
                    st.rerun()

            st.markdown("---")

def show_vendor_payments():
    st.markdown('<div class="sub-header">🤝 Vendor Payment Processing</div>', unsafe_allow_html=True)
    
    # Generate monthly vendor statements
    current_month = datetime.now().strftime("%Y-%m")
    
    st.markdown(f"#### Monthly Vendor Payments - {current_month}")
    
    approved_vendors = [v for v in st.session_state.vendors if v["status"] == "Approved"]
    
    for vendor in approved_vendors:
        # Calculate monthly earnings
        vendor_services = [s for s in st.session_state.vendor_services 
                          if s["vendor_name"] == vendor["name"] 
                          and s["date"].startswith(current_month)
                          and s["status"] == "Completed"]
        
        total_earnings = sum(s["amount"] for s in vendor_services)
        total_service_fees = sum(s["service_fee"] for s in vendor_services)
        net_payment = total_earnings - total_service_fees
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"""
            <div class="card">
                <h5>{vendor['name']} - {vendor['service']}</h5>
                <p><strong>Services Completed:</strong> {len(vendor_services)}</p>
                <p><strong>Gross Earnings:</strong> ${total_earnings:,.2f}</p>
                <p><strong>Service Fees ({vendor['service_fee']}%):</strong> ${total_service_fees:,.2f}</p>
                <p><strong>Net Payment Due:</strong> ${net_payment:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if net_payment > 0:
                if st.button("💰 Process Payment", key=f"pay_{vendor['name']}"):
                    # Create vendor statement
                    statement_id = f"VS{len(st.session_state.vendor_statements) + 1:03d}"
                    new_statement = {
                        "id": statement_id,
                        "vendor_name": vendor["name"],
                        "month": current_month,
                        "amount": net_payment,
                        "services_count": len(vendor_services),
                        "service_fee_total": total_service_fees,
                        "payment_date": datetime.now().strftime("%Y-%m-%d"),
                        "payment_method": "Bank Transfer",
                        "status": "Paid"
                    }
                    st.session_state.vendor_statements.append(new_statement)
                    
                    # Update vendor earnings
                    vendor["monthly_earnings"] = net_payment
                    vendor["services_completed"] += len(vendor_services)
                    log_activity(st.session_state.current_user['name'], "Vendor Payment", 
                                f"Paid ${net_payment:,.2f} to {vendor['name']} for {current_month}")
                    add_notification(f"Payment processed for {vendor['name']} - ${net_payment:,.2f}", "vendor_payment")
                    st.success(f"Payment of ${net_payment:,.2f} processed for {vendor['name']}!")
                    st.rerun()
        
        with col3:
            # Show payment status
            existing_statement = next((s for s in st.session_state.vendor_statements 
                                     if s["vendor_name"] == vendor["name"] and s["month"] == current_month), None)
            if existing_statement:
                st.success("✅ Paid")
            elif net_payment > 0:
                st.warning("⏳ Pending")
            else:
                st.info("💤 No Payment")
        
        st.markdown("---")


def show_vendor_payment_history():
    st.markdown('<div class="sub-header">📊 Vendor Payment History</div>', unsafe_allow_html=True)
    
    # Filter for ABC Laundry payments for 2025
    abc_laundry_payments = [s for s in st.session_state.vendor_statements 
                           if s["vendor_name"] == "ABC Laundry" 
                           and s["month"] in ["2025-10", "2025-11"]]  # UPDATED TO 2025
    
    if abc_laundry_payments:
        st.markdown("#### ABC Laundry - October & November 2025 Payments")  # UPDATED
        
        # Create a DataFrame for better display
        payment_data = []
        for payment in abc_laundry_payments:
            payment_data.append({
                "Month": payment["month"],
                "Amount Paid": f"${payment['amount']:,.2f}",
                "Services Count": payment["services_count"],
                "Service Fees": f"${payment['service_fee_total']:,.2f}",
                "Payment Date": payment["payment_date"],
                "Payment Method": payment["payment_method"],
                "Status": payment["status"]
            })
        
        df = pd.DataFrame(payment_data)
        st.dataframe(df, use_container_width=True)
        
        # Calculate totals
        total_paid = sum(payment["amount"] for payment in abc_laundry_payments)
        total_services = sum(payment["services_count"] for payment in abc_laundry_payments)
        total_fees = sum(payment["service_fee_total"] for payment in abc_laundry_payments)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Paid to ABC Laundry", f"${total_paid:,.2f}")
        with col2:
            st.metric("Total Services", total_services)
        with col3:
            st.metric("Total Service Fees", f"${total_fees:,.2f}")
        
        # Payment trend chart
        months = [p["month"] for p in abc_laundry_payments]
        amounts = [p["amount"] for p in abc_laundry_payments]
        
        fig = px.bar(x=months, y=amounts, 
                    title="ABC Laundry Payment Trend - Oct & Nov 2025",  # UPDATED
                    labels={"x": "Month", "y": "Amount Paid ($)"},
                    color=months)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No payment history found for ABC Laundry in October and November 2025.")

# ==================== MANAGER PORTAL ====================
def show_manager_portal():
    st.markdown('<div class="main-header">👨‍💼 Hotel Manager Dashboard</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "📈 Analytics", "👥 User Management", "👨‍💼 Staff Management", "🤝 Vendor Management", "📊 Reports", 
        "⚙️ Configuration", "📋 Approvals", "💰 Financial Overview", "📊 Staff Performance" , "📅 Calendar","📋 System Logs" ])
    
    with tab1:
        show_manager_analytics()
    with tab2:
        show_user_management()
    with tab3:  
        show_staff_management()
    with tab4:
        show_vendor_management()
    with tab5:
        show_manager_reports()
    with tab6:
        show_system_config()
    with tab7:
        show_approval_system()
    with tab8:
        show_financial_overview()
    with tab9:
        show_staff_performance()
    with tab10:
        show_calendar()
    with tab11:
        show_system_logs()

def show_system_logs():
    st.markdown('<div class="sub-header">📋 System Activity Logs</div>', unsafe_allow_html=True)
    
    if not st.session_state.system_logs:
        st.info("No system logs available.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        log_level = st.selectbox("Filter by Level", ["ALL", "INFO", "WARNING", "ERROR"])
    with col2:
        search_user = st.text_input("Search by User")
    with col3:
        date_filter = st.date_input("Filter by Date")
    
    # Display logs
    filtered_logs = st.session_state.system_logs[::-1]  # Show latest first
    
    if log_level != "ALL":
        filtered_logs = [log for log in filtered_logs if log["level"] == log_level]
    
    if search_user:
        filtered_logs = [log for log in filtered_logs if search_user.lower() in log["user"].lower()]
    
    for log in filtered_logs[:50]:  # Show last 50 logs
        level_color = {
            "INFO": "card",
            "WARNING": "warning-card", 
            "ERROR": "critical-card"
        }.get(log["level"], "card")
        
        st.markdown(f"""
        <div class="card {level_color}">
            <p><strong>{log['timestamp']} | {log['level']} | {log['user']}</strong></p>
            <p><strong>Action:</strong> {log['action']}</p>
            <p><strong>Details:</strong> {log['details']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_staff_management():
    st.markdown('<div class="sub-header">👥 Staff Management</div>', unsafe_allow_html=True)
    
    with st.form("add_staff_form"):
        st.markdown("#### Add New Staff Member")
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name *")
            email = st.text_input("Email Address *")
            phone = st.text_input("Phone Number *")
        
        with col2:
            role = st.selectbox("Staff Role *", 
                               ["Front Desk Officer", "Housekeeping Staff", "Maintenance Staff", 
                                "Billing Officer", "Catering Staff", "Event & Concierge Staff"])
        
        # Password setup
        st.markdown("#### Account Setup")
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input("Initial Password *", type="password", value="staff123")
        with col2:
            confirm_password = st.text_input("Confirm Password *", type="password", value="staff123")
        
        submitted = st.form_submit_button("👨‍💼 Add Staff Member")
        
        if submitted:
            if not all([full_name, email, phone, role, password]):
                st.error("Please fill in all required fields (*)")
            elif password != confirm_password:
                st.error("Passwords do not match!")
            else:
                # Check if email already exists
                existing_user = any(user["email"] == email for user in st.session_state.registered_users)
                if existing_user:
                    st.error("This email is already registered.")
                else:
                    # Add new staff to registered users
                    new_staff = {
                        "email": email,
                        "name": full_name,
                        "role": role,
                        "status": "Active",
                        "registration_date": datetime.now().strftime("%Y-%m-%d"),
                        "phone": phone,
                        "password": password
                    }
                    st.session_state.registered_users.append(new_staff)
                    log_activity(st.session_state.current_user['name'], "New User Registration", 
                            f"New Staff member added: {full_name} as {role} ({email})")
                    add_notification(f"New staff member added: {full_name} ({role})", "staff_added")
                    st.success(f"Staff member {full_name} added successfully! They can now login with email: {email}")
                    
                    
def show_financial_overview():
    st.markdown('<div class="sub-header">💰 Financial Overview</div>', unsafe_allow_html=True)
    
    # Financial metrics with real data
    total_revenue = sum(b["amount"] for b in st.session_state.bookings if b.get("payment_status") == "Paid")
    total_revenue += sum(b["amount"] for b in st.session_state.completed_bookings)
    
    pending_payments = sum(b["amount"] for b in st.session_state.bookings if b.get("payment_status") == "Pending")
    vendor_payments = sum(s["amount"] for s in st.session_state.vendor_statements)
    refunds_processed = sum(r.get("refund_amount", 0) for r in st.session_state.refund_requests)
    
    # Calculate current month revenue
    current_month = datetime.now().strftime("%Y-%m")
    current_month_revenue = sum(b["amount"] for b in st.session_state.bookings 
                               if b.get("payment_status") == "Paid" 
                               and "timestamp" in b 
                               and b["timestamp"].startswith(current_month))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col2:
        st.metric("Current Month Revenue", f"${current_month_revenue:,.0f}")
    with col3:
        st.metric("Vendor Payments", f"${vendor_payments:,.0f}")
    with col4:
        st.metric("Pending Payments", f"${pending_payments:,.0f}")
    
    # Monthly revenue trend with real data
    st.markdown("#### Revenue Trend")
    monthly_revenue = {}
    for booking in st.session_state.bookings + st.session_state.completed_bookings:
        if booking.get("payment_status") == "Paid" and "timestamp" in booking:
            month = booking["timestamp"][:7]  # YYYY-MM
            if month not in monthly_revenue:
                monthly_revenue[month] = 0
            monthly_revenue[month] += booking["amount"]
    
    # Add sample data for previous months if needed
    sample_months = {"2024-09": 12500, "2024-10": 14200, "2024-11": current_month_revenue}
    for month, revenue in sample_months.items():
        if month not in monthly_revenue:
            monthly_revenue[month] = revenue
    
    if monthly_revenue:
        months = list(monthly_revenue.keys())
        revenue = list(monthly_revenue.values())
        
        fig = px.line(x=months, y=revenue, 
                     title="Monthly Revenue Trend",
                     labels={"x": "Month", "y": "Revenue ($)"})
        st.plotly_chart(fig, use_container_width=True)
    
    # Vendor payment breakdown
    st.markdown("#### Vendor Payments Breakdown")
    vendor_payment_data = {}
    for statement in st.session_state.vendor_statements:
        vendor = statement["vendor_name"]
        if vendor not in vendor_payment_data:
            vendor_payment_data[vendor] = 0
        vendor_payment_data[vendor] += statement["amount"]
    
    if vendor_payment_data:
        vendors = list(vendor_payment_data.keys())
        payments = list(vendor_payment_data.values())
        
        fig = px.pie(values=payments, names=vendors, 
                    title="Vendor Payments Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_vendor_management():
    st.markdown('<div class="sub-header">🤝 Vendor Management</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💰 Current Vendor Balances", "📋 Payment History"])
    
    with tab1:
        show_current_vendor_balances()
    with tab2:
        show_vendor_payment_history_manager()

def show_staff_performance():
    st.markdown('<div class="sub-header">📊 Staff Performance</div>', unsafe_allow_html=True)
    
    # Calculate staff performance metrics
    staff_roles = ["Housekeeping Staff", "Maintenance Staff", "Catering Staff", "Event & Concierge Staff"]
    
    performance_data = []
    for role in staff_roles:
        staff_members = [u for u in st.session_state.registered_users if u["role"] == role and u["status"] == "Active"]
        
        for staff in staff_members:
            # Count completed tasks
            completed_tasks = [
                t for t in st.session_state.tasks 
                if t["assigned_to"] == role and t["status"] == "Completed"
            ]
            
            # Calculate average completion time (simulated)
            avg_completion_time = "2.5 hours"  # This would require timestamp tracking
            
            performance_data.append({
                "Name": staff["name"],
                "Role": role,
                "Completed Tasks": len(completed_tasks),
                "Avg Completion Time": avg_completion_time,
                "Performance Score": f"{(min(len(completed_tasks) * 10, 100))}%"
            })
    
    if performance_data:
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True)
        
        # Performance chart
        fig = px.bar(df, x='Name', y='Completed Tasks', color='Role',
                    title='Staff Performance - Completed Tasks')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No staff performance data available.")


def show_current_vendor_balances():
    st.markdown("#### Current Vendor Payables")
    
    approved_vendors = [v for v in st.session_state.vendors if v["status"] == "Approved"]
    
    if not approved_vendors:
        st.info("No approved vendors.")
        return
    
    for vendor in approved_vendors:
        # Calculate current month payable
        current_month = datetime.now().strftime("%Y-%m")
        vendor_services = [s for s in st.session_state.vendor_services 
                          if s["vendor_name"] == vendor["name"] 
                          and s["date"].startswith(current_month)
                          and s["status"] == "Completed"]
        
        total_earnings = sum(s["amount"] for s in vendor_services)
        total_service_fees = sum(s["service_fee"] for s in vendor_services)
        net_payment = total_earnings - total_service_fees
        
        # Check if already paid this month
        existing_statement = next((s for s in st.session_state.vendor_statements 
                                 if s["vendor_name"] == vendor["name"] and s["month"] == current_month), None)
        
        status_color = "warning-card" if not existing_statement and net_payment > 0 else "success-card" if existing_statement else "card"
        
        st.markdown(f"""
        <div class="card {status_color}">
            <h4>{vendor['name']} - {vendor['service']}</h4>
            <p><strong>Contact:</strong> {vendor['contact']} | <strong>Phone:</strong> {vendor.get('phone', 'N/A')}</p>
            <p><strong>Service Fee:</strong> {vendor['service_fee']}%</p>
            <p><strong>Current Month Services:</strong> {len(vendor_services)}</p>
            <p><strong>Gross Earnings:</strong> ${total_earnings:,.2f}</p>
            <p><strong>Service Fees:</strong> ${total_service_fees:,.2f}</p>
            <p><strong>Net Payment Due:</strong> ${net_payment:,.2f}</p>
            <p><strong>Payment Status:</strong> {"✅ Paid" if existing_statement else "⏳ Pending" if net_payment > 0 else "💤 No Payment Due"}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick payment action
        if net_payment > 0 and not existing_statement:
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button(f"💰 Pay Now", key=f"pay_{vendor['name']}"):
                    # Create vendor statement
                    statement_id = f"VS{len(st.session_state.vendor_statements) + 1:03d}"
                    new_statement = {
                        "id": statement_id,
                        "vendor_name": vendor["name"],
                        "month": current_month,
                        "amount": net_payment,
                        "services_count": len(vendor_services),
                        "service_fee_total": total_service_fees,
                        "payment_date": datetime.now().strftime("%Y-%m-%d"),
                        "payment_method": "Bank Transfer",
                        "status": "Paid"
                    }
                    st.session_state.vendor_statements.append(new_statement)
                    
                    # Update vendor earnings
                    vendor["monthly_earnings"] = net_payment
                    vendor["services_completed"] += len(vendor_services)
                    
                    add_notification(f"Payment processed for {vendor['name']} - ${net_payment:,.2f}", "vendor_payment")
                    st.success(f"Payment of ${net_payment:,.2f} processed for {vendor['name']}!")
                    st.rerun()
            st.markdown("---")

def show_vendor_payment_history_manager():
    st.markdown("#### Vendor Payment History")
    
    # Show all vendor payments
    if not st.session_state.vendor_statements:
        st.info("No vendor payment history available.")
        return
    
    # Group by vendor
    vendors_payments = {}
    for statement in st.session_state.vendor_statements:
        vendor = statement["vendor_name"]
        if vendor not in vendors_payments:
            vendors_payments[vendor] = []
        vendors_payments[vendor].append(statement)
    
    for vendor, payments in vendors_payments.items():
        st.markdown(f"##### {vendor}")
        
        # Create a DataFrame for better display
        payment_data = []
        total_paid = 0
        for payment in payments:
            payment_data.append({
                "Month": payment["month"],
                "Amount Paid": f"${payment['amount']:,.2f}",
                "Services": payment["services_count"],
                "Fees": f"${payment['service_fee_total']:,.2f}",
                "Payment Date": payment["payment_date"],
                "Method": payment["payment_method"]
            })
            total_paid += payment["amount"]
        
        df = pd.DataFrame(payment_data)
        st.dataframe(df, use_container_width=True)
        
        st.metric(f"Total Paid to {vendor}", f"${total_paid:,.2f}")
        st.markdown("---")
    
    # Overall vendor payments summary
    st.markdown("#### Vendor Payments Summary")
    vendor_totals = {}
    for statement in st.session_state.vendor_statements:
        vendor = statement["vendor_name"]
        if vendor not in vendor_totals:
            vendor_totals[vendor] = 0
        vendor_totals[vendor] += statement["amount"]
    
    if vendor_totals:
        vendors = list(vendor_totals.keys())
        totals = list(vendor_totals.values())
        
        fig = px.bar(x=vendors, y=totals, 
                    title="Total Payments by Vendor",
                    labels={"x": "Vendor", "y": "Total Amount ($)"})
        st.plotly_chart(fig, use_container_width=True)

# ==================== OTHER PORTAL FUNCTIONS ====================

def show_front_desk_portal():
    st.markdown('<div class="main-header">🏢 Front Desk Operations Portal</div>', unsafe_allow_html=True)
    
    # CHANGED: Combine into 4 tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🛏️ Room Management", "👥 Check-In/Out", "📋 Service Requests & Task Assignment", "📅 Calendar"])
    
    with tab1:
        show_front_desk_dashboard()
    with tab2:
        show_room_management()
    with tab3:
        show_checkin_checkout()
    with tab4:  
        show_service_requests_task_assignment()
    with tab5:
        show_calendar()

def show_service_requests_task_assignment():
    st.markdown('<div class="sub-header">📋 Service Requests & Task Assignment</div>', unsafe_allow_html=True)
    
    # Show pending service requests
    pending_requests = [req for req in st.session_state.service_requests if req["status"] == "Pending"]
    
    if not pending_requests:
        st.info("No pending service requests.")
        return
    
    for req in pending_requests[::-1]:
        # Display request
        col1, col2 = st.columns([3, 2])
        
        with col1:
            urgency_color = {
                "Critical": "critical-card", 
                "High": "critical-card", 
                "Medium": "warning-card", 
                "Low": "card"
            }.get(req["urgency"], "card")
            
            st.markdown(f"""
            <div class="card {urgency_color}">
                <h4>Request #{req['id']} - {req['type']}</h4>
                <p><strong>Guest:</strong> {req['guest']}</p>
                <p><strong>Room:</strong> {req['room']}</p>
                <p><strong>Urgency:</strong> {req['urgency']}</p>
                <p><strong>Details:</strong> {req['details']}</p>
                <p><strong>Requested:</strong> {req['timestamp']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Assign Task")
            
            # Special handling for Meeting requests
            if req["type"] == "Meeting":
                st.markdown("**Meeting Request - Additional Details Required**")
                meeting_date = st.date_input("Meeting Date", key=f"date_{req['id']}")
                meeting_time = st.time_input("Meeting Time", key=f"time_{req['id']}")
                meeting_venue = st.text_input("Venue", key=f"venue_{req['id']}")
                meeting_remarks = st.text_area("Special Remarks", key=f"remarks_{req['id']}")
            
            department = st.selectbox(
                "Assign to Department",
                ["Housekeeping Staff", "Maintenance Staff", "Catering Staff", "Event & Concierge Staff"],
                key=f"dept_{req['id']}"
            )
            
            if st.button(f"✅ Assign Task", key=f"assign_{req['id']}"):
                # Create task
                task_id = f"TK{len(st.session_state.tasks) + 1:03d}"
                new_task = {
                    "id": task_id,
                    "type": req["type"],
                    "room": req["room"],
                    "assigned_to": department,
                    "status": "Pending",
                    "description": f"{req['type']} for {req['guest']}: {req['details']}",
                    "request_id": req["id"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add meeting details if it's a meeting
                if req["type"] == "Meeting":
                    new_task["meeting_details"] = {
                        "date": meeting_date.strftime("%Y-%m-%d"),
                        "time": meeting_time.strftime("%H:%M"),
                        "venue": meeting_venue,
                        "remarks": meeting_remarks
                    }
                    # Also add to meetings calendar
                    if 'meetings' not in st.session_state:
                        st.session_state.meetings = []
                    st.session_state.meetings.append({
                        "title": f"Meeting - {req['guest']}",
                        "date": meeting_date.strftime("%Y-%m-%d"),
                        "time": meeting_time.strftime("%H:%M"),
                        "venue": meeting_venue,
                        "department": department,
                        "remarks": meeting_remarks,
                        "guest": req['guest'],
                        "room": req['room']
                    })
                
                st.session_state.tasks.append(new_task)
                req["status"] = "Assigned"
                
                # Send notification
                add_notification(f"Task assigned to {department}: {req['type']} for Room {req['room']}", "task_assigned", [department])
                st.success(f"✅ Task assigned to {department}! Notification sent.")
                st.rerun()
        
        st.markdown("---")
            
def show_front_desk_dashboard():
    st.markdown('<div class="sub-header">📊 Operations Overview</div>', unsafe_allow_html=True)
    
    # Calculate metrics
    total_rooms = len(st.session_state.rooms)
    occupied = len([r for r in st.session_state.rooms if r["status"] == "occupied"])
    vacant = len([r for r in st.session_state.rooms if r["status"] == "vacant"])
    today_bookings = len([b for b in st.session_state.bookings if b["check_in"] <= datetime.now().strftime("%Y-%m-%d") <= b["check_out"]])
    pending_requests = len([r for r in st.session_state.service_requests if r["status"] == "Pending"])
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Occupancy Rate", f"{(occupied/total_rooms)*100:.1f}%")
    with col2:
        st.metric("Available Rooms", vacant)
    with col3:
        st.metric("Today's Bookings", today_bookings)
    with col4:
        st.metric("Pending Requests", pending_requests)
    
    # Recent bookings
    st.markdown("#### Recent Bookings")
    recent_bookings = st.session_state.bookings[-5:][::-1] if st.session_state.bookings else []
    for booking in recent_bookings:
        st.markdown(f"""
        <div class="card">
            <p><strong>#{booking['id']}</strong> - {booking['guest']} - {booking['room_type']} - {booking['status']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_room_management():
    st.markdown('<div class="sub-header">🛏️ Room Rack</div>', unsafe_allow_html=True)
    
    # Room grid
    st.markdown("#### Room Status Overview")
    
    # Use columns but with proper spacing
    cols = st.columns(4)
    for idx, room in enumerate(st.session_state.rooms):
        with cols[idx % 4]:
            status_class = f"room-status-{room['status']}"
            st.markdown(f"""
            <div class="{status_class}">
                <h4>Room {room['number']}</h4>
                <p>{room['type']} - ${room['price']}/night</p>
                <p><strong>{room['status'].title()}</strong></p>
                {f"<p>Guest: {room['guest']}</p>" if room['guest'] else ""}
            </div>
            """, unsafe_allow_html=True)
    
    # Quick status update
    st.markdown("#### Quick Status Update")
    col1, col2 = st.columns(2)
    with col1:
        room_number = st.selectbox("Room Number", [r["number"] for r in st.session_state.rooms])
        new_status = st.selectbox("New Status", ["pending", "occupied", "vacant", "cleaning", "maintenance"])
    with col2:
        guest_name = st.text_input("Guest Name (if occupied)")
        if st.button("🔄 Update Room Status", use_container_width=True):
            for room in st.session_state.rooms:
                if room["number"] == room_number:
                    room["status"] = new_status
                    room["guest"] = guest_name if new_status == "occupied" else ""
                    add_notification(f"Room {room_number} status updated to {new_status}", "update", ["Front Desk Officer", "Hotel Manager"])
                    st.success(f"Room {room_number} status updated!")
                    break

def show_checkin_checkout():
    st.markdown('<div class="sub-header">👥 Guest Check-In/Check-Out</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["✅ Check-In", "🚪 Check-Out"])
    
    with tab1:
        st.markdown("#### Guest Check-In")
        col1, col2 = st.columns(2)
        with col1:
            booking_ref = st.text_input("Booking Reference")
            guest_name = st.text_input("Guest Name")
        with col2:
            available_rooms = [r["number"] for r in st.session_state.rooms if r["status"] == "vacant"]
            assigned_room = st.selectbox("Assign Room", available_rooms)
            payment_method = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "Online Banking", "E-Wallet", "Cash"])
        
        # THIS IS WHERE THE CHECK-IN CODE GOES:
        if st.button("✅ Complete Check-In", use_container_width=True):
            # Validate inputs
            if not booking_ref or not guest_name:
                st.error("Please enter booking reference and guest name")
                return
            
            # Update room status to occupied
            for room in st.session_state.rooms:
                if room["number"] == assigned_room:
                    room["status"] = "occupied"  # This is correct
                    room["guest"] = guest_name
                    break
            
            # Update booking with room number
            for booking in st.session_state.bookings:
                if booking["id"] == booking_ref:
                    booking["room_number"] = assigned_room
                    break
            
            # Create task for housekeeping
            task_id = f"TK{len(st.session_state.tasks) + 1:03d}"
            new_task = {
                "id": task_id,
                "type": "Room Preparation",
                "room": assigned_room,
                "assigned_to": "Housekeeping",
                "status": "Pending",
                "description": f"Prepare room for {guest_name}",
                "booking_id": booking_ref,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.tasks.append(new_task)
            
            # ADD LOG ENTRY FOR CHECK-IN:
            log_activity(st.session_state.current_user['name'], "Guest Check-In", 
                        f"Guest {guest_name} checked into Room {assigned_room} (Booking: {booking_ref})")
            
            add_notification(f"Guest {guest_name} checked into Room {assigned_room}", "checkin", ["Housekeeping Staff"])
            st.success(f"Guest checked into Room {assigned_room} successfully!")
    
    with tab2:
        st.markdown("#### Guest Check-Out")
        occupied_rooms = [r for r in st.session_state.rooms if r["status"] == "occupied"]
        checkout_room = st.selectbox("Select Room for Check-Out", [r["number"] for r in occupied_rooms])
        
        if st.button("💰 Process Check-Out", use_container_width=True):
            for room in st.session_state.rooms:
                if room["number"] == checkout_room:
                    guest_name = room["guest"]
                    room["status"] = "cleaning"
                    room["guest"] = ""
                    
                    # Find and update booking status to Completed
                    for booking in st.session_state.bookings:
                        if booking.get("room_number") == checkout_room and booking["status"] == "Confirmed":
                            booking["status"] = "Completed"
                            # Move to completed bookings for historical records
                            completed_booking = booking.copy()
                            st.session_state.completed_bookings.append(completed_booking)
                            # Remove from active bookings
                            st.session_state.bookings = [b for b in st.session_state.bookings if b["id"] != booking["id"]]
                            break
                    
                    # Create cleaning task
                    task_id = f"TK{len(st.session_state.tasks) + 1:03d}"
                    new_task = {
                        "id": task_id,
                        "type": "Cleaning",
                        "room": checkout_room,
                        "assigned_to": "Housekeeping",
                        "status": "Pending",
                        "description": f"Clean room after {guest_name} check-out",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.tasks.append(new_task)
                    
                    add_notification(f"Room {checkout_room} ready for cleaning after check-out", "checkout", ["Housekeeping Staff"])
                    add_notification(f"Guest {guest_name} has checked out from Room {checkout_room}", "checkout", ["Hotel Manager"])
                    st.success("Check-out completed successfully! Room assigned for cleaning.")
                    break

# ... (rest of the code remains the same for other functions like show_request_queue, show_task_assignment, etc.)

def show_approval_system():
    st.markdown('<div class="sub-header">📋 Approval System</div>', unsafe_allow_html=True)
    
    # Vendor approvals
    st.markdown("#### Vendor Applications")
    pending_vendors = [v for v in st.session_state.vendor_applications if v["status"] == "Pending"]
    
    if not pending_vendors:
        st.info("No pending vendor applications.")
    else:
        for idx, vendor in enumerate(pending_vendors):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="card warning-card">
                    <h4>{vendor['name']}</h4>
                    <p><strong>Service:</strong> {vendor['service']}</p>
                    <p><strong>Contact:</strong> {vendor['contact_person']} | {vendor['email']}</p>
                    <p><strong>Experience:</strong> {vendor['experience']} years</p>
                    <p><strong>Service Fee:</strong> {vendor['service_fee']}%</p>
                    <p><strong>Description:</strong> {vendor['description']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                # FIXED: Use unique key with index and vendor name
                if st.button("✅ Approve", key=f"approve_{idx}_{vendor['name']}"):
                    vendor["status"] = "Approved"
                    # Add to approved vendors
                    st.session_state.vendors.append({
                        "name": vendor["name"],
                        "service": vendor["service"],
                        "status": "Approved",
                        "contact": vendor["email"],
                        "registration_date": vendor["registration_date"],
                        "service_fee": vendor["service_fee"],
                        "monthly_earnings": 0,
                        "services_completed": 0,
                        "contact_person": vendor["contact_person"],
                        "phone": vendor.get("phone", ""),
                        "description": vendor["description"]
                    })
                    # Update user status
                    for user in st.session_state.registered_users:
                        if user["email"] == vendor["email"]:
                            user["status"] = "Active"
                    add_notification(f"Vendor {vendor['name']} approved", "vendor_approval", ["Vendor"])
                    st.rerun()
            with col3:
                # FIXED: Use unique key with index and vendor name
                if st.button("❌ Reject", key=f"reject_{idx}_{vendor['name']}"):
                    vendor["status"] = "Rejected"
                    # Update user status
                    for user in st.session_state.registered_users:
                        if user["email"] == vendor["email"]:
                            user["status"] = "Rejected"
                    st.rerun()

def show_manager_analytics():
    st.markdown('<div class="sub-header">📈 Performance Dashboard</div>', unsafe_allow_html=True)
    
    # Calculate metrics with real data
    total_rooms = len(st.session_state.rooms)
    occupied = len([r for r in st.session_state.rooms if r["status"] == "occupied"])
    revenue = sum(b["amount"] for b in st.session_state.bookings if b["status"] == "Confirmed")
    revenue += sum(b["amount"] for b in st.session_state.completed_bookings)
    pending_tasks = len([t for t in st.session_state.tasks if t["status"] == "Pending"])
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Occupancy Rate", f"{(occupied/total_rooms)*100:.1f}%")
    with col2:
        st.metric("Total Revenue", f"${revenue:,.0f}")
    with col3:
        st.metric("Pending Tasks", pending_tasks)
    with col4:
        st.metric("Active Bookings", len(st.session_state.bookings))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Room status chart
        status_counts = {
            'Occupied': occupied,
            'Vacant': len([r for r in st.session_state.rooms if r["status"] == "vacant"]),
            'Cleaning': len([r for r in st.session_state.rooms if r["status"] == "cleaning"]),
            'Maintenance': len([r for r in st.session_state.rooms if r["status"] == "maintenance"])
        }
        fig = px.pie(values=list(status_counts.values()), names=list(status_counts.keys()), 
                     title='Room Status Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue trend (with real data)
        monthly_revenue = {}
        for booking in st.session_state.bookings + st.session_state.completed_bookings:
            if booking.get("payment_status") == "Paid" and "timestamp" in booking:
                month = booking["timestamp"][:7]  # YYYY-MM
                if month not in monthly_revenue:
                    monthly_revenue[month] = 0
                monthly_revenue[month] += booking["amount"]
        
        # Add sample data for previous months
        sample_data = {"2024-09": 12500, "2024-10": 14200, "2024-11": 8600}
        for month, rev in sample_data.items():
            if month not in monthly_revenue:
                monthly_revenue[month] = rev
        
        if monthly_revenue:
            months = list(monthly_revenue.keys())
            revenues = list(monthly_revenue.values())
            
            fig = px.line(x=months, y=revenues, title='Monthly Revenue Trend (in $)')
            st.plotly_chart(fig, use_container_width=True)

def show_user_management():
    st.markdown('<div class="sub-header">👥 User Management</div>', unsafe_allow_html=True)
    
    # User statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_users = len(st.session_state.registered_users)
        st.metric("Total Users", total_users)
    with col2:
        active_users = len([u for u in st.session_state.registered_users if u["status"] == "Active"])
        st.metric("Active Users", active_users)
    with col3:
        guest_users = len([u for u in st.session_state.registered_users if u["role"] == "Guest"])
        st.metric("Guest Users", guest_users)
    with col4:
        staff_users = len([u for u in st.session_state.registered_users if u["role"] != "Guest" and u["role"] != "Vendor"])
        st.metric("Staff Users", staff_users)
    
    # User table
    st.markdown("#### User Database")
    
    # Convert to DataFrame for better display
    user_data = []
    for user in st.session_state.registered_users:
        user_data.append({
            "Name": user["name"],
            "Email": user["email"],
            "Role": user["role"],
            "Status": user["status"],
            "Registration Date": user["registration_date"]
        })
    
    if user_data:
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True)
        
        # User actions
        st.markdown("#### User Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_email = st.selectbox("Select User", [user["email"] for user in st.session_state.registered_users])
            new_status = st.selectbox("Update Status", ["Active", "Suspended", "Inactive"])
            
            if st.button("Update User Status"):
                for user in st.session_state.registered_users:
                    if user["email"] == selected_email:
                        user["status"] = new_status
                        add_notification(f"User {user['name']} status updated to {new_status}", "user_management")
                        st.success(f"User status updated successfully!")
                        break
        
        with col2:
            new_role = st.selectbox("Change Role", list(DEMO_ACCOUNTS.keys()))
            if st.button("Change User Role"):
                for user in st.session_state.registered_users:
                    if user["email"] == selected_email:
                        old_role = user["role"]
                        user["role"] = new_role
                        add_notification(f"User {user['name']} role changed from {old_role} to {new_role}", "user_management")
                        st.success(f"User role changed successfully!")
                        break
    else:
        st.info("No users registered in the system.")

def show_manager_reports():
    st.markdown('<div class="sub-header">📊 Business Reports</div>', unsafe_allow_html=True)
    
    report_type = st.selectbox("Select Report Type", [
        "Occupancy & Revenue Report",
        "Reservation Trends", 
        "Guest Satisfaction",
        "Staff Performance",
        "Vendor Expense Report"
    ])
    
    date_range = st.date_input("Report Period", 
                              [datetime(2025, 1, 1), datetime.now()])  # CHANGED TO 2025
    
    if st.button("📥 Download Report", use_container_width=True):
        # Generate sample report data with 2025 figures
        total_revenue = sum(b["amount"] for b in st.session_state.bookings + st.session_state.completed_bookings)
        occupied_rooms = len([r for r in st.session_state.rooms if r["status"] == "occupied"])
        total_rooms = len(st.session_state.rooms)
        occupancy_rate = (occupied_rooms/total_rooms)*100
        
        report_data = pd.DataFrame({
            'Metric': ['Total Revenue (2025)', 'Average Occupancy (2025)', 'RevPAR (2025)', 
                      'Guest Satisfaction', 'Staff Performance', 'Vendor Expenses (2025)'],
            'Value': [f"${total_revenue:,.0f}", 
                     f"{occupancy_rate:.1f}%",
                     f"${(total_revenue/total_rooms):.0f}",
                     '4.6/5.0', 
                     '92%',
                     f"${sum(s['amount'] for s in st.session_state.vendor_statements):,.0f}"],
        })
        
        # Create download button
        csv = report_data.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Report as CSV",
            data=csv,
            file_name=f"{report_type.replace(' ', '_').lower()}_2025.csv",
            mime="text/csv",
        )
        st.success("2025 Report generated successfully!")

def show_staff_attendance_performance():
    st.markdown('<div class="sub-header">👥 Staff Attendance & Performance</div>', unsafe_allow_html=True)
    
    # Attendance Summary
    st.markdown("#### 📊 Attendance Summary")
    today = datetime.now().strftime("%Y-%m-%d")
    today_attendance = [r for r in st.session_state.attendance_records if r["date"] == today]
    
    if today_attendance:
        df_attendance = pd.DataFrame(today_attendance)
        st.dataframe(df_attendance, use_container_width=True)
    
    # Performance Metrics
    st.markdown("#### 🎯 Performance Metrics")
    if st.session_state.performance_metrics:
        df_performance = pd.DataFrame(st.session_state.performance_metrics)
        st.dataframe(df_performance, use_container_width=True)
        
        # Performance chart by role
        performance_by_role = df_performance.groupby('role')['value'].sum().reset_index()
        fig = px.bar(performance_by_role, x='role', y='value', title='Tasks Completed by Role')
        st.plotly_chart(fig, use_container_width=True)

# ==================== HOUSEKEEPING PORTAL ====================
        
def show_housekeeping_portal():
    st.markdown('<div class="main-header">🧹 Housekeeping Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Assigned Tasks", "📊 Performance", "📅 Calendar", "📊 Past Work"])
    
    with tab1:
        st.markdown('<div class="sub-header">🛏️ Cleaning Schedule</div>', unsafe_allow_html=True)
        
        housekeeping_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == "Housekeeping" and t["status"] in ["Pending", "In Progress"]]
        
        if not housekeeping_tasks:
            st.info("No tasks assigned.")
        else:
            for task in housekeeping_tasks:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    status_color = "warning-card" if task["status"] == "Pending" else "card"
                    st.markdown(f"""
                    <div class="card {status_color}">
                        <h4>{task['type']} - Room {task['room']}</h4>
                        <p>{task['description']}</p>
                        <p>Assigned: {task['timestamp']}</p>
                        <p>Status: <strong>{task['status']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if task["status"] == "Pending":
                        if st.button("Start", key=f"start_{task['id']}"):
                            task["status"] = "In Progress"
                            st.rerun()
                with col3:
                    if task["status"] in ["Pending", "In Progress"]:
                        if st.button("Complete", key=f"complete_{task['id']}"):
                            task["status"] = "Completed"
                            task["completed_by"] = st.session_state.current_user['name']
                            task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            # ADD LOG ENTRY HERE:
                            log_activity(st.session_state.current_user['name'], "Task Completed", 
                                    f"Housekeeping Task {task['id']} completed - {task['description']}")
                        
                            # Update room status if it's a cleaning task
                            if task["type"] == "Cleaning":
                                for room in st.session_state.rooms:
                                    if room["number"] == task["room"]:
                                        room["status"] = "vacant"
                                        break
                            
                            add_notification(f"Housekeeping task {task['id']} completed for Room {task['room']}", 
                                           "task_completed", ["Hotel Manager", "Front Desk Officer"])
                            st.success(f"Task {task['id']} completed!")
                            st.rerun()
    
    with tab3:
        show_calendar("Housekeeping Staff")
    
    with tab4:
        show_past_work("Housekeeping Staff")
        
# ==================== MAINTENANCE PORTAL ====================
def show_maintenance_portal():
    st.markdown('<div class="main-header">🔧 Maintenance Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Assigned Tasks", "📅 Calendar", "📊 Past Work"])
    
    with tab1:
        maintenance_requests = [r for r in st.session_state.service_requests if r["type"] == "Maintenance" and r["status"] in ["Pending", "In Progress"]]
        
        if not maintenance_requests:
            st.info("No maintenance requests.")
            return
        
        for request in maintenance_requests:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                urgency_color = {
                    "Critical": "critical-card", 
                    "High": "critical-card", 
                    "Medium": "warning-card", 
                    "Low": "card"
                }.get(request["urgency"], "card")
                
                status_color = "warning-card" if request["status"] == "Pending" else "card"
                
                st.markdown(f"""
                <div class="card {urgency_color} {status_color}">
                    <h4>Maintenance - Room {request['room']}</h4>
                    <p>Issue: {request['details']}</p>
                    <p>Guest: {request['guest']}</p>
                    <p>Urgency: {request['urgency']}</p>
                    <p>Status: <strong>{request['status']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if request["status"] == "Pending":
                    if st.button("Start Work", key=f"start_{request['id']}"):
                        request["status"] = "In Progress"
                        st.rerun()
            with col3:
                if request["status"] in ["Pending", "In Progress"]:
                    if st.button("Complete", key=f"complete_{request['id']}"):
                        request["status"] = "Completed"
                        request["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # ADD LOG ENTRY HERE:
                        log_activity(st.session_state.current_user['name'], "Task Completed", 
                                    f"Maintenance Request {request['id']} completed - {request['details']}")
                        add_notification(f"Maintenance completed for Room {request['room']}", "maintenance")
                        st.rerun()
    
    with tab2:
        show_calendar("Maintenance Staff")
    
    with tab3:
        show_past_work("Maintenance Staff")

# ==================== CATERING PORTAL ====================
def show_catering_portal():
    st.markdown('<div class="main-header">🍽️ Catering Services Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Assigned Tasks", "📅 Calendar", "📊 Past Work"])
    
    with tab1:
        st.markdown('<div class="sub-header">🍳 Catering Tasks</div>', unsafe_allow_html=True)
        
        catering_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == "Catering" and t["status"] in ["Pending", "In Progress"]]
        
        if not catering_tasks:
            st.info("No catering tasks assigned.")
            return
        
        for task in catering_tasks:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                status_color = "warning-card" if task["status"] == "Pending" else "card" if task["status"] == "In Progress" else "success-card"
                st.markdown(f"""
                <div class="card {status_color}">
                    <h4>{task['type']} - Booking #{task.get('booking_id', 'N/A')}</h4>
                    <p>{task['description']}</p>
                    <p>Assigned: {task['timestamp']}</p>
                    <p>Status: <strong>{task['status']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if task["status"] == "Pending":
                    if st.button("Start", key=f"start_{task['id']}"):
                        task["status"] = "In Progress"
                        st.rerun()
            with col3:
                if task["status"] in ["Pending", "In Progress"]:
                    if st.button("Complete", key=f"complete_{task['id']}"):
                        task["status"] = "Completed"
                        task["completed_by"] = st.session_state.current_user['name']
                        task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        log_activity(st.session_state.current_user['name'], "Task Completed", 
                                    f"Catering Task {task['id']} completed - {task['description']}")
                        add_notification(f"Catering task {task['id']} completed", "task")
                        st.rerun()
    
    with tab2:
        show_calendar("Catering Staff")
    
    with tab3:
        show_past_work("Catering Staff")

# ==================== EVENT & CONCIERGE PORTAL ====================
def show_event_concierge_portal():
    st.markdown('<div class="main-header">🎉 Event & Concierge Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Assigned Tasks", "📅 Event Calendar", "📊 Past Work"])
    
    with tab1:
        st.markdown('<div class="sub-header">🎊 Event & Concierge Tasks</div>', unsafe_allow_html=True)
        
        event_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == "Event & Concierge" and t["status"] in ["Pending", "In Progress"]]
        
        if not event_tasks:
            st.info("No event or concierge tasks assigned.")
            return
        
        for task in event_tasks:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                status_color = "warning-card" if task["status"] == "Pending" else "card" if task["status"] == "In Progress" else "success-card"
                
                # Show meeting details if available
                meeting_info = ""
                if task.get("meeting_details"):
                    md = task["meeting_details"]
                    meeting_info = f"<p><strong>Meeting:</strong> {md.get('date', '')} at {md.get('time', '')} - {md.get('venue', '')}</p>"
                
                st.markdown(f"""
                <div class="card {status_color}">
                    <h4>{task['type']} - Booking #{task.get('booking_id', 'N/A')}</h4>
                    <p>{task['description']}</p>
                    {meeting_info}
                    <p>Assigned: {task['timestamp']}</p>
                    <p>Status: <strong>{task['status']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if task["status"] == "Pending":
                    if st.button("Start", key=f"start_{task['id']}"):
                        task["status"] = "In Progress"
                        st.rerun()
            with col3:
                if task["status"] in ["Pending", "In Progress"]:
                    if st.button("Complete", key=f"complete_{task['id']}"):
                        task["status"] = "Completed"
                        task["completed_by"] = st.session_state.current_user['name']
                        task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        log_activity(st.session_state.current_user['name'], "Task Completed", 
                                    f"Event/Concierge Task {task['id']} completed - {task['description']}")
                        add_notification(f"Event/Concierge task {task['id']} completed", "task")
                        st.rerun()
    
    with tab2:
        show_calendar("Event & Concierge Staff")
    
    with tab3:
        show_past_work("Event & Concierge Staff")
                    
def show_system_config():
    st.markdown('<div class="sub-header">⚙️ System Configuration</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Room Rates")
        # FIXED: Use only the 4 consistent room types
        room_types = ["Single", "Double", "Suite", "Deluxe"]
        default_rates = {"Single": 150, "Double": 200, "Suite": 350, "Deluxe": 500}
        
        for room_type in room_types:
            new_rate = st.number_input(
                f"{room_type} Room Rate ($)",
                min_value=50,
                max_value=1000,
                value=default_rates[room_type],
                key=f"rate_{room_type}"
            )
            if st.button(f"Update {room_type} Rate", key=f"update_{room_type}"):
                # Update room rates in the system
                for room in st.session_state.rooms:
                    if room["type"] == room_type:
                        room["price"] = new_rate
                st.success(f"{room_type} room rate updated to ${new_rate}")
    
    with col2:
        st.markdown("#### System Settings")
        
        # Hotel information
        hotel_name = st.text_input("Hotel Name", value="Grand Stay Hotel")
        check_in_time = st.time_input("Check-in Time", value=datetime.strptime("14:00", "%H:%M").time())
        check_out_time = st.time_input("Check-out Time", value=datetime.strptime("12:00", "%H:%M").time())
        
        # System preferences
        auto_cancel_hours = st.number_input("Auto-cancel unpaid bookings after (hours)", 
                                          min_value=1, max_value=48, value=2)
        max_guests_per_room = st.number_input("Maximum Guests per Room", 
                                            min_value=1, max_value=6, value=4)
        
        if st.button("💾 Save Configuration", use_container_width=True):
            st.success("System configuration saved successfully!")

def to_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()

# Run the application
if __name__ == "__main__":
    main()