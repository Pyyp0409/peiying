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
        'bookings': [],
        'rooms': [
            {"number": "101", "type": "Single", "status": "occupied", "guest": "John Smith", "price": 150},
            {"number": "102", "type": "Double", "status": "vacant", "guest": "", "price": 200},
            {"number": "103", "type": "Suite", "status": "cleaning", "guest": "", "price": 350},
            {"number": "201", "type": "Single", "status": "occupied", "guest": "Sarah Johnson", "price": 150},
            {"number": "202", "type": "Double", "status": "maintenance", "guest": "", "price": 200},
            {"number": "203", "type": "Suite", "status": "vacant", "guest": "", "price": 350},
            {"number": "301", "type": "Deluxe", "status": "occupied", "guest": "Mike Brown", "price": 500},
            {"number": "302", "type": "Deluxe", "status": "vacant", "guest": "", "price": 500},
        ],
        'service_requests': [],
        'invoices': [],
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
            {"email": "vendor@demo.com", "name": "Tom Suppliers", "role": "Vendor", "status": "Pending", "registration_date": "2024-01-01", "password": "vendor123"},  # Changed to Pending
            {"email": "catering@demo.com", "name": "Sarah Catering", "role": "Catering Staff", "status": "Active", "registration_date": "2024-01-01", "password": "catering123"},
            {"email": "events@demo.com", "name": "Emma Events", "role": "Event & Concierge Staff", "status": "Active", "registration_date": "2024-01-01", "password": "events123"},
        ],
        'reviews': [
            {"guest": "John Traveler", "room": "101", "ratings": {"overall": 5, "cleanliness": 5, "service": 4, "comfort": 5}, "comments": "Excellent stay! The room was spacious and clean.", "timestamp": "2024-01-15 10:30:00"},
            {"guest": "Sarah Visitor", "room": "201", "ratings": {"overall": 4, "cleanliness": 4, "service": 5, "comfort": 4}, "comments": "Great service and comfortable beds. Will come back!", "timestamp": "2024-01-20 14:45:00"},
            {"guest": "Mike Brown", "room": "301", "ratings": {"overall": 5, "cleanliness": 5, "service": 5, "comfort": 5}, "comments": "Perfect experience from check-in to check-out. Highly recommended!", "timestamp": "2024-02-01 09:15:00"}
        ],
        'tasks': [],
        'vendors': [
            {"name": "ABC Laundry", "service": "Linens", "status": "Approved", "contact": "contact@abclaundry.com", "registration_date": "2024-01-01", "service_fee": 5.0, "monthly_earnings": 0, "services_completed": 0},
            {"name": "XYZ Catering", "service": "Food Service", "status": "Approved", "contact": "info@xyzcatering.com", "registration_date": "2024-01-02", "service_fee": 7.5, "monthly_earnings": 0, "services_completed": 0}
        ],
        'vendor_services': [],
        'vendor_statements': [],
        'cancellation_requests': [],
        'refund_requests': []
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

