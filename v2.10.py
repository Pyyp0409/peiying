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
        text-align: center;
    }
    
    .room-status-vacant {
        background-color: #27AE60;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    
    .room-status-cleaning {
        background-color: #F39C12;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    
    .room-status-maintenance {
        background-color: #95A5A6;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
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
    ],
    "Marketing & Sales Staff": [
        {"email": "marketing@demo.com", "password": "marketing123", "name": "Alex Promoter"}
    ]
}

# Initialize session data
def init_session_data():
    # Initialize all session state variables
    defaults = {
        'authenticated': False,
        'current_user': None,
        'current_role': None,
        'supabase': init_supabase(),
        'bookings': [
            # Sample bookings with real data
            {"id": "BK001", "guest": "John Traveler", "guest_email": "guest1@demo.com", "room_type": "Deluxe", 
             "check_in": "2024-09-15", "check_out": "2024-09-18", "status": "Completed", "payment_status": "Paid", 
             "amount": 1500, "amount_paid": 1500, "room_number": "301", "timestamp": "2024-09-15 14:30:00"},
            {"id": "BK002", "guest": "Sarah Visitor", "guest_email": "guest2@demo.com", "room_type": "Suite", 
             "check_in": "2024-10-05", "check_out": "2024-10-10", "status": "Completed", "payment_status": "Paid", 
             "amount": 1750, "amount_paid": 1750, "room_number": "203", "timestamp": "2024-10-05 15:45:00"},
            {"id": "BK003", "guest": "Mike Brown", "guest_email": "mike@example.com", "room_type": "Double", 
             "check_in": "2024-10-20", "check_out": "2024-10-25", "status": "Confirmed", "payment_status": "Paid", 
             "amount": 1000, "amount_paid": 1000, "room_number": "102", "timestamp": "2024-10-20 12:15:00"},
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
        ],
        'service_requests': [],
        'invoices': [
            {"id": "INV001", "booking_id": "BK001", "guest": "John Traveler", "amount": 1500, "status": "Paid", 
             "payment_method": "Credit Card", "due_date": "2024-09-15 16:30:00"},
            {"id": "INV002", "booking_id": "BK002", "guest": "Sarah Visitor", "amount": 1750, "status": "Paid", 
             "payment_method": "Online Banking", "due_date": "2024-10-05 17:45:00"},
            {"id": "INV003", "booking_id": "BK003", "guest": "Mike Brown", "amount": 1000, "status": "Paid", 
             "payment_method": "Debit Card", "due_date": "2024-10-20 14:15:00"},
        ],
        'notifications': [],
        'staff_applications': [],
        'vendor_applications': [],
        'guest_applications': [],
        'registered_users': [
            {"email": "guest1@demo.com", "name": "John Traveler", "role": "Guest", "status": "Active", "registration_date": "2024-01-01", "password": "guest123"},
            {"email": "guest2@demo.com", "name": "Sarah Visitor", "role": "Guest", "status": "Active", "registration_date": "2024-01-02", "password": "guest123"},
            {"email": "frontdesk@demo.com", "name": "Emily Frontdesk", "role": "Front Desk Officer", "status": "Active", "registration_date": "2024-01-01", "password": "frontdesk123"},
            {"email": "housekeeping@demo.com", "name": "Maria Cleaner", "role": "Housekeeping Staff", "status": "Active", "registration_date": "2024-01-01", "password": "house123"},
            {"email": "maintenance@demo.com", "name": "Mike Technician", "role": "Maintenance Staff", "status": "Active", "registration_date": "2024-01-01", "password": "maintain123"},
            {"email": "manager@demo.com", "name": "David Manager", "role": "Hotel Manager", "status": "Active", "registration_date": "2024-01-01", "password": "manager123"},
            {"email": "billing@demo.com", "name": "Lisa Accountant", "role": "Billing Officer", "status": "Active", "registration_date": "2024-01-01", "password": "billing123"},
            {"email": "vendor@demo.com", "name": "Tom Suppliers", "role": "Vendor", "status": "Approved", "registration_date": "2024-01-01", "password": "vendor123"},
            {"email": "catering@demo.com", "name": "Sarah Catering", "role": "Catering Staff", "status": "Active", "registration_date": "2024-01-01", "password": "catering123"},
            {"email": "events@demo.com", "name": "Emma Events", "role": "Event & Concierge Staff", "status": "Active", "registration_date": "2024-01-01", "password": "events123"},
            {"email": "marketing@demo.com", "name": "Alex Promoter", "role": "Marketing & Sales Staff", "status": "Active", "registration_date": "2024-01-01", "password": "marketing123"},
        ],
        'reviews': [
            {"guest": "John Traveler", "room": "301", "ratings": {"overall": 5, "cleanliness": 5, "service": 4, "comfort": 5}, "comments": "Excellent stay! The room was spacious and clean.", "timestamp": "2024-09-18 10:30:00"},
            {"guest": "Sarah Visitor", "room": "203", "ratings": {"overall": 4, "cleanliness": 4, "service": 5, "comfort": 4}, "comments": "Great service and comfortable beds. Will come back!", "timestamp": "2024-10-10 14:45:00"},
        ],
        'tasks': [],
        'vendors': [
            {"name": "ABC Laundry", "service": "Laundry", "status": "Approved", "contact": "vendor@demo.com", 
             "registration_date": "2024-01-01", "service_fee": 5.0, "monthly_earnings": 2850, "services_completed": 38,
             "contact_person": "Tom Suppliers", "phone": "+1-555-0123", "description": "Professional laundry services for hotels"},
            {"name": "XYZ Catering", "service": "Food Service", "status": "Approved", "contact": "catering@demo.com", 
             "registration_date": "2024-01-02", "service_fee": 7.5, "monthly_earnings": 4200, "services_completed": 28}
        ],
        'vendor_services': [
            # September services for ABC Laundry
            {"id": "VS001", "vendor_name": "ABC Laundry", "service_type": "Laundry", "location": "All Rooms", 
             "amount": 1500, "service_fee": 75, "date": "2024-09-30", "status": "Completed", "description": "Monthly laundry service"},
            {"id": "VS002", "vendor_name": "ABC Laundry", "service_type": "Laundry", "location": "Linen", 
             "amount": 500, "service_fee": 25, "date": "2024-09-15", "status": "Completed", "description": "Extra linen service"},
            # October services for ABC Laundry
            {"id": "VS003", "vendor_name": "ABC Laundry", "service_type": "Laundry", "location": "All Rooms", 
             "amount": 1600, "service_fee": 80, "date": "2024-10-31", "status": "Completed", "description": "Monthly laundry service"},
            {"id": "VS004", "vendor_name": "ABC Laundry", "service_type": "Laundry", "location": "Towels", 
             "amount": 350, "service_fee": 17.5, "date": "2024-10-20", "status": "Completed", "description": "Emergency towel service"},
        ],
        'vendor_statements': [
            # September payment to ABC Laundry
            {"id": "VS001", "vendor_name": "ABC Laundry", "month": "2024-09", "amount": 1900, 
             "services_count": 2, "service_fee_total": 100, "payment_date": "2024-10-05", 
             "payment_method": "Bank Transfer", "status": "Paid"},
            # October payment to ABC Laundry
            {"id": "VS002", "vendor_name": "ABC Laundry", "month": "2024-10", "amount": 1852.5, 
             "services_count": 2, "service_fee_total": 97.5, "payment_date": "2024-11-05", 
             "payment_method": "Bank Transfer", "status": "Paid"},
        ],
        'cancellation_requests': [],
        'refund_requests': [],
        'completed_bookings': [
            {"id": "BK001", "guest": "John Traveler", "guest_email": "guest1@demo.com", "room_type": "Deluxe", 
             "check_in": "2024-09-15", "check_out": "2024-09-18", "status": "Completed", "payment_status": "Paid", 
             "amount": 1500, "amount_paid": 1500, "room_number": "301", "timestamp": "2024-09-15 14:30:00"},
            {"id": "BK002", "guest": "Sarah Visitor", "guest_email": "guest2@demo.com", "room_type": "Suite", 
             "check_in": "2024-10-05", "check_out": "2024-10-10", "status": "Completed", "payment_status": "Paid", 
             "amount": 1750, "amount_paid": 1750, "room_number": "203", "timestamp": "2024-10-05 15:45:00"},
        ],
        # NEW: Staff scheduling data
        'staff_schedules': [
            {"staff_name": "Emily Frontdesk", "role": "Front Desk Officer", "date": "2024-11-01", 
             "shift_start": "07:00", "shift_end": "15:00", "status": "Scheduled"},
            {"staff_name": "Maria Cleaner", "role": "Housekeeping Staff", "date": "2024-11-01", 
             "shift_start": "08:00", "shift_end": "16:00", "status": "Scheduled"},
            {"staff_name": "Mike Technician", "role": "Maintenance Staff", "date": "2024-11-01", 
             "shift_start": "09:00", "shift_end": "17:00", "status": "Scheduled"},
        ],
        # NEW: Marketing campaigns
        'marketing_campaigns': [
            {"id": "MC001", "name": "Summer Special", "type": "Seasonal Promotion", "start_date": "2024-06-01", 
             "end_date": "2024-08-31", "budget": 5000, "status": "Completed", "bookings_generated": 45, 
             "revenue_generated": 22500, "roi": 350},
            {"id": "MC002", "name": "Business Traveler Package", "type": "Corporate Promotion", 
             "start_date": "2024-09-01", "end_date": "2024-11-30", "budget": 3000, "status": "Active", 
             "bookings_generated": 28, "revenue_generated": 14000, "roi": 367},
        ],
        # NEW: Staff meetings
        'staff_meetings': [
            {"id": "MT001", "title": "Weekly Operations Review", "staff_member": "Emily Frontdesk", 
             "guest": "Corporate Client", "date": "2024-11-05", "time": "14:00", "duration": 60, 
             "status": "Scheduled", "room": "Conference Room A"},
            {"id": "MT002", "title": "Event Planning Session", "staff_member": "Emma Events", 
             "guest": "Wedding Planner", "date": "2024-11-06", "time": "10:00", "duration": 90, 
             "status": "Scheduled", "room": "Meeting Room B"},
        ],
        # NEW: Inventory management
        'inventory': [
            {"item_id": "INV001", "name": "Bed Linens", "category": "Room Supplies", "quantity": 150, 
             "min_quantity": 50, "unit_cost": 25.00, "supplier": "ABC Textiles", "last_ordered": "2024-10-15"},
            {"item_id": "INV002", "name": "Toiletries Set", "category": "Amenities", "quantity": 200, 
             "min_quantity": 75, "unit_cost": 8.50, "supplier": "Hotel Supplies Inc", "last_ordered": "2024-10-20"},
            {"item_id": "INV003", "name": "Coffee Pods", "category": "Food & Beverage", "quantity": 500, 
             "min_quantity": 200, "unit_cost": 0.75, "supplier": "Beverage Co", "last_ordered": "2024-10-25"},
        ],
        # NEW: Staff performance metrics
        'staff_performance': [
            {"staff_name": "Maria Cleaner", "role": "Housekeeping Staff", "month": "2024-10", 
             "tasks_completed": 45, "avg_rating": 4.8, "efficiency_score": 92, "guest_compliments": 3},
            {"staff_name": "Mike Technician", "role": "Maintenance Staff", "month": "2024-10", 
             "tasks_completed": 28, "avg_rating": 4.6, "efficiency_score": 88, "guest_compliments": 2},
            {"staff_name": "Emily Frontdesk", "role": "Front Desk Officer", "month": "2024-10", 
             "tasks_completed": 65, "avg_rating": 4.9, "efficiency_score": 95, "guest_compliments": 5},
        ]
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Notification system
def add_notification(message, category="info", target_roles=None):
    notification = {
        "id": len(st.session_state.notifications) + 1,
        "message": message,
        "category": category,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False,
        "target_roles": target_roles
    }
    st.session_state.notifications.append(notification)

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

# Main application
def main():
    # Initialize session data
    init_session_data()
    
    # Show login page if not authenticated
    if not st.session_state.authenticated:
        show_login_page()
    else:
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
            user = authenticate_user(email, password, role)
            if user:
                st.session_state.authenticated = True
                st.session_state.current_user = user
                st.session_state.current_role = role
                add_notification(f"User {user['name']} logged in as {role}", "success")
                st.success(f"Welcome back, {user['name']}!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please use demo accounts or registered accounts.")
        
        st.markdown('</div>', unsafe_allow_html=True)

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
                    
                    add_notification(f"New vendor application: {company_name}", "vendor", ["Hotel Manager"])
                    st.success(f"📋 Vendor application submitted! {company_name} is now pending approval. You will be notified once approved.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_main_application():
    # Sidebar with user info and notifications
    with st.sidebar:
        # User info card
        unread_count = len([n for n in st.session_state.notifications if not n['read']])
        badge_html = f'<span class="notification-badge">{unread_count}</span>' if unread_count > 0 else ''
        
        st.markdown(f"""
        <div class="sidebar-header">
            <h3>👋 Welcome, {st.session_state.current_user['name']}</h3>
            <p><strong>Role:</strong> {st.session_state.current_role}</p>
            <p>🔔 Notifications {badge_html}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Notifications section
        if unread_count > 0:
            with st.expander("📋 Recent Notifications", expanded=False):
                user_notifications = [
                    n for n in st.session_state.notifications 
                    if not n['read'] and (n.get('target_roles') is None or st.session_state.current_role in n.get('target_roles', []))
                ][-5:][::-1]
                
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
    elif st.session_state.current_role == "Marketing & Sales Staff":
        show_marketing_portal()

# ==================== GUEST PORTAL ====================
def show_guest_portal():
    st.markdown('<div class="main-header">👤 Guest Portal - Grand Stay Hotel</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Book Room", "📋 My Bookings", "🛎️ Service Requests", "📅 Schedule Meeting", "⭐ Leave Review", "📝 Recent Reviews"])
    
    with tab1:
        show_guest_booking()
    with tab2:
        show_guest_bookings()
    with tab3:
        show_guest_service_requests()
    with tab4:
        show_meeting_scheduling()  # NEW: Meeting scheduling
    with tab5:
        show_guest_reviews()
    with tab6:
        show_recent_reviews()

def show_guest_booking():
    st.markdown('<div class="sub-header">📅 Room Reservation</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        booking_type = st.selectbox("Booking Type", ["Hourly", "Daily", "Weekly", "Monthly"])
        room_type = st.selectbox("Room Type", ["Single", "Double", "Suite", "Deluxe"])
        
        if booking_type == "Hourly":
            col_a, col_b = st.columns(2)
            with col_a:
                check_in_date = st.date_input("Date", datetime.now())
                check_in_time = st.time_input("Start Time", datetime.now().time())
            with col_b:
                duration_hours = st.number_input("Duration (hours)", min_value=1, max_value=23, value=4)
                check_out_time = (datetime.combine(check_in_date, check_in_time) + timedelta(hours=duration_hours)).time()
            st.info(f"Check-out: {check_out_time.strftime('%H:%M')}")
        else:
            check_in = st.date_input("Check-in Date", datetime.now())
            check_out = st.date_input("Check-out Date", datetime.now() + timedelta(days=1))
            
        num_guests = st.number_input("Number of Guests", min_value=1, max_value=4, value=2)
    
    with col2:
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
    
    if booking_type == "Hourly":
        # Hourly rate is 1/8 of daily rate (3-hour minimum)
        hourly_rate = base_price / 8
        total_price = hourly_rate * duration_hours
        nights = duration_hours / 24
    else:
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
        duration_text = f"{duration_hours} hours" if booking_type == "Hourly" else f"{nights} nights"
        st.markdown(f"""
        <div class="card">
            <h4>Booking Details</h4>
            <p><strong>Type:</strong> {booking_type}</p>
            <p><strong>Room:</strong> {room_type}</p>
            <p><strong>Duration:</strong> {duration_text}</p>
            <p><strong>Base Price:</strong> ${base_price * nights if booking_type != 'Hourly' else total_price:.2f}</p>
            <p><strong>Additional Services:</strong> ${total_price - (base_price * nights if booking_type != 'Hourly' else total_price):.2f}</p>
            <hr>
            <h4>Total: ${total_price:.2f}</h4>
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
        
        if booking_type == "Hourly":
            check_in_str = f"{check_in_date.strftime('%Y-%m-%d')} {check_in_time.strftime('%H:%M')}"
            check_out_str = f"{check_in_date.strftime('%Y-%m-%d')} {check_out_time.strftime('%H:%M')}"
        else:
            check_in_str = check_in.strftime("%Y-%m-%d")
            check_out_str = check_out.strftime("%Y-%m-%d")
        
        new_booking = {
            "id": booking_id,
            "guest": st.session_state.current_user['name'],
            "guest_email": st.session_state.current_user['email'],
            "room_type": room_type,
            "booking_type": booking_type,
            "check_in": check_in_str,
            "check_out": check_out_str,
            "status": "Confirmed",
            "payment_status": "Pending",
            "amount": total_price,
            "amount_paid": 0,
            "special_requests": special_requests,
            "payment_method": payment_method,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cancellation_status": "Not Requested"
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
        add_notification(f"New {booking_type.lower()} booking #{booking_id} from {st.session_state.current_user['name']}", "booking", ["Front Desk Officer", "Hotel Manager"])
        add_notification(f"Payment required for booking #{booking_id} - ${total_price:.2f}", "payment", ["Billing Officer"])
        
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
            <p><strong>Amount Due:</strong> ${total_price:.2f}</p>
            <p><strong>Payment Method:</strong> {payment_method}</p>
            <p><strong>Payment Deadline:</strong> {(datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="color: #E74C3C;"><strong>⚠️ Important:</strong> Booking will auto-cancel if payment not completed in 2 hours</p>
        </div>
        """, unsafe_allow_html=True)

def show_meeting_scheduling():
    st.markdown('<div class="sub-header">📅 Schedule Meeting with Staff</div>', unsafe_allow_html=True)
    
    with st.form("meeting_scheduling_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            meeting_title = st.text_input("Meeting Title *")
            staff_member = st.selectbox("Staff Member *", 
                                      ["Event Planner", "Concierge", "Hotel Manager", "Catering Manager"])
            meeting_date = st.date_input("Meeting Date *", datetime.now() + timedelta(days=1))
        
        with col2:
            meeting_time = st.time_input("Meeting Time *", datetime.strptime("10:00", "%H:%M").time())
            duration = st.number_input("Duration (minutes) *", min_value=15, max_value=180, value=60, step=15)
            meeting_room = st.selectbox("Preferred Location", 
                                      ["Conference Room A", "Conference Room B", "Business Center", "Lobby Lounge"])
        
        meeting_agenda = st.text_area("Meeting Agenda / Purpose *")
        
        submitted = st.form_submit_button("📅 Schedule Meeting")
        
        if submitted:
            if not all([meeting_title, staff_member, meeting_agenda]):
                st.error("Please fill in all required fields (*)")
            else:
                meeting_id = f"MT{len(st.session_state.staff_meetings) + 1:03d}"
                new_meeting = {
                    "id": meeting_id,
                    "title": meeting_title,
                    "staff_member": staff_member,
                    "guest": st.session_state.current_user['name'],
                    "date": meeting_date.strftime("%Y-%m-%d"),
                    "time": meeting_time.strftime("%H:%M"),
                    "duration": duration,
                    "agenda": meeting_agenda,
                    "room": meeting_room,
                    "status": "Scheduled",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.staff_meetings.append(new_meeting)
                
                add_notification(f"New meeting scheduled: {meeting_title} with {staff_member}", "meeting", ["Event & Concierge Staff", "Hotel Manager"])
                st.success(f"Meeting scheduled successfully! Our {staff_member} will contact you to confirm details.")

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
            
            booking_type = booking.get('booking_type', 'Daily')
            duration_text = f"({booking_type})" if booking_type != 'Daily' else ""
            
            st.markdown(f"""
            <div class="card {status_color}">
                <h4>Booking #{booking['id']} - {booking['room_type']} {duration_text}</h4>
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

# ==================== MARKETING PORTAL ====================
def show_marketing_portal():
    st.markdown('<div class="main-header">📢 Marketing & Sales Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Campaign Management", "📊 Performance Analytics", "📈 Sales Dashboard", "👥 Guest Insights"])
    
    with tab1:
        show_campaign_management()
    with tab2:
        show_marketing_analytics()
    with tab3:
        show_sales_dashboard()
    with tab4:
        show_guest_insights()

def show_campaign_management():
    st.markdown('<div class="sub-header">🎯 Marketing Campaigns</div>', unsafe_allow_html=True)
    
    # Create new campaign
    with st.form("new_campaign_form"):
        st.markdown("#### Create New Campaign")
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name *")
            campaign_type = st.selectbox("Campaign Type *", 
                                       ["Seasonal Promotion", "Corporate Package", "Loyalty Program", 
                                        "Social Media Campaign", "Email Marketing", "Partnership"])
            start_date = st.date_input("Start Date *", datetime.now())
        
        with col2:
            end_date = st.date_input("End Date *", datetime.now() + timedelta(days=30))
            budget = st.number_input("Budget ($) *", min_value=100, max_value=10000, value=1000)
            target_audience = st.selectbox("Target Audience", 
                                         ["Business Travelers", "Families", "Couples", "Tour Groups", "All Guests"])
        
        campaign_description = st.text_area("Campaign Description *")
        promotion_code = st.text_input("Promotion Code")
        
        submitted = st.form_submit_button("🚀 Launch Campaign")
        
        if submitted:
            if not all([campaign_name, campaign_description]):
                st.error("Please fill in all required fields (*)")
            else:
                campaign_id = f"MC{len(st.session_state.marketing_campaigns) + 1:03d}"
                new_campaign = {
                    "id": campaign_id,
                    "name": campaign_name,
                    "type": campaign_type,
                    "description": campaign_description,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "budget": budget,
                    "target_audience": target_audience,
                    "promotion_code": promotion_code,
                    "status": "Active",
                    "bookings_generated": 0,
                    "revenue_generated": 0,
                    "roi": 0,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.marketing_campaigns.append(new_campaign)
                add_notification(f"New marketing campaign launched: {campaign_name}", "marketing", ["Hotel Manager"])
                st.success(f"Campaign '{campaign_name}' launched successfully!")
    
    # Existing campaigns
    st.markdown("#### Active Campaigns")
    active_campaigns = [c for c in st.session_state.marketing_campaigns if c["status"] == "Active"]
    
    if not active_campaigns:
        st.info("No active campaigns.")
    else:
        for campaign in active_campaigns:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="card success-card">
                    <h4>{campaign['name']}</h4>
                    <p><strong>Type:</strong> {campaign['type']} | <strong>Audience:</strong> {campaign['target_audience']}</p>
                    <p><strong>Period:</strong> {campaign['start_date']} to {campaign['end_date']}</p>
                    <p><strong>Budget:</strong> ${campaign['budget']} | <strong>Revenue:</strong> ${campaign['revenue_generated']}</p>
                    <p><strong>ROI:</strong> {campaign['roi']}% | <strong>Bookings:</strong> {campaign['bookings_generated']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Update", key=f"update_{campaign['id']}"):
                    # In a real app, this would open an update form
                    st.info("Update functionality would be implemented here")
            with col3:
                if st.button("End", key=f"end_{campaign['id']}"):
                    campaign["status"] = "Completed"
                    st.rerun()

def show_marketing_analytics():
    st.markdown('<div class="sub-header">📊 Campaign Performance</div>', unsafe_allow_html=True)
    
    # Campaign performance metrics
    total_campaigns = len(st.session_state.marketing_campaigns)
    active_campaigns = len([c for c in st.session_state.marketing_campaigns if c["status"] == "Active"])
    total_revenue = sum(c["revenue_generated"] for c in st.session_state.marketing_campaigns)
    total_bookings = sum(c["bookings_generated"] for c in st.session_state.marketing_campaigns)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Campaigns", total_campaigns)
    with col2:
        st.metric("Active Campaigns", active_campaigns)
    with col3:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col4:
        st.metric("Bookings Generated", total_bookings)
    
    # Campaign performance chart
    if st.session_state.marketing_campaigns:
        campaign_names = [c["name"] for c in st.session_state.marketing_campaigns]
        campaign_revenue = [c["revenue_generated"] for c in st.session_state.marketing_campaigns]
        
        fig = px.bar(x=campaign_names, y=campaign_revenue, 
                    title="Revenue by Campaign",
                    labels={"x": "Campaign", "y": "Revenue ($)"})
        st.plotly_chart(fig, use_container_width=True)
        
        # ROI comparison
        campaign_roi = [c["roi"] for c in st.session_state.marketing_campaigns]
        fig = px.line(x=campaign_names, y=campaign_roi, 
                     title="Campaign ROI Comparison",
                     labels={"x": "Campaign", "y": "ROI (%)"})
        st.plotly_chart(fig, use_container_width=True)

def show_sales_dashboard():
    st.markdown('<div class="sub-header">📈 Sales Performance</div>', unsafe_allow_html=True)
    
    # Sales metrics
    total_revenue = sum(b["amount"] for b in st.session_state.bookings + st.session_state.completed_bookings)
    monthly_revenue = total_revenue  # Simplified calculation
    average_booking_value = total_revenue / len(st.session_state.bookings + st.session_state.completed_bookings) if st.session_state.bookings else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col2:
        st.metric("Monthly Revenue", f"${monthly_revenue:,.0f}")
    with col3:
        st.metric("Avg Booking Value", f"${average_booking_value:,.0f}")
    
    # Revenue trend
    monthly_data = {}
    for booking in st.session_state.bookings + st.session_state.completed_bookings:
        month = booking["timestamp"][:7]  # YYYY-MM
        if month not in monthly_data:
            monthly_data[month] = 0
        monthly_data[month] += booking["amount"]
    
    if monthly_data:
        months = list(monthly_data.keys())
        revenue = list(monthly_data.values())
        
        fig = px.line(x=months, y=revenue, 
                     title="Monthly Revenue Trend",
                     labels={"x": "Month", "y": "Revenue ($)"})
        st.plotly_chart(fig, use_container_width=True)

def show_guest_insights():
    st.markdown('<div class="sub-header">👥 Guest Analytics</div>', unsafe_allow_html=True)
    
    # Guest demographics (simplified)
    guest_types = {
        "Business Travelers": 45,
        "Families": 25,
        "Couples": 20,
        "Tour Groups": 10
    }
    
    fig = px.pie(values=list(guest_types.values()), names=list(guest_types.keys()),
                title="Guest Type Distribution")
    st.plotly_chart(fig, use_container_width=True)
    
    # Repeat guest analysis
    repeat_guests = len([g for g in st.session_state.registered_users 
                        if g["role"] == "Guest" and len([b for b in st.session_state.completed_bookings 
                                                        if b["guest_email"] == g["email"]]) > 1])
    total_guests = len([g for g in st.session_state.registered_users if g["role"] == "Guest"])
    repeat_rate = (repeat_guests / total_guests * 100) if total_guests > 0 else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Guests", total_guests)
    with col2:
        st.metric("Repeat Guest Rate", f"{repeat_rate:.1f}%")

# ==================== MANAGER PORTAL ENHANCEMENTS ====================
def show_manager_portal():
    st.markdown('<div class="main-header">👨‍💼 Hotel Manager Dashboard</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📈 Analytics", "👥 User Management", "🤝 Vendor Management", "📊 Reports", 
        "⚙️ Configuration", "📋 Approvals", "💰 Financial Overview", "👨‍💼 Staff Scheduling", "📦 Inventory"
    ])
    
    with tab1:
        show_manager_analytics()
    with tab2:
        show_user_management()
    with tab3:
        show_vendor_management()
    with tab4:
        show_manager_reports()
    with tab5:
        show_system_config()
    with tab6:
        show_approval_system()
    with tab7:
        show_financial_overview()
    with tab8:
        show_staff_scheduling()  # NEW: Staff scheduling
    with tab9:
        show_inventory_management()  # NEW: Inventory management

def show_staff_scheduling():
    st.markdown('<div class="sub-header">👨‍💼 Staff Scheduling</div>', unsafe_allow_html=True)
    
    # Create new schedule
    with st.form("new_schedule_form"):
        st.markdown("#### Create New Schedule")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            staff_name = st.selectbox("Staff Member", 
                                    ["Emily Frontdesk", "Maria Cleaner", "Mike Technician", 
                                     "Sarah Catering", "Emma Events", "Alex Promoter"])
            role = st.selectbox("Role", 
                              ["Front Desk Officer", "Housekeeping Staff", "Maintenance Staff", 
                               "Catering Staff", "Event & Concierge Staff", "Marketing & Sales Staff"])
        
        with col2:
            schedule_date = st.date_input("Date", datetime.now() + timedelta(days=1))
            shift_start = st.time_input("Shift Start", datetime.strptime("08:00", "%H:%M").time())
        
        with col3:
            shift_end = st.time_input("Shift End", datetime.strptime("16:00", "%H:%M").time())
            status = st.selectbox("Status", ["Scheduled", "Confirmed", "Completed"])
        
        submitted = st.form_submit_button("📅 Create Schedule")
        
        if submitted:
            new_schedule = {
                "staff_name": staff_name,
                "role": role,
                "date": schedule_date.strftime("%Y-%m-%d"),
                "shift_start": shift_start.strftime("%H:%M"),
                "shift_end": shift_end.strftime("%H:%M"),
                "status": status
            }
            st.session_state.staff_schedules.append(new_schedule)
            add_notification(f"New schedule created for {staff_name}", "scheduling", [role])
            st.success(f"Schedule created for {staff_name} on {schedule_date}")
    
    # View existing schedules
    st.markdown("#### Current Schedules")
    if not st.session_state.staff_schedules:
        st.info("No staff schedules created.")
    else:
        # Filter schedules for the next 7 days
        next_week = datetime.now() + timedelta(days=7)
        upcoming_schedules = [s for s in st.session_state.staff_schedules 
                            if datetime.strptime(s["date"], "%Y-%m-%d") <= next_week]
        
        for schedule in upcoming_schedules:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                status_color = "success-card" if schedule["status"] == "Confirmed" else "warning-card" if schedule["status"] == "Scheduled" else "card"
                st.markdown(f"""
                <div class="card {status_color}">
                    <h4>{schedule['staff_name']} - {schedule['role']}</h4>
                    <p><strong>Date:</strong> {schedule['date']}</p>
                    <p><strong>Shift:</strong> {schedule['shift_start']} to {schedule['shift_end']}</p>
                    <p><strong>Status:</strong> {schedule['status']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Confirm", key=f"confirm_{schedule['staff_name']}_{schedule['date']}"):
                    schedule["status"] = "Confirmed"
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"delete_{schedule['staff_name']}_{schedule['date']}"):
                    st.session_state.staff_schedules.remove(schedule)
                    st.rerun()

def show_inventory_management():
    st.markdown('<div class="sub-header">📦 Inventory Management</div>', unsafe_allow_html=True)
    
    # Add new inventory item
    with st.form("new_inventory_form"):
        st.markdown("#### Add New Inventory Item")
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = st.text_input("Item Name *")
            category = st.selectbox("Category *", 
                                  ["Room Supplies", "Amenities", "Food & Beverage", "Cleaning Supplies", "Office Supplies"])
            supplier = st.text_input("Supplier *")
        
        with col2:
            quantity = st.number_input("Quantity *", min_value=0, value=100)
            min_quantity = st.number_input("Minimum Quantity *", min_value=1, value=50)
            unit_cost = st.number_input("Unit Cost ($) *", min_value=0.0, value=10.0, step=0.5)
        
        submitted = st.form_submit_button("📦 Add to Inventory")
        
        if submitted:
            if not all([item_name, category, supplier]):
                st.error("Please fill in all required fields (*)")
            else:
                item_id = f"INV{len(st.session_state.inventory) + 1:03d}"
                new_item = {
                    "item_id": item_id,
                    "name": item_name,
                    "category": category,
                    "quantity": quantity,
                    "min_quantity": min_quantity,
                    "unit_cost": unit_cost,
                    "supplier": supplier,
                    "last_ordered": datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.inventory.append(new_item)
                st.success(f"Inventory item '{item_name}' added successfully!")
    
    # Inventory overview
    st.markdown("#### Current Inventory")
    if not st.session_state.inventory:
        st.info("No inventory items.")
    else:
        # Low stock alert
        low_stock_items = [item for item in st.session_state.inventory if item["quantity"] <= item["min_quantity"]]
        if low_stock_items:
            st.warning(f"⚠️ {len(low_stock_items)} items are running low on stock!")
        
        for item in st.session_state.inventory:
            status_color = "critical-card" if item["quantity"] <= item["min_quantity"] else "success-card" if item["quantity"] > item["min_quantity"] * 2 else "warning-card"
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="card {status_color}">
                    <h4>{item['name']} ({item['category']})</h4>
                    <p><strong>Quantity:</strong> {item['quantity']} | <strong>Min:</strong> {item['min_quantity']}</p>
                    <p><strong>Unit Cost:</strong> ${item['unit_cost']} | <strong>Supplier:</strong> {item['supplier']}</p>
                    <p><strong>Last Ordered:</strong> {item['last_ordered']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                new_quantity = st.number_input("Update Qty", min_value=0, value=item["quantity"], 
                                             key=f"qty_{item['item_id']}")
                if st.button("Update", key=f"update_{item['item_id']}"):
                    item["quantity"] = new_quantity
                    st.rerun()
            with col3:
                if st.button("Reorder", key=f"reorder_{item['item_id']}"):
                    item["last_ordered"] = datetime.now().strftime("%Y-%m-%d")
                    item["quantity"] += item["min_quantity"] * 2  # Reorder 2x min quantity
                    add_notification(f"Reorder placed for {item['name']}", "inventory", ["Hotel Manager"])
                    st.success(f"Reorder placed for {item['name']}!")
                    st.rerun()

# ==================== BILLING PORTAL FIXES ====================
def show_billing_portal():
    st.markdown('<div class="main-header">💰 Billing & Invoicing Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Pending Invoices", "💰 Payment Processing", "📝 Cancellation Refunds", "🤝 Vendor Payments", "📊 Vendor Payment History"])
    
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
                    <p><strong>Current Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### Refund Calculation")
                
                # FIXED: Calculate refund based on actual cancellation timing
                try:
                    request_datetime = datetime.strptime(request['request_date'], "%Y-%m-%d %H:%M:%S")
                    current_datetime = datetime.now()
                    
                    # Parse check-in date properly
                    if ' ' in booking["check_in"]:
                        check_in_datetime = datetime.strptime(booking["check_in"], "%Y-%m-%d %H:%M")
                    else:
                        check_in_datetime = datetime.strptime(booking["check_in"], "%Y-%m-%d")
                    
                    hours_until_checkin = (check_in_datetime - current_datetime).total_seconds() / 3600
                    
                    # Determine refund percentage based on timing
                    if hours_until_checkin >= 48:
                        refund_percentage = 0.5  # 50% refund for 48+ hours notice
                        refund_reason = "Standard cancellation (48+ hours notice)"
                    elif request["amount_paid"] == 0:
                        refund_percentage = 1.0  # Full refund if not paid
                        refund_reason = "Free cancellation (not paid)"
                    elif hours_until_checkin >= 2:
                        refund_percentage = 0.25  # 25% refund for 2-48 hours notice
                        refund_reason = "Short notice cancellation (2-48 hours)"
                    else:
                        refund_percentage = 0.0  # No refund for late cancellation
                        refund_reason = "Late cancellation (no refund)"
                    
                    refund_amount = request["amount_paid"] * refund_percentage
                    processing_fee = refund_amount * 0.02  # 2% processing fee
                    net_refund = refund_amount - processing_fee
                    
                    st.write(f"**Time until check-in:** {hours_until_checkin:.1f} hours")
                    st.write(f"**Refund Reason:** {refund_reason}")
                    st.write(f"**Refund Amount:** ${refund_amount:.2f}")
                    st.write(f"**Processing Fee (2%):** ${processing_fee:.2f}")
                    st.write(f"**Net Refund:** ${net_refund:.2f}")
                    
                    # Update request with calculated values
                    request["refund_amount"] = net_refund
                    request["processing_fee"] = processing_fee
                    request["refund_reason"] = refund_reason
                    request["calculated_at"] = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    
                except Exception as e:
                    st.error(f"Error calculating refund: {e}")
                    continue
                
                if st.button("✅ Process Refund", key=f"refund_{request['booking_id']}"):
                    # Process refund
                    request["status"] = "Processed"
                    request["processed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    request["processed_by"] = st.session_state.current_user['name']
                    
                    # Update booking status
                    booking["status"] = "Cancelled"
                    booking["cancellation_status"] = "Processed"
                    
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

# ==================== STAFF PERFORMANCE TRACKING ====================
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
    
    # Staff Performance Section
    st.markdown("#### Staff Performance Overview")
    
    if st.session_state.staff_performance:
        # Create performance chart
        staff_names = [p["staff_name"] for p in st.session_state.staff_performance]
        efficiency_scores = [p["efficiency_score"] for p in st.session_state.staff_performance]
        avg_ratings = [p["avg_rating"] for p in st.session_state.staff_performance]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Efficiency Score', x=staff_names, y=efficiency_scores))
        fig.add_trace(go.Scatter(name='Average Rating', x=staff_names, y=avg_ratings, 
                                yaxis='y2', mode='lines+markers', line=dict(color='red')))
        
        fig.update_layout(
            title='Staff Performance Metrics',
            yaxis=dict(title='Efficiency Score (%)'),
            yaxis2=dict(title='Average Rating', overlaying='y', side='right')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed performance table
        st.markdown("#### Detailed Performance Metrics")
        performance_data = []
        for performance in st.session_state.staff_performance:
            performance_data.append({
                "Staff Name": performance["staff_name"],
                "Role": performance["role"],
                "Tasks Completed": performance["tasks_completed"],
                "Avg Rating": performance["avg_rating"],
                "Efficiency Score": f"{performance['efficiency_score']}%",
                "Guest Compliments": performance["guest_compliments"]
            })
        
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True)
    
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

# ==================== OTHER PORTAL FUNCTIONS ====================
# Note: Other existing functions (show_front_desk_portal, show_housekeeping_portal, etc.)
# remain largely the same but would include the new features where relevant

def show_event_concierge_portal():
    st.markdown('<div class="main-header">🎉 Event & Concierge Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Assigned Tasks", "📅 Event Calendar", "👥 Guest Meetings"])
    
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
                        add_notification(f"Event/Concierge task {task['id']} completed", "task")
                        st.rerun()
    
    with tab2:
        st.markdown("#### Upcoming Events")
        events = [
            {"name": "Corporate Conference", "date": "2024-02-15", "guests": 80, "status": "Confirmed"},
            {"name": "Wedding Reception", "date": "2024-02-20", "guests": 120, "status": "Planning"},
        ]
        
        for event in events:
            st.markdown(f"""
            <div class="card">
                <h4>{event['name']}</h4>
                <p>Date: {event['date']} | Guests: {event['guests']}</p>
                <p>Status: {event['status']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("#### Scheduled Guest Meetings")
        guest_meetings = [m for m in st.session_state.staff_meetings 
                         if m["staff_member"] in ["Event Planner", "Concierge"]]
        
        if not guest_meetings:
            st.info("No guest meetings scheduled.")
        else:
            for meeting in guest_meetings:
                st.markdown(f"""
                <div class="card">
                    <h4>{meeting['title']}</h4>
                    <p><strong>Guest:</strong> {meeting['guest']}</p>
                    <p><strong>Date:</strong> {meeting['date']} at {meeting['time']}</p>
                    <p><strong>Duration:</strong> {meeting['duration']} minutes</p>
                    <p><strong>Location:</strong> {meeting['room']}</p>
                    <p><strong>Agenda:</strong> {meeting.get('agenda', 'Not specified')}</p>
                </div>
                """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()