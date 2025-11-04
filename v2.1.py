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

# Page configuration
st.set_page_config(
    page_title="Grand Stay Hotel Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with the new color scheme
st.markdown("""
<style>
    :root {
        --primary: #A0D2E8;
        --secondary: #E5EAF5;
        --accent: #D0BDF4;
        --dark-accent: #8458B3;
        --dark-bg: #494D5F;
        --text-light: #FFFFFF;
        --text-dark: #2C3E50;
    }
    
    .stApp {
        background-color:#e5eaf5;
    }
    
    .main .block-container {
        padding-top: 2rem;
        background-color: var(--dark-bg);
    }
    
    .main-header {
        font-size: 3.5rem;
        color: var(--text-light);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Playfair Display', serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        padding: 2rem;
        border-radius: 20px;
        background: linear-gradient(145deg, var(--dark-bg), var(--dark-accent));
        box-shadow: 0 12px 35px rgba(0,0,0,0.3);
        border: 1px solid var(--accent);
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: var(--primary);
        margin-bottom: 1.5rem;
        font-weight: 500;
        border-bottom: 3px solid var(--accent);
        padding-bottom: 0.8rem;
        font-family: 'Montserrat', sans-serif;
    }
    
    .card {
        background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
        color: var(--text-dark);
        padding: 1.8rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        margin-bottom: 1.5rem;
        border-left: 5px solid var(--dark-accent);
        border: 1px solid var(--accent);
    }
    
    .success-card {
        border-left: 5px solid #27AE60;
        background: linear-gradient(135deg, var(--secondary) 0%, #27AE60 100%);
        color: var(--text-dark);
    }
    
    .warning-card {
        border-left: 5px solid #F39C12;
        background: linear-gradient(135deg, var(--secondary) 0%, #F39C12 100%);
        color: var(--text-dark);
    }
    
    .critical-card {
        border-left: 5px solid #E74C3C;
        background: linear-gradient(135deg, var(--secondary) 0%, #E74C3C 100%);
        color: var(--text-dark);
    }
    
    .demo-account {
        background: linear-gradient(135deg, var(--accent) 0%, var(--dark-accent) 100%);
        color: var(--text-light);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
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
    
    .elegant-cover {
        background: linear-gradient(135deg, var(--dark-accent) 0%, var(--dark-bg) 100%);
        padding: 4rem 2rem;
        border-radius: 25px;
        text-align: center;
        color: var(--text-light);
        margin-bottom: 3rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border: 2px solid var(--accent);
        position: relative;
        overflow: hidden;
    }
    
    .elegant-cover::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 0%, var(--primary) 100%);
        opacity: 0.1;
    }
    
    .elegant-title {
        font-size: 4.5rem;
        font-weight: 300;
        font-family: 'Playfair Display', serif;
        margin-bottom: 1rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
        background: linear-gradient(135deg, var(--primary) 0%, var(--text-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .elegant-subtitle {
        font-size: 1.8rem;
        font-weight: 300;
        opacity: 0.9;
        font-family: 'Montserrat', sans-serif;
        color: var(--secondary);
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, var(--dark-accent) 0%, var(--dark-bg) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: var(--text-light);
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid var(--accent);
    }
    
    .stButton button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--dark-accent) 100%);
        color: var(--text-light);
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, var(--dark-accent) 0%, var(--accent) 100%);
        color: var(--text-light);
    }
    
    .tab-content {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
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
        {"email": "guest2@demo.com", "password": "guest123", "name": "Sarah Visitor"},
        {"email": "guest3@demo.com", "password": "guest123", "name": "Michael Explorer"},
        {"email": "guest4@demo.com", "password": "guest123", "name": "Emily Adventurer"}
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
    "Executive Chef": [
        {"email": "chef@demo.com", "password": "chef123", "name": "Gordon Chef"}
    ],
    "Event Coordinator": [
        {"email": "events@demo.com", "password": "events123", "name": "Emma Events"}
    ]
}

# Real-time data storage with enhanced functionality
def init_session_data():
    if 'bookings' not in st.session_state:
        st.session_state.bookings = []
    if 'rooms' not in st.session_state:
        st.session_state.rooms = [
            {"number": "101", "type": "Single", "status": "occupied", "guest": "John Smith"},
            {"number": "102", "type": "Double", "status": "vacant", "guest": ""},
            {"number": "103", "type": "Suite", "status": "cleaning", "guest": ""},
            {"number": "201", "type": "Single", "status": "occupied", "guest": "Sarah Johnson"},
            {"number": "202", "type": "Double", "status": "maintenance", "guest": ""},
            {"number": "203", "type": "Suite", "status": "vacant", "guest": ""},
            {"number": "301", "type": "Deluxe", "status": "occupied", "guest": "Mike Brown"},
            {"number": "302", "type": "Deluxe", "status": "vacant", "guest": ""},
            {"number": "303", "type": "Suite", "status": "vacant", "guest": ""},
            {"number": "401", "type": "Single", "status": "vacant", "guest": ""},
            {"number": "402", "type": "Double", "status": "occupied", "guest": "Robert Wilson"},
            {"number": "403", "type": "Suite", "status": "cleaning", "guest": ""},
        ]
    if 'service_requests' not in st.session_state:
        st.session_state.service_requests = []
    if 'invoices' not in st.session_state:
        st.session_state.invoices = []
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    if 'staff_applications' not in st.session_state:
        st.session_state.staff_applications = []
    if 'vendor_applications' not in st.session_state:
        st.session_state.vendor_applications = []
    if 'guest_applications' not in st.session_state:
        st.session_state.guest_applications = []
    if 'reviews' not in st.session_state:
        st.session_state.reviews = []

# Add notification function
def add_notification(message, category="info"):
    notification = {
        "id": len(st.session_state.notifications) + 1,
        "message": message,
        "category": category,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False
    }
    st.session_state.notifications.append(notification)

# Authentication system
def authenticate_user(email, password, role):
    for account_role, accounts in DEMO_ACCOUNTS.items():
        if role == account_role:
            for account in accounts:
                if account["email"] == email and account["password"] == password:
                    return account
    return None

# Main application
def main():
    # Initialize session data
    init_session_data()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'current_role' not in st.session_state:
        st.session_state.current_role = None
    if 'supabase' not in st.session_state:
        st.session_state.supabase = init_supabase()

    # Show login page if not authenticated
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_application()

def show_login_page():
    st.markdown("""
    <div class="elegant-cover">
        <div class="elegant-title">🏨 Grand Stay Hotel</div>
        <div class="elegant-subtitle">Premium Luxury Hospitality Experience</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Application options
    app_type = st.radio("Select Application Type", 
                       ["🏨 Book Hotel Stay", "👥 Apply for Guest Account", "💼 Apply for Job Position", "🤝 Apply as Vendor"],
                       horizontal=True)
    
    if app_type == "🏨 Book Hotel Stay":
        show_hotel_login()
    else:
        show_application_form(app_type)

def show_hotel_login():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="sub-header">🔐 System Login</div>', unsafe_allow_html=True)
        
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
                st.error("Invalid credentials. Please use demo accounts below.")
    
    with col2:
        st.markdown('<div class="sub-header">👥 Demo Accounts</div>', unsafe_allow_html=True)
        st.info("Use these demo accounts to explore the system:")
        
        for role_name, accounts in DEMO_ACCOUNTS.items():
            with st.expander(f"{role_name} Accounts"):
                for account in accounts:
                    st.markdown(f"""
                    <div class="demo-account">
                        <strong>Email:</strong> {account['email']}<br>
                        <strong>Password:</strong> {account['password']}<br>
                        <strong>Name:</strong> {account['name']}
                    </div>
                    """, unsafe_allow_html=True)

def show_application_form(app_type):
    st.markdown('<div class="sub-header">📝 Application Form</div>', unsafe_allow_html=True)
    
    with st.form("application_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
            
        with col2:
            if app_type == "👥 Apply for Guest Account":
                address = st.text_area("Home Address")
                id_type = st.selectbox("ID Type", ["Passport", "Driver's License", "National ID"])
                id_number = st.text_input("ID Number")
            else:
                company = st.text_input("Company Name" if app_type == "🤝 Apply as Vendor" else "Current Position")
                experience = st.text_area("Relevant Experience")
                documents = st.file_uploader("Upload Resume/Certificates", type=['pdf', 'docx'], 
                                           accept_multiple_files=True)
        
        additional_info = st.text_area("Additional Information / Cover Letter")
        
        submitted = st.form_submit_button("📤 Submit Application")
        if submitted:
            application = {
                "type": app_type,
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Pending"
            }
            
            if app_type == "👥 Apply for Guest Account":
                application.update({
                    "address": address,
                    "id_type": id_type,
                    "id_number": id_number
                })
                st.session_state.guest_applications.append(application)
                add_notification(f"New guest application from {full_name}", "info")
            elif app_type == "💼 Apply for Job Position":
                application.update({
                    "position": company,
                    "experience": experience,
                    "documents": len(documents) if documents else 0
                })
                st.session_state.staff_applications.append(application)
                add_notification(f"New job application from {full_name}", "info")
            else:  # Vendor application
                application.update({
                    "company": company,
                    "experience": experience,
                    "documents": len(documents) if documents else 0
                })
                st.session_state.vendor_applications.append(application)
                add_notification(f"New vendor application from {company}", "info")
            
            st.success("Application submitted successfully! We will contact you soon.")

def show_main_application():
    # Notification badge in sidebar
    unread_count = len([n for n in st.session_state.notifications if not n['read']])
    if unread_count > 0:
        notification_badge = f'<span class="notification-badge">{unread_count}</span>'
    else:
        notification_badge = ''
    
    notification_text = f"🔔 Notifications {notification_badge}"
    
    st.sidebar.markdown(f"""
    <div class="sidebar-header">
        <h3>👋 {st.session_state.current_user['name']}</h3>
        <p><strong>Role:</strong> {st.session_state.current_role}</p>
        <p>{notification_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show notifications
    if unread_count > 0:
        with st.sidebar.expander("📋 Recent Notifications", expanded=False):
            for notification in st.session_state.notifications[-5:][::-1]:
                read_status = "✅ " if notification['read'] else "🔔 "
                st.write(f"{read_status}{notification['message']}")
                st.caption(notification['timestamp'])
                
            if st.button("Mark All as Read"):
                for notification in st.session_state.notifications:
                    notification['read'] = True
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
    elif st.session_state.current_role == "Executive Chef":
        show_chef_portal()
    elif st.session_state.current_role == "Event Coordinator":
        show_event_portal()
    
    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.current_role = None
        st.rerun()

# Guest Portal Functions
def show_guest_portal():
    st.markdown('<div class="main-header">👤 Guest Portal - Grand Stay Hotel</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Book Room", "📋 My Bookings", "🛎️ Service Requests", "⭐ Leave Review", 
        "🍽️ Catering", "🎉 Event Services", "📞 Other Services"
    ])
    
    with tab1:
        show_booking_flow()
    with tab2:
        show_guest_bookings()
    with tab3:
        show_service_requests()
    with tab4:
        show_review_system()
    with tab5:
        show_catering_services()
    with tab6:
        show_event_services()
    with tab7:
        show_other_services()

def show_booking_flow():
    st.markdown('<div class="sub-header">📅 Room Booking (4-Step Process)</div>', unsafe_allow_html=True)
    
    # Step 1: Room Selection
    st.markdown("#### Step 1: Select Room Type & Dates")
    col1, col2 = st.columns(2)
    
    with col1:
        room_type = st.selectbox("Room Type", ["Single", "Double", "Suite", "Deluxe"])
        check_in = st.date_input("Check-in Date", datetime.now())
        num_guests = st.number_input("Number of Guests", min_value=1, max_value=4, value=2)
    
    with col2:
        duration_type = st.selectbox("Booking Type", ["Hourly", "Daily", "Weekly", "Monthly"])
        check_out = st.date_input("Check-out Date", datetime.now() + timedelta(days=1))
        meal_package = st.selectbox("Meal Package", ["None", "Breakfast Only", "Half Board", "Full Board"])
    
    # Step 2: Additional Services
    st.markdown("#### Step 2: Additional Services")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        airport_pickup = st.checkbox("Airport Pickup ($50)")
        spa_access = st.checkbox("Spa Access ($75)")
    
    with col2:
        gym_access = st.checkbox("Gym Access (Complimentary)")
        guided_tours = st.checkbox("Guided City Tour ($100)")
    
    with col3:
        special_requests = st.text_area("Special Requests")
    
    # Step 3: Price Calculation
    st.markdown("#### Step 3: Price Summary")
    room_prices = {"Single": 150, "Double": 200, "Suite": 350, "Deluxe": 500}
    base_price = room_prices[room_type]
    
    # Calculate duration
    nights = (check_out - check_in).days
    if nights == 0:
        nights = 1
    
    total_price = base_price * nights
    
    # Add service costs
    if airport_pickup:
        total_price += 50
    if spa_access:
        total_price += 75
    if guided_tours:
        total_price += 100
    
    # Display price breakdown
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card">
            <h4>Price Breakdown</h4>
            <p>Room ({room_type}): ${base_price}/night × {nights} nights = ${base_price * nights}</p>
            <p>Additional Services: ${total_price - (base_price * nights)}</p>
            <hr>
            <h4>Total: ${total_price}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Step 4: Payment
    st.markdown("#### Step 4: Payment & Confirmation")
    if st.button("💳 Proceed to Payment", use_container_width=True):
        with st.spinner("Processing payment..."):
            time.sleep(2)
            
            # Create booking record
            booking_id = f"BK{len(st.session_state.bookings) + 1:03d}"
            new_booking = {
                "id": booking_id,
                "guest": st.session_state.current_user['name'],
                "room_type": room_type,
                "check_in": check_in.strftime("%Y-%m-%d"),
                "check_out": check_out.strftime("%Y-%m-%d"),
                "status": "Confirmed",
                "amount": f"${total_price}",
                "special_requests": special_requests,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.bookings.append(new_booking)
            
            add_notification(f"New booking #{booking_id} from {st.session_state.current_user['name']}", "booking")
            st.success("🎉 Booking confirmed! Provisional invoice generated. Please complete payment within 15 minutes.")

def show_guest_bookings():
    st.markdown('<div class="sub-header">📋 My Current Bookings</div>', unsafe_allow_html=True)
    
    # Filter bookings for current guest
    guest_bookings = [b for b in st.session_state.bookings if b["guest"] == st.session_state.current_user['name']]
    
    if not guest_bookings:
        st.info("You have no current bookings.")
        return
    
    for booking in guest_bookings:
        status_color = "success-card" if booking["status"] == "Confirmed" else "warning-card"
        st.markdown(f"""
        <div class="card {status_color}">
            <h4>Booking #{booking['id']} - {booking['room_type']}</h4>
            <p><strong>Dates:</strong> {booking['check_in']} to {booking['check_out']}</p>
            <p><strong>Status:</strong> {booking['status']} | <strong>Amount:</strong> {booking['amount']}</p>
            {f"<p><strong>Special Requests:</strong> {booking['special_requests']}</p>" if booking.get('special_requests') else ""}
        </div>
        """, unsafe_allow_html=True)

def show_service_requests():
    st.markdown('<div class="sub-header">🛎️ In-Stay Service Requests</div>', unsafe_allow_html=True)
    
    service_type = st.selectbox("Service Type", 
                               ["Housekeeping", "Room Service", "Maintenance", "Concierge", "Transportation"])
    
    col1, col2 = st.columns(2)
    with col1:
        urgency = st.select_slider("Urgency Level", ["Low", "Medium", "High", "Critical"])
        room_number = st.text_input("Your Room Number")
    
    with col2:
        preferred_time = st.time_input("Preferred Service Time", datetime.now().time())
        contact_method = st.selectbox("Contact Method", ["Phone", "Room Visit", "No Contact"])
    
    service_details = st.text_area("Service Details Description")
    
    if st.button("📨 Submit Service Request", use_container_width=True):
        # Create service request
        request_id = f"SR{len(st.session_state.service_requests) + 1:03d}"
        new_request = {
            "id": request_id,
            "guest": st.session_state.current_user['name'],
            "room": room_number,
            "type": service_type,
            "urgency": urgency,
            "details": service_details,
            "status": "Pending",
            "time": datetime.now().strftime("%I:%M %p")
        }
        st.session_state.service_requests.append(new_request)
        add_notification(f"New {service_type} request from Room {room_number}", "service")
        st.success("Service request submitted! Our staff will attend to it shortly.")

def show_review_system():
    st.markdown('<div class="sub-header">⭐ Share Your Experience</div>', unsafe_allow_html=True)
    
    # Show only if user has bookings
    guest_bookings = [b for b in st.session_state.bookings if b["guest"] == st.session_state.current_user['name']]
    
    if not guest_bookings:
        st.info("You need to have a booking to leave a review.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        stay_date = st.date_input("Date of Stay", datetime.now() - timedelta(days=7))
        room_number = st.text_input("Room Number (Optional)")
        
        st.markdown("#### Rate Your Experience")
        overall_rating = st.slider("Overall Rating", 1, 5, 5)
        cleanliness = st.slider("Cleanliness", 1, 5, 5)
        service = st.slider("Service Quality", 1, 5, 5)
        comfort = st.slider("Room Comfort", 1, 5, 5)
        value = st.slider("Value for Money", 1, 5, 5)
    
    with col2:
        st.markdown("#### Current Ratings")
        avg_rating = (overall_rating + cleanliness + service + comfort + value) / 5
        st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
        
        # Display rating breakdown
        ratings_data = {
            'Category': ['Overall', 'Cleanliness', 'Service', 'Comfort', 'Value'],
            'Rating': [overall_rating, cleanliness, service, comfort, value]
        }
        fig = px.bar(ratings_data, x='Rating', y='Category', orientation='h')
        st.plotly_chart(fig, use_container_width=True)
    
    review_text = st.text_area("Detailed Review Comments")
    
    if st.button("📤 Submit Review", use_container_width=True):
        review = {
            "guest": st.session_state.current_user['name'],
            "ratings": {
                "overall": overall_rating,
                "cleanliness": cleanliness,
                "service": service,
                "comfort": comfort,
                "value": value
            },
            "comments": review_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.reviews.append(review)
        add_notification(f"New review from {st.session_state.current_user['name']}", "review")
        st.success("Thank you for your valuable feedback!")

def show_catering_services():
    st.markdown('<div class="sub-header">🍽️ Catering Services</div>', unsafe_allow_html=True)
    
    st.info("Order premium catering services for your stay")
    
    col1, col2 = st.columns(2)
    
    with col1:
        service_type = st.selectbox("Catering Type", 
                                  ["In-Room Dining", "Private Chef", "Special Diet", "Group Catering"])
        delivery_time = st.time_input("Preferred Delivery Time")
        num_people = st.number_input("Number of People", min_value=1, max_value=50, value=2)
    
    with col2:
        cuisine_type = st.selectbox("Cuisine Preference", 
                                  ["International", "Asian", "European", "Local", "Vegetarian"])
        special_requirements = st.text_area("Dietary Requirements")
    
    menu_selection = st.multiselect("Menu Selection", 
                                   ["Breakfast Set", "Lunch Special", "Dinner Course", "Dessert Platter"])
    
    if st.button("🍽️ Order Catering", use_container_width=True):
        st.success("Catering order placed! Our executive chef will contact you soon.")

def show_event_services():
    st.markdown('<div class="sub-header">🎉 Event Services</div>', unsafe_allow_html=True)
    
    st.info("Plan your perfect event with our professional event coordination services")
    
    col1, col2 = st.columns(2)
    
    with col1:
        event_type = st.selectbox("Event Type", 
                                ["Business Meeting", "Wedding", "Birthday Party", "Conference", "Private Dinner"])
        event_date = st.date_input("Event Date")
        num_guests = st.number_input("Expected Guests", min_value=1, max_value=500, value=50)
    
    with col2:
        venue_preference = st.selectbox("Venue Preference", 
                                      ["Ballroom", "Garden", "Conference Room", "Private Suite"])
        budget_range = st.selectbox("Budget Range", 
                                  ["$500-$1000", "$1000-$2500", "$2500-$5000", "$5000+"])
    
    additional_services = st.multiselect("Additional Services", 
                                       ["Photography", "Music", "Decoration", "Catering", "Transportation"])
    
    if st.button("🎉 Plan Event", use_container_width=True):
        st.success("Event planning request submitted! Our event coordinator will contact you soon.")

def show_other_services():
    st.markdown('<div class="sub-header">📞 Other Services</div>', unsafe_allow_html=True)
    
    st.info("Explore additional services available during your stay")
    
    services = [
        {"name": "Spa & Wellness", "description": "Relaxing spa treatments and wellness services", "price": "From $75"},
        {"name": "Business Center", "description": "Fully equipped business facilities", "price": "Complimentary"},
        {"name": "Car Rental", "description": "Luxury car rental services", "price": "From $80/day"},
        {"name": "Tour Guide", "description": "Professional local tour guides", "price": "From $50/hour"},
        {"name": "Laundry Service", "description": "Premium laundry and dry cleaning", "price": "From $15"},
        {"name": "Airport Transfer", "description": "Luxury airport transportation", "price": "From $60"}
    ]
    
    cols = st.columns(2)
    for idx, service in enumerate(services):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="card">
                <h4>{service['name']}</h4>
                <p>{service['description']}</p>
                <p><strong>Price:</strong> {service['price']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    if st.button("📞 Inquire About Services", use_container_width=True):
        st.success("Service inquiry submitted! Our concierge will contact you soon.")

# Front Desk Portal Functions
def show_front_desk_portal():
    st.markdown('<div class="main-header">🏢 Front Desk Operations Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🛏️ Room Management", "👥 Check-In/Out", "📋 Request Queue"])
    
    with tab1:
        show_front_desk_dashboard()
    with tab2:
        show_room_management()
    with tab3:
        show_checkin_checkout()
    with tab4:
        show_request_queue()

def show_front_desk_dashboard():
    st.markdown('<div class="sub-header">📊 Today\'s Operations Overview</div>', unsafe_allow_html=True)
    
    # Calculate real-time metrics
    total_rooms = len(st.session_state.rooms)
    occupied_rooms = len([r for r in st.session_state.rooms if r["status"] == "occupied"])
    occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0
    pending_requests = len([r for r in st.session_state.service_requests if r["status"] == "Pending"])
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Expected Arrivals", "15", "2 from yesterday")
    with col2:
        st.metric("Scheduled Departures", "12", "-1 from yesterday")
    with col3:
        st.metric("Current Occupancy", f"{occupancy_rate:.1f}%", "5%")
    with col4:
        st.metric("Pending Requests", str(pending_requests), "3 new")
    
    # Recent bookings
    st.markdown("#### Recent Bookings")
    if st.session_state.bookings:
        recent_bookings = st.session_state.bookings[-5:][::-1]
        for booking in recent_bookings:
            st.markdown(f"""
            <div class="card">
                <p><strong>#{booking['id']}</strong> - {booking['guest']} - {booking['room_type']} - {booking['status']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent bookings")

# Housekeeping Portal
def show_housekeeping_portal():
    st.markdown('<div class="main-header">🧹 Housekeeping Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Cleaning Schedule", "✅ Task Completion", "📊 Performance"])
    
    with tab1:
        st.markdown('<div class="sub-header">🛏️ Room Cleaning Schedule</div>', unsafe_allow_html=True)
        
        # Show rooms needing cleaning
        cleaning_rooms = [r for r in st.session_state.rooms if r["status"] == "cleaning"]
        for room in cleaning_rooms:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="card warning-card">
                    <h4>Room {room['number']} - {room['type']}</h4>
                    <p>Status: Ready for Cleaning</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button(f"Start Cleaning", key=f"start_{room['number']}"):
                    room["status"] = "cleaning_in_progress"
                    st.rerun()
            with col3:
                if st.button(f"Complete", key=f"complete_{room['number']}"):
                    room["status"] = "vacant"
                    add_notification(f"Room {room['number']} cleaned and ready", "cleaning")
                    st.rerun()

# Maintenance Portal
def show_maintenance_portal():
    st.markdown('<div class="main-header">🔧 Maintenance Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🛠️ Maintenance Tasks", "📋 Equipment Log"])
    
    with tab1:
        st.markdown('<div class="sub-header">🔧 Maintenance Requests</div>', unsafe_allow_html=True)
        
        maintenance_requests = [r for r in st.session_state.service_requests if r["type"] == "Maintenance"]
        for request in maintenance_requests:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                urgency_color = {"High": "critical-card", "Medium": "warning-card", "Low": "card"}[request["urgency"]]
                st.markdown(f"""
                <div class="card {urgency_color}">
                    <h4>Room {request['room']} - {request['type']}</h4>
                    <p>Issue: {request['details']}</p>
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

# Catering Portal
def show_catering_portal():
    st.markdown('<div class="main-header">🍽️ Catering Services Portal</div>', unsafe_allow_html=True)
    
    st.info("Manage catering orders and kitchen operations")
    
    # Sample catering orders
    catering_orders = [
        {"id": "CT001", "room": "301", "type": "In-Room Dining", "time": "19:00", "status": "Pending"},
        {"id": "CT002", "room": "201", "type": "Special Diet", "time": "08:30", "status": "Preparing"},
    ]
    
    for order in catering_orders:
        st.markdown(f"""
        <div class="card">
            <h4>Order #{order['id']} - Room {order['room']}</h4>
            <p>Type: {order['type']} | Time: {order['time']} | Status: {order['status']}</p>
        </div>
        """, unsafe_allow_html=True)

# Chef Portal
def show_chef_portal():
    st.markdown('<div class="main-header">👨‍🍳 Executive Chef Portal</div>', unsafe_allow_html=True)
    
    st.info("Manage kitchen operations and menu planning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🍳 Today's Special Orders")
        # Show special orders
        st.markdown("""
        <div class="card">
            <h4>VIP Suite 301</h4>
            <p>Vegetarian 7-course meal</p>
            <p>Time: 19:30 | Status: Preparing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📊 Kitchen Performance")
        st.metric("Orders Today", "24")
        st.metric("Preparation Time", "18 min")
        st.metric("Guest Satisfaction", "4.8/5")

# Event Coordinator Portal
def show_event_portal():
    st.markdown('<div class="main-header">🎉 Event Coordination Portal</div>', unsafe_allow_html=True)
    
    st.info("Manage events and function bookings")
    
    # Sample events
    events = [
        {"id": "EV001", "type": "Wedding", "date": "2024-02-14", "guests": "120", "status": "Confirmed"},
        {"id": "EV002", "type": "Business Conference", "date": "2024-02-20", "guests": "80", "status": "Planning"},
    ]
    
    for event in events:
        st.markdown(f"""
        <div class="card">
            <h4>Event #{event['id']} - {event['type']}</h4>
            <p>Date: {event['date']} | Guests: {event['guests']} | Status: {event['status']}</p>
        </div>
        """, unsafe_allow_html=True)

# Manager Portal with enhanced functionality
def show_manager_portal():
    st.markdown('<div class="main-header">👨‍💼 Hotel Manager Dashboard</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Analytics", "👥 Staff Management", "🤝 Vendor Management", "📊 Reports", "📋 Approvals"
    ])
    
    with tab1:
        show_manager_analytics()
    with tab2:
        show_staff_management()
    with tab3:
        show_vendor_management()
    with tab4:
        show_manager_reports()
    with tab5:
        show_approval_system()

def show_approval_system():
    st.markdown('<div class="sub-header">📋 Approval Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Staff Applications", len(st.session_state.staff_applications))
    with col2:
        st.metric("Vendor Applications", len(st.session_state.vendor_applications))
    with col3:
        st.metric("Guest Applications", len(st.session_state.guest_applications))
    
    # Staff Applications
    st.markdown("#### 👥 Staff Applications")
    for app in st.session_state.staff_applications:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"""
            <div class="card">
                <h4>{app['full_name']}</h4>
                <p>Position: {app['position']} | Email: {app['email']}</p>
                <p>Experience: {app['experience'][:100]}...</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("✅ Approve", key=f"staff_approve_{app['email']}"):
                app['status'] = 'Approved'
                add_notification(f"Staff application approved: {app['full_name']}", "success")
                st.rerun()
        with col3:
            if st.button("❌ Reject", key=f"staff_reject_{app['email']}"):
                app['status'] = 'Rejected'
                st.rerun()
    
    # Vendor Applications
    st.markdown("#### 🤝 Vendor Applications")
    for app in st.session_state.vendor_applications:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"""
            <div class="card">
                <h4>{app['company']}</h4>
                <p>Contact: {app['full_name']} | Email: {app['email']}</p>
                <p>Experience: {app['experience'][:100]}...</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("✅ Approve", key=f"vendor_approve_{app['email']}"):
                app['status'] = 'Approved'
                add_notification(f"Vendor application approved: {app['company']}", "success")
                st.rerun()
        with col3:
            if st.button("❌ Reject", key=f"vendor_reject_{app['email']}"):
                app['status'] = 'Rejected'
                st.rerun()

def show_manager_analytics():
    st.markdown('<div class="sub-header">📈 Real-time Hotel Performance</div>', unsafe_allow_html=True)
    
    # Calculate metrics
    total_rooms = len(st.session_state.rooms)
    occupied = len([r for r in st.session_state.rooms if r["status"] == "occupied"])
    vacant = len([r for r in st.session_state.rooms if r["status"] == "vacant"])
    cleaning = len([r for r in st.session_state.rooms if r["status"] == "cleaning"])
    maintenance = len([r for r in st.session_state.rooms if r["status"] == "maintenance"])
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Occupancy Rate", f"{(occupied/total_rooms)*100:.1f}%", "5.2%")
    with col2:
        st.metric("Revenue (Today)", "$8,450", "12%")
    with col3:
        st.metric("ADR", "$245", "$15")
    with col4:
        st.metric("RevPAR", "$189", "$22")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Room status pie chart
        status_data = {
            'Status': ['Occupied', 'Vacant', 'Cleaning', 'Maintenance'],
            'Count': [occupied, vacant, cleaning, maintenance]
        }
        fig = px.pie(status_data, values='Count', names='Status', title='Room Status Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue trend
        revenue_data = {
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Revenue': [7200, 6800, 7100, 7500, 8200, 9500, 8800]
        }
        fig = px.line(revenue_data, x='Day', y='Revenue', title='Weekly Revenue Trend')
        st.plotly_chart(fig, use_container_width=True)

def show_staff_management():
    st.markdown('<div class="sub-header">👥 Staff Management</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Add New Staff")
        with st.form("new_staff_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            role = st.selectbox("Role", list(DEMO_ACCOUNTS.keys()))
            department = st.selectbox("Department", ["Front Desk", "Housekeeping", "Maintenance", "Catering", "Management"])
            
            if st.form_submit_button("➕ Add Staff"):
                add_notification(f"New staff added: {name} as {role}", "staff")
                st.success(f"Staff {name} added successfully!")
    
    with col2:
        st.markdown("#### Current Staff")
        staff_list = [
            {"name": "Emily Frontdesk", "role": "Front Desk", "status": "Active"},
            {"name": "Maria Cleaner", "role": "Housekeeping", "status": "Active"},
            {"name": "Mike Technician", "role": "Maintenance", "status": "Active"},
        ]
        
        for staff in staff_list:
            st.markdown(f"""
            <div class="card">
                <p><strong>{staff['name']}</strong> - {staff['role']} - {staff['status']}</p>
            </div>
            """, unsafe_allow_html=True)

def show_vendor_management():
    st.markdown('<div class="sub-header">🤝 Vendor Management</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Approve New Vendors")
        # Show pending vendor applications
        pending_vendors = [v for v in st.session_state.vendor_applications if v['status'] == 'Pending']
        for vendor in pending_vendors:
            st.markdown(f"""
            <div class="card warning-card">
                <h4>{vendor['company']}</h4>
                <p>Contact: {vendor['full_name']}</p>
                <p>Status: {vendor['status']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Current Vendors")
        vendors = [
            {"name": "ABC Supplies", "service": "Linens", "status": "Active"},
            {"name": "XYZ Foods", "service": "Catering", "status": "Active"},
        ]
        
        for vendor in vendors:
            st.markdown(f"""
            <div class="card success-card">
                <p><strong>{vendor['name']}</strong> - {vendor['service']}</p>
            </div>
            """, unsafe_allow_html=True)

def show_manager_reports():
    st.markdown('<div class="sub-header">📊 Management Reports</div>', unsafe_allow_html=True)
    
    report_type = st.selectbox("Select Report Type", 
                              ["Daily Occupancy Report", "Revenue Analysis", "Guest Satisfaction", "Staff Performance"])
    
    if st.button("📥 Download Report", use_container_width=True):
        # Generate sample report data
        report_data = pd.DataFrame({
            'Metric': ['Total Revenue', 'Average Occupancy', 'RevPAR', 'ADR', 'Guest Satisfaction'],
            'Value': ['$850,000', '78%', '$156', '$200', '4.2/5'],
            'Change': ['+15%', '+5%', '+8%', '+7%', '+0.3']
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

# Billing Portal Functions
def show_billing_portal():
    st.markdown('<div class="main-header">💰 Billing & Finance Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🧾 Invoice Management", "💳 Payment Processing", "📈 Financial Reports"])
    
    with tab1:
        show_invoice_management()
    with tab2:
        show_payment_processing()
    with tab3:
        show_financial_reports()

def show_invoice_management():
    st.markdown('<div class="sub-header">🧾 Invoice Management</div>', unsafe_allow_html=True)
    
    # Sample invoices
    sample_invoices = [
        {"id": "INV001", "guest": "John Smith", "amount": "$450", "status": "Paid", "due_date": "2024-01-15"},
        {"id": "INV002", "guest": "Sarah Johnson", "amount": "$320", "status": "Pending", "due_date": "2024-01-16"},
    ]
    
    for invoice in sample_invoices:
        status_color = "success-card" if invoice["status"] == "Paid" else "warning-card"
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class="card {status_color}">
                <h4>Invoice {invoice['id']}</h4>
                <p>Guest: {invoice['guest']} | Amount: {invoice['amount']}</p>
                <p>Status: <strong>{invoice['status']}</strong> | Due: {invoice['due_date']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("📧 Send", key=f"email_{invoice['id']}"):
                st.success(f"Invoice {invoice['id']} sent to guest!")

def show_payment_processing():
    st.markdown('<div class="sub-header">💳 Payment Processing</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Process Payment")
        invoice_id = st.text_input("Invoice ID")
        payment_amount = st.number_input("Payment Amount ($)", min_value=1.0, step=10.0)
        
        if st.button("✅ Record Payment", use_container_width=True):
            st.success(f"Payment of ${payment_amount} recorded for invoice {invoice_id}")
    
    with col2:
        st.markdown("#### Payment Summary")
        st.metric("Today's Payments", "$2,450")
        st.metric("Pending Payments", "$1,280")

def show_financial_reports():
    st.markdown('<div class="sub-header">📈 Financial Analytics</div>', unsafe_allow_html=True)
    
    # Sample financial data
    revenue_data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [125000, 118000, 132000, 145000, 158000, 167000],
    }
    
    fig = px.line(revenue_data, x='Month', y='Revenue', title='Monthly Revenue Trend')
    st.plotly_chart(fig, use_container_width=True)
    
    if st.button("📥 Download Financial Report", use_container_width=True):
        csv = pd.DataFrame(revenue_data).to_csv(index=False)
        st.download_button(
            label="⬇️ Download Report",
            data=csv,
            file_name="financial_report.csv",
            mime="text/csv",
        )

# Vendor Portal Functions
def show_vendor_portal():
    st.markdown('<div class="main-header">🚚 Vendor Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📦 Orders", "💰 Statements"])
    
    with tab1:
        show_vendor_orders()
    with tab2:
        show_vendor_statements()

def show_vendor_orders():
    st.markdown('<div class="sub-header">📦 Current Orders</div>', unsafe_allow_html=True)
    
    orders = [
        {"id": "VO001", "item": "Linens", "quantity": "50 sets", "status": "Delivered"},
        {"id": "VO002", "item": "Toiletries", "quantity": "200 units", "status": "In Transit"},
    ]
    
    for order in orders:
        st.markdown(f"""
        <div class="card">
            <h4>Order {order['id']}</h4>
            <p>Item: {order['item']} | Quantity: {order['quantity']}</p>
            <p>Status: {order['status']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_vendor_statements():
    st.markdown('<div class="sub-header">💰 Payment Statements</div>', unsafe_allow_html=True)
    
    statements = [
        {"period": "January 2024", "amount": "$2,450", "status": "Paid"},
        {"period": "February 2024", "amount": "$3,120", "status": "Pending"},
    ]
    
    for stmt in statements:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class="card">
                <h4>{stmt['period']}</h4>
                <p>Amount: {stmt['amount']} | Status: {stmt['status']}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("📥 Download", key=f"dl_{stmt['period']}"):
                # Generate simple statement data
                statement_data = f"Period: {stmt['period']}\nAmount: {stmt['amount']}\nStatus: {stmt['status']}"
                st.download_button(
                    label="⬇️ Download",
                    data=statement_data,
                    file_name=f"statement_{stmt['period'].replace(' ', '_')}.txt",
                    mime="text/plain",
                    key=f"download_{stmt['period']}"
                )

# Room management and other existing functions remain similar but with new color scheme
def show_room_management():
    st.markdown('<div class="sub-header">🛏️ Room Rack Management</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Room Status")
        cols = st.columns(4)
        for idx, room in enumerate(st.session_state.rooms):
            with cols[idx % 4]:
                status_colors = {
                    "occupied": "#E74C3C",
                    "vacant": "#27AE60", 
                    "cleaning": "#F39C12",
                    "maintenance": "#95A5A6"
                }
                st.markdown(f"""
                <div style="background-color: {status_colors[room['status']]}; 
                            color: white; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 0.5rem;">
                    <h4>Room {room['number']}</h4>
                    <p>{room['type']}</p>
                    <p><strong>{room['status'].title()}</strong></p>
                </div>
                """, unsafe_allow_html=True)

def show_checkin_checkout():
    st.markdown('<div class="sub-header">👥 Check-In / Check-Out</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["✅ Check-In", "🚪 Check-Out"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            guest_name = st.text_input("Guest Name")
        with col2:
            room = st.selectbox("Assign Room", ["101", "102", "103"])
        
        if st.button("✅ Check-In", use_container_width=True):
            st.success(f"Guest checked into Room {room}")

def show_request_queue():
    st.markdown('<div class="sub-header">📋 Service Requests</div>', unsafe_allow_html=True)
    
    pending_requests = [r for r in st.session_state.service_requests if r["status"] == "Pending"]
    for req in pending_requests:
        st.markdown(f"""
        <div class="card">
            <h4>{req['type']} - Room {req['room']}</h4>
            <p>Guest: {req['guest']} | Urgency: {req['urgency']}</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()