# ==================== GUEST PORTAL ====================
def show_guest_portal():
    st.markdown('<div class="main-header">👤 Guest Portal - Grand Stay Hotel</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Book Room", "📋 My Bookings", "🛎️ Service Requests", "⭐ Leave Review", "📝 Recent Reviews"])
    
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

def show_guest_bookings():
    st.markdown('<div class="sub-header">📋 My Bookings</div>', unsafe_allow_html=True)
    
    guest_bookings = [b for b in st.session_state.bookings if b["guest_email"] == st.session_state.current_user['email']]
    
    if not guest_bookings:
        st.info("You have no current bookings.")
        return
    
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

def show_guest_service_requests():
    st.markdown('<div class="sub-header">🛎️ Service Requests</div>', unsafe_allow_html=True)
    
    service_type = st.selectbox("Service Type", 
                               ["Housekeeping", "Room Service", "Maintenance", "Concierge", "Transportation"])
    
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

def show_guest_reviews():
    st.markdown('<div class="sub-header">⭐ Share Your Experience</div>', unsafe_allow_html=True)
    
    # Check if user has completed stays to review
    completed_stays = [b for b in st.session_state.bookings 
                      if b["guest_email"] == st.session_state.current_user['email'] 
                      and b["status"] == "Completed"]
    
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
    
    # Find vendor details
    vendor_email = st.session_state.current_user['email']
    vendor_info = None
    
    for vendor in st.session_state.vendors:
        if vendor["contact"] == vendor_email:
            vendor_info = vendor
            break
    
    if vendor_info:
        if vendor_info["status"] == "Approved":
            tab1, tab2, tab3 = st.tabs(["🏢 Dashboard", "💰 Statements & Payments", "📊 Performance"])
            
            with tab1:
                show_vendor_dashboard(vendor_info)
            with tab2:
                show_vendor_statements(vendor_info)
            with tab3:
                show_vendor_performance(vendor_info)
        else:
            st.warning("⏳ Your vendor application is pending approval. You will gain access to the vendor portal once approved.")
            st.info("Please check back later or contact the hotel management for updates.")
    else:
        st.error("Vendor account not found. Please contact support.")

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
                <p><strong>Service Fee:</strong> ${service['service_fee']:.2f}</p>
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

# ==================== BILLING PORTAL ====================
def show_billing_portal():
    st.markdown('<div class="main-header">💰 Billing & Invoicing Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Pending Invoices", "💰 Payment Processing", "📝 Cancellation Refunds", "🤝 Vendor Payments"])
    
    with tab1:
        show_pending_invoices()
    with tab2:
        show_payment_processing()
    with tab3:
        show_cancellation_refunds()
    with tab4:
        show_vendor_payments()

def show_pending_invoices():
    st.markdown('<div class="sub-header">📋 Outstanding Invoices</div>', unsafe_allow_html=True)
    
    pending_invoices = [inv for inv in st.session_state.invoices if inv["status"] == "Pending"]
    
    if not pending_invoices:
        st.info("No pending invoices.")
        return
    
    for invoice in pending_invoices:
        col1, col2, col3 = st.columns([3, 1, 1])
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
                add_notification(f"Invoice {invoice['id']} marked as paid", "payment")
                st.success(f"Invoice {invoice['id']} marked as paid!")
                st.rerun()
        with col3:
            if st.button("📧 Send Reminder", key=f"remind_{invoice['id']}"):
                add_notification(f"Payment reminder sent for invoice {invoice['id']}", "reminder")
                st.success(f"Payment reminder sent for invoice {invoice['id']}!")

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

# ==================== MANAGER PORTAL ====================
def show_manager_portal():
    st.markdown('<div class="main-header">👨‍💼 Hotel Manager Dashboard</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📈 Analytics", "👥 User Management", "🤝 Vendor Management", "📊 Reports", "⚙️ Configuration", "📋 Approvals", "💰 Financial Overview"])
    
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

def show_financial_overview():
    st.markdown('<div class="sub-header">💰 Financial Overview</div>', unsafe_allow_html=True)
    
    # Financial metrics
    total_revenue = sum(b["amount"] for b in st.session_state.bookings if b.get("payment_status") == "Paid")
    pending_payments = sum(b["amount"] for b in st.session_state.bookings if b.get("payment_status") == "Pending")
    vendor_payments = sum(s["amount"] for s in st.session_state.vendor_statements)
    refunds_processed = sum(r["refund_amount"] for r in st.session_state.refund_requests)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col2:
        st.metric("Pending Payments", f"${pending_payments:,.0f}")
    with col3:
        st.metric("Vendor Payments", f"${vendor_payments:,.0f}")
    with col4:
        st.metric("Refunds Processed", f"${refunds_processed:,.0f}")
    
    # Monthly revenue trend
    st.markdown("#### Revenue Trend")
    monthly_revenue = {}
    for booking in st.session_state.bookings:
        if booking.get("payment_status") == "Paid" and "timestamp" in booking:
            month = booking["timestamp"][:7]  # YYYY-MM
            if month not in monthly_revenue:
                monthly_revenue[month] = 0
            monthly_revenue[month] += booking["amount"]
    
    if monthly_revenue:
        months = list(monthly_revenue.keys())
        revenue = list(monthly_revenue.values())
        
        fig = px.line(x=months, y=revenue, 
                     title="Monthly Revenue Trend",
                     labels={"x": "Month", "y": "Revenue ($)"})
        st.plotly_chart(fig, use_container_width=True)

# ==================== OTHER PORTAL FUNCTIONS ====================
# Note: Other portal functions (Front Desk, Housekeeping, Maintenance, Catering, Event) remain mostly the same
# but with added vendor service tracking when tasks are completed

def show_front_desk_portal():
    st.markdown('<div class="main-header">🏢 Front Desk Operations Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🛏️ Room Management", "👥 Check-In/Out", "📋 Request Queue", "🎯 Task Assignment"])
    
    with tab1:
        show_front_desk_dashboard()
    with tab2:
        show_room_management()
    with tab3:
        show_checkin_checkout()
    with tab4:
        show_request_queue()
    with tab5:
        show_task_assignment()

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
        new_status = st.selectbox("New Status", ["occupied", "vacant", "cleaning", "maintenance"])
    with col2:
        guest_name = st.text_input("Guest Name (if occupied)")
        if st.button("🔄 Update Room Status", use_container_width=True):
            for room in st.session_state.rooms:
                if room["number"] == room_number:
                    room["status"] = new_status
                    room["guest"] = guest_name if new_status == "occupied" else ""
                    add_notification(f"Room {room_number} status updated to {new_status}", "update")
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
        
        if st.button("✅ Complete Check-In", use_container_width=True):
            # Update room status
            for room in st.session_state.rooms:
                if room["number"] == assigned_room:
                    room["status"] = "occupied"
                    room["guest"] = guest_name
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
                    st.success("Check-out completed successfully! Room assigned for cleaning.")
                    break

def show_request_queue():
    st.markdown('<div class="sub-header">📋 Service Request Queue</div>', unsafe_allow_html=True)
    
    pending_requests = [r for r in st.session_state.service_requests if r["status"] == "Pending"]
    
    if not pending_requests:
        st.info("No pending service requests.")
        return
    
    for request in pending_requests:
        # FIXED: Complete urgency mapping including "Critical"
        urgency_color = {
            "Critical": "critical-card", 
            "High": "critical-card", 
            "Medium": "warning-card", 
            "Low": "card"
        }.get(request["urgency"], "card")
        
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"""
            <div class="card {urgency_color}">
                <h4>{request['type']} - Room {request['room']}</h4>
                <p>Guest: {request['guest']}</p>
                <p>Details: {request['details']}</p>
                <p>Urgency: {request['urgency']} | Submitted: {request['timestamp']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Assign to available vendors based on service type
            available_vendors = [v for v in st.session_state.vendors 
                                if v["status"] == "Approved" 
                                and (request['type'].lower() in v['service'].lower() or v['service'] == "Maintenance")]
            vendor_options = ["Housekeeping", "Maintenance", "Catering", "Event & Concierge"] + [v["name"] for v in available_vendors]
            assign_to = st.selectbox(f"Assign to", vendor_options, key=f"assign_{request['id']}")
        
        with col3:
            if st.button("✅ Complete", key=f"complete_{request['id']}"):
                request["status"] = "Completed"
                
                # If assigned to a vendor, record the service
                if assign_to in [v["name"] for v in available_vendors]:
                    vendor = next(v for v in available_vendors if v["name"] == assign_to)
                    service_id = f"VS{len(st.session_state.vendor_services) + 1:03d}"
                    service_fee = (100 * vendor["service_fee"]) / 100  # Calculate service fee amount
                    
                    vendor_service = {
                        "id": service_id,
                        "vendor_name": vendor["name"],
                        "service_type": request["type"],
                        "location": f"Room {request['room']}",
                        "amount": 100,  # Base service amount
                        "service_fee": service_fee,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "status": "Completed"
                    }
                    st.session_state.vendor_services.append(vendor_service)
                
                add_notification(f"Service request {request['id']} completed", "service")
                st.success(f"Request {request['id']} marked as completed!")
                st.rerun()

def show_task_assignment():
    st.markdown('<div class="sub-header">🎯 Manual Task Assignment</div>', unsafe_allow_html=True)
    
    # Show bookings with special requests
    special_request_bookings = [b for b in st.session_state.bookings if b.get('special_requests')]
    
    if not special_request_bookings:
        st.info("No bookings with special requests requiring manual assignment.")
        return
    
    for booking in special_request_bookings:
        st.markdown(f"""
        <div class="card warning-card">
            <h4>Booking #{booking['id']} - {booking['guest']}</h4>
            <p><strong>Room Type:</strong> {booking['room_type']}</p>
            <p><strong>Special Requests:</strong> {booking['special_requests']}</p>
            <p><strong>Check-in:</strong> {booking['check_in']} | <strong>Check-out:</strong> {booking['check_out']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Task assignment options including vendors
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button(f"🧹 Housekeeping", key=f"house_{booking['id']}"):
                task_id = f"TK{len(st.session_state.tasks) + 1:03d}"
                new_task = {
                    "id": task_id,
                    "type": "Special Housekeeping",
                    "room": "TBD",
                    "assigned_to": "Housekeeping",
                    "status": "Pending",
                    "description": f"Special request: {booking['special_requests']} for {booking['guest']}",
                    "booking_id": booking['id'],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.tasks.append(new_task)
                add_notification(f"New housekeeping task assigned: {task_id}", "task", ["Housekeeping Staff"])
                st.success(f"Task assigned to Housekeeping team!")
                st.rerun()
        
        with col2:
            if st.button(f"🔧 Maintenance", key=f"maint_{booking['id']}"):
                task_id = f"TK{len(st.session_state.tasks) + 1:03d}"
                new_task = {
                    "id": task_id,
                    "type": "Special Maintenance",
                    "room": "TBD",
                    "assigned_to": "Maintenance",
                    "status": "Pending",
                    "description": f"Special request: {booking['special_requests']} for {booking['guest']}",
                    "booking_id": booking['id'],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.tasks.append(new_task)
                add_notification(f"New maintenance task assigned: {task_id}", "task", ["Maintenance Staff"])
                st.success(f"Task assigned to Maintenance team!")
                st.rerun()
        
        with col3:
            if st.button(f"🍽️ Catering", key=f"cater_{booking['id']}"):
                task_id = f"TK{len(st.session_state.tasks) + 1:03d}"
                new_task = {
                    "id": task_id,
                    "type": "Catering Service",
                    "room": "TBD",
                    "assigned_to": "Catering",
                    "status": "Pending",
                    "description": f"Special request: {booking['special_requests']} for {booking['guest']}",
                    "booking_id": booking['id'],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.tasks.append(new_task)
                add_notification(f"New catering task assigned: {task_id}", "task", ["Catering Staff"])
                st.success(f"Task assigned to Catering team!")
                st.rerun()
        
        with col4:
            if st.button(f"🎉 Event/Concierge", key=f"event_{booking['id']}"):
                task_id = f"TK{len(st.session_state.tasks) + 1:03d}"
                new_task = {
                    "id": task_id,
                    "type": "Event/Concierge Service",
                    "room": "TBD",
                    "assigned_to": "Event & Concierge",
                    "status": "Pending",
                    "description": f"Special request: {booking['special_requests']} for {booking['guest']}",
                    "booking_id": booking['id'],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.tasks.append(new_task)
                add_notification(f"New event/concierge task assigned: {task_id}", "task", ["Event & Concierge Staff"])
                st.success(f"Task assigned to Event & Concierge team!")
                st.rerun()
        
        st.markdown("---")

# ==================== HOUSEKEEPING PORTAL ====================
def show_housekeeping_portal():
    st.markdown('<div class="main-header">🧹 Housekeeping Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Assigned Tasks", "✅ Task Completion"])
    
    with tab1:
        st.markdown('<div class="sub-header">🛏️ Cleaning Schedule</div>', unsafe_allow_html=True)
        
        housekeeping_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == "Housekeeping" and t["status"] == "Pending"]
        
        if not housekeeping_tasks:
            st.info("No tasks assigned.")
            return
        
        for task in housekeeping_tasks:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="card warning-card">
                    <h4>{task['type']} - Room {task['room']}</h4>
                    <p>{task['description']}</p>
                    <p>Assigned: {task['timestamp']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Start", key=f"start_{task['id']}"):
                    task["status"] = "In Progress"
                    st.rerun()
            with col3:
                if st.button("Complete", key=f"complete_{task['id']}"):
                    task["status"] = "Completed"
                    # Update room status
                    for room in st.session_state.rooms:
                        if room["number"] == task["room"] and task["type"] == "Cleaning":
                            room["status"] = "vacant"
                    add_notification(f"Housekeeping task {task['id']} completed for Room {task['room']}", "task")
                    st.rerun()

# ==================== MAINTENANCE PORTAL ====================
def show_maintenance_portal():
    st.markdown('<div class="main-header">🔧 Maintenance Portal</div>', unsafe_allow_html=True)
    
    maintenance_requests = [r for r in st.session_state.service_requests if r["type"] == "Maintenance" and r["status"] == "Pending"]
    
    if not maintenance_requests:
        st.info("No maintenance requests.")
        return
    
    for request in maintenance_requests:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            # FIXED: Complete urgency mapping including "Critical"
            urgency_color = {
                "Critical": "critical-card", 
                "High": "critical-card", 
                "Medium": "warning-card", 
                "Low": "card"
            }.get(request["urgency"], "card")
            
            st.markdown(f"""
            <div class="card {urgency_color}">
                <h4>Maintenance - Room {request['room']}</h4>
                <p>Issue: {request['details']}</p>
                <p>Guest: {request['guest']}</p>
                <p>Urgency: {request['urgency']}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("Start Work", key=f"start_{request['id']}"):
                request["status"] = "In Progress"
                st.rerun()
        with col3:
            if st.button("Complete", key=f"complete_{request['id']}"):
                request["status"] = "Completed"
                add_notification(f"Maintenance completed for Room {request['room']}", "maintenance")
                st.rerun()

# ==================== CATERING PORTAL ====================
def show_catering_portal():
    st.markdown('<div class="main-header">🍽️ Catering Services Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Assigned Tasks", "📊 Kitchen Operations"])
    
    with tab1:
        st.markdown('<div class="sub-header">🍳 Catering Tasks</div>', unsafe_allow_html=True)
        
        catering_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == "Catering"]
        
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
                if task["status"] == "In Progress":
                    if st.button("Complete", key=f"complete_{task['id']}"):
                        task["status"] = "Completed"
                        add_notification(f"Catering task {task['id']} completed", "task")
                        st.rerun()
    
    with tab2:
        st.markdown("#### Kitchen Performance")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Today's Orders", "18")
        with col2:
            st.metric("Preparation Time", "22 min")
        with col3:
            st.metric("Guest Satisfaction", "4.7/5")

# ==================== EVENT & CONCIERGE PORTAL ====================
def show_event_concierge_portal():
    st.markdown('<div class="main-header">🎉 Event & Concierge Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Assigned Tasks", "📅 Event Calendar"])
    
    with tab1:
        st.markdown('<div class="sub-header">🎊 Event & Concierge Tasks</div>', unsafe_allow_html=True)
        
        event_tasks = [t for t in st.session_state.tasks if t["assigned_to"] == "Event & Concierge"]
        
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
                if task["status"] == "In Progress":
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

# ==================== MANAGER PORTAL FUNCTIONS ====================
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
                        "services_completed": 0
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
    
    # Calculate metrics
    total_rooms = len(st.session_state.rooms)
    occupied = len([r for r in st.session_state.rooms if r["status"] == "occupied"])
    revenue = sum(b["amount"] for b in st.session_state.bookings if b["status"] == "Confirmed")
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
        # Revenue trend (sample data)
        revenue_data = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Revenue': [125000, 118000, 132000, 145000, 158000, revenue/1000]
        }
        fig = px.line(revenue_data, x='Month', y='Revenue', title='Monthly Revenue Trend (in $1000)')
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

def show_vendor_management():
    st.markdown('<div class="sub-header">🤝 Vendor Management</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Vendor Approval", "Current Vendors"])
    
    with tab1:
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
                    # FIXED: Use unique key with index
                    if st.button("✅ Approve", key=f"approve_vendor_{idx}"):
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
                            "services_completed": 0
                        })
                        # Update user status
                        for user in st.session_state.registered_users:
                            if user["email"] == vendor["email"]:
                                user["status"] = "Active"
                        add_notification(f"Vendor {vendor['name']} approved", "vendor_approval", ["Vendor"])
                        st.rerun()
                with col3:
                    # FIXED: Use unique key with index
                    if st.button("❌ Reject", key=f"reject_vendor_{idx}"):
                        vendor["status"] = "Rejected"
                        # Update user status
                        for user in st.session_state.registered_users:
                            if user["email"] == vendor["email"]:
                                user["status"] = "Rejected"
                        st.rerun()
    
    with tab2:
        st.markdown("#### Approved Vendors")
        approved_vendors = [v for v in st.session_state.vendors if v["status"] == "Approved"]
        
        if not approved_vendors:
            st.info("No approved vendors.")
        else:
            for vendor in approved_vendors:
                st.markdown(f"""
                <div class="card success-card">
                    <h4>{vendor['name']}</h4>
                    <p>Service: {vendor['service']}</p>
                    <p>Contact: {vendor['contact']}</p>
                    <p>Service Fee: {vendor['service_fee']}%</p>
                    <p>Services Completed: {vendor['services_completed']}</p>
                    <p>Monthly Earnings: ${vendor['monthly_earnings']:,.2f}</p>
                    <p>Status: {vendor['status']}</p>
                </div>
                """, unsafe_allow_html=True)

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
                              [datetime.now() - timedelta(days=30), datetime.now()])
    
    if st.button("📥 Download Report", use_container_width=True):
        # Generate sample report data
        report_data = pd.DataFrame({
            'Metric': ['Total Revenue', 'Average Occupancy', 'RevPAR', 'Guest Satisfaction', 'Staff Performance'],
            'Value': [f"${sum(b['amount'] for b in st.session_state.bookings):,.0f}", 
                     f"{(len([r for r in st.session_state.rooms if r['status'] == 'occupied'])/len(st.session_state.rooms))*100:.1f}%",
                     f"${(sum(b['amount'] for b in st.session_state.bookings)/len(st.session_state.rooms)):.0f}",
                     '4.6/5.0', '92%'],
        })
        
        # Create download button
        csv = report_data.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Report as CSV",
            data=csv,
            file_name=f"{report_type.replace(' ', '_').lower()}.csv",
            mime="text/csv",
        )
        st.success("Report generated successfully!")

def show_system_config():
    st.markdown('<div class="sub-header">⚙️ System Configuration</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Room Rates")
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

# Run the application
if __name__ == "__main__":
    main()