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

# Demo accounts data
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
        'reviews': [],
        'tasks': [],
        'vendors': [
            {"name": "ABC Laundry", "service": "Linens", "status": "Approved", "contact": "contact@abclaundry.com"},
            {"name": "XYZ Catering", "service": "Food Service", "status": "Approved", "contact": "info@xyzcatering.com"}
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
                st.error("Invalid credentials. Please use demo accounts below.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Demo accounts below login box
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

# ==================== GUEST PORTAL ====================
def show_guest_portal():
    st.markdown('<div class="main-header">👤 Guest Portal - Grand Stay Hotel</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Book Room", "📋 My Bookings", "🛎️ Service Requests", "⭐ Leave Review"])
    
    with tab1:
        show_guest_booking()
    with tab2:
        show_guest_bookings()
    with tab3:
        show_guest_service_requests()
    with tab4:
        show_guest_reviews()

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
            "amount": total_price,
            "special_requests": special_requests,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            "due_date": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.invoices.append(new_invoice)
        
        # Send notifications
        add_notification(f"New booking #{booking_id} from {st.session_state.current_user['name']}", "booking", ["Front Desk Officer", "Hotel Manager"])
        add_notification(f"Payment required for booking #{booking_id} - ${total_price}", "payment", ["Billing Officer"])
        
        st.success(f"🎉 Booking confirmed! Your booking ID is {booking_id}. Please complete payment within 2 hours.")
        
        # Show provisional invoice
        st.markdown(f"""
        <div class="card success-card">
            <h4>📄 Provisional Invoice #{invoice_id}</h4>
            <p><strong>Booking ID:</strong> {booking_id}</p>
            <p><strong>Guest:</strong> {st.session_state.current_user['name']}</p>
            <p><strong>Amount Due:</strong> ${total_price}</p>
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
        status_color = "success-card" if booking["status"] == "Confirmed" else "warning-card"
        st.markdown(f"""
        <div class="card {status_color}">
            <h4>Booking #{booking['id']} - {booking['room_type']}</h4>
            <p><strong>Dates:</strong> {booking['check_in']} to {booking['check_out']}</p>
            <p><strong>Status:</strong> {booking['status']} | <strong>Amount:</strong> ${booking['amount']}</p>
            <p><strong>Special Requests:</strong> {booking.get('special_requests', 'None')}</p>
        </div>
        """, unsafe_allow_html=True)

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
        else:
            add_notification(f"New {service_type} request from Room {room_number}", "service", ["Front Desk Officer"])
        
        st.success("Service request submitted! Our staff will attend to it shortly.")

def show_guest_reviews():
    st.markdown('<div class="sub-header">⭐ Share Your Experience</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        stay_date = st.date_input("Date of Stay", datetime.now() - timedelta(days=7))
        room_number = st.text_input("Room Number")
        
        st.markdown("#### Rate Your Experience")
        overall_rating = st.slider("Overall Rating", 1, 5, 5)
        cleanliness = st.slider("Cleanliness", 1, 5, 5)
        service = st.slider("Service Quality", 1, 5, 5)
        comfort = st.slider("Room Comfort", 1, 5, 5)
    
    with col2:
        avg_rating = (overall_rating + cleanliness + service + comfort) / 4
        st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
    
    review_text = st.text_area("Detailed Review Comments")
    
    if st.button("📤 Submit Review", use_container_width=True):
        review = {
            "guest": st.session_state.current_user['name'],
            "room": room_number,
            "ratings": {
                "overall": overall_rating,
                "cleanliness": cleanliness,
                "service": service,
                "comfort": comfort
            },
            "comments": review_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.reviews.append(review)
        add_notification(f"New review submitted by {st.session_state.current_user['name']}", "review", ["Hotel Manager"])
        st.success("Thank you for your valuable feedback!")

# ==================== FRONT DESK PORTAL ====================
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
            payment_method = st.selectbox("Payment Method", ["Credit Card", "Cash", "Corporate Account"])
        
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
        urgency_color = {"High": "critical-card", "Medium": "warning-card", "Low": "card"}[request["urgency"]]
        
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
            assign_to = st.selectbox(f"Assign to", ["Housekeeping", "Maintenance", "Catering"], key=f"assign_{request['id']}")
        
        with col3:
            if st.button("✅ Complete", key=f"complete_{request['id']}"):
                request["status"] = "Completed"
                add_notification(f"Service request {request['id']} completed", "service")
                st.success(f"Request {request['id']} marked as completed!")

# ==================== STAFF PORTALS ====================
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

def show_maintenance_portal():
    st.markdown('<div class="main-header">🔧 Maintenance Portal</div>', unsafe_allow_html=True)
    
    maintenance_requests = [r for r in st.session_state.service_requests if r["type"] == "Maintenance" and r["status"] == "Pending"]
    
    if not maintenance_requests:
        st.info("No maintenance requests.")
        return
    
    for request in maintenance_requests:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            urgency_color = {"High": "critical-card", "Medium": "warning-card", "Low": "card"}[request["urgency"]]
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

# ==================== MANAGER PORTAL ====================
def show_manager_portal():
    st.markdown('<div class="main-header">👨‍💼 Hotel Manager Dashboard</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Analytics", "👥 Staff Management", "🤝 Vendor Management", "📊 Reports", "⚙️ Configuration"])
    
    with tab1:
        show_manager_analytics()
    with tab2:
        show_staff_management()
    with tab3:
        show_vendor_management()
    with tab4:
        show_manager_reports()
    with tab5:
        show_system_config()

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

def show_staff_management():
    st.markdown('<div class="sub-header">👥 Staff Management</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Staff Performance")
        staff_data = [
            {"name": "Emily Frontdesk", "role": "Front Desk", "tasks_completed": 45, "rating": 4.8},
            {"name": "Maria Cleaner", "role": "Housekeeping", "tasks_completed": 38, "rating": 4.6},
            {"name": "Mike Technician", "role": "Maintenance", "tasks_completed": 25, "rating": 4.7},
        ]
        
        for staff in staff_data:
            st.markdown(f"""
            <div class="card">
                <h4>{staff['name']}</h4>
                <p>Role: {staff['role']}</p>
                <p>Tasks Completed: {staff['tasks_completed']} | Rating: {staff['rating']}/5</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Staff Scheduling")
        with st.form("schedule_form"):
            staff_member = st.selectbox("Staff Member", ["Emily Frontdesk", "Maria Cleaner", "Mike Technician"])
            shift_date = st.date_input("Shift Date")
            shift_type = st.selectbox("Shift Type", ["Morning (7AM-3PM)", "Evening (3PM-11PM)", "Night (11PM-7AM)"])
            
            if st.form_submit_button("📅 Assign Shift"):
                st.success(f"Shift assigned to {staff_member}")

def show_vendor_management():
    st.markdown('<div class="sub-header">🤝 Vendor Management</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Vendor Approval", "Current Vendors"])
    
    with tab1:
        st.markdown("#### Vendor Applications")
        for application in st.session_state.vendor_applications:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="card">
                    <h4>{application['company']}</h4>
                    <p>Service: {application['service']}</p>
                    <p>Contact: {application['contact']}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✅ Approve", key=f"approve_{application['company']}"):
                    application['status'] = 'Approved'
                    st.session_state.vendors.append(application)
                    st.rerun()
            with col3:
                if st.button("❌ Reject", key=f"reject_{application['company']}"):
                    application['status'] = 'Rejected'
                    st.rerun()
    
    with tab2:
        st.markdown("#### Approved Vendors")
        for vendor in st.session_state.vendors:
            st.markdown(f"""
            <div class="card success-card">
                <h4>{vendor['name']}</h4>
                <p>Service: {vendor['service']}</p>
                <p>Contact: {vendor['contact']}</p>
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
        for room_type in room_types:
            new_rate = st.number_input(f"{room_type} Rate ($)", min_value=50, max_value=1000, value=150, key=f"rate_{room_type}")
        
        st.markdown("#### System Settings")
        auto_cancel = st.number_input("Auto-cancel Time (hours)", min_value=1, value=2)
        max_guests = st.number_input("Max Guests per Room", min_value=1, value=4)
    
    with col2:
        st.markdown("#### Notification Settings")
        email_alerts = st.checkbox("Email Alerts for High Priority")
        sms_alerts = st.checkbox("SMS Alerts for Critical Issues")
        
        if st.button("💾 Save Configuration", use_container_width=True):
            st.success("System configuration updated successfully!")

# ==================== BILLING PORTAL ====================
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
    st.markdown('<div class="sub-header">🧾 Invoice Tracking</div>', unsafe_allow_html=True)
    
    for invoice in st.session_state.invoices:
        status_color = "success-card" if invoice["status"] == "Paid" else "warning-card" if invoice["status"] == "Pending" else "critical-card"
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"""
            <div class="card {status_color}">
                <h4>Invoice {invoice['id']}</h4>
                <p>Guest: {invoice['guest']} | Amount: ${invoice['amount']}</p>
                <p>Status: {invoice['status']} | Due: {invoice['due_date']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("📧 Remind", key=f"remind_{invoice['id']}"):
                st.success(f"Reminder sent for {invoice['id']}")
        
        with col3:
            if st.button("✅ Paid", key=f"paid_{invoice['id']}"):
                invoice["status"] = "Paid"
                st.rerun()

def show_payment_processing():
    st.markdown('<div class="sub-header">💳 Payment Collection</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Process Payment")
        invoice_id = st.text_input("Invoice ID")
        payment_amount = st.number_input("Payment Amount ($)", min_value=1.0)
        payment_method = st.selectbox("Payment Method", ["Credit Card", "Bank Transfer", "Cash"])
        
        if st.button("✅ Record Payment", use_container_width=True):
            st.success(f"Payment of ${payment_amount} recorded!")
    
    with col2:
        st.markdown("#### Payment Summary")
        total_revenue = sum(b["amount"] for b in st.session_state.bookings if b["status"] == "Confirmed")
        pending_payments = sum(i["amount"] for i in st.session_state.invoices if i["status"] == "Pending")
        
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
        st.metric("Pending Payments", f"${pending_payments:,.0f}")

def show_financial_reports():
    st.markdown('<div class="sub-header">📈 Financial Analytics</div>', unsafe_allow_html=True)
    
    # Sample financial chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue = [125, 118, 132, 145, 158, 167]  # in thousands
    
    fig = px.line(x=months, y=revenue, title='Monthly Revenue Trend ($000)')
    st.plotly_chart(fig, use_container_width=True)
    
    if st.button("📥 Download Financial Report", use_container_width=True):
        financial_data = pd.DataFrame({
            'Month': months,
            'Revenue ($000)': revenue,
            'Expenses ($000)': [85, 82, 88, 92, 95, 98],
            'Profit ($000)': [40, 36, 44, 53, 63, 69]
        })
        
        csv = financial_data.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Report",
            data=csv,
            file_name="financial_report.csv",
            mime="text/csv",
        )

# ==================== VENDOR PORTAL ====================
def show_vendor_portal():
    st.markdown('<div class="main-header">🤝 Vendor Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📦 Assigned Tasks", "✅ Task Completion", "💰 Payment Statements"])
    
    with tab1:
        show_vendor_tasks()
    with tab2:
        show_vendor_completion()
    with tab3:
        show_vendor_statements()

def show_vendor_tasks():
    st.markdown('<div class="sub-header">📦 Service Requests</div>', unsafe_allow_html=True)
    
    vendor_tasks = [r for r in st.session_state.service_requests if r["type"] in ["Laundry", "Catering"] and r["status"] == "Pending"]
    
    for task in vendor_tasks:
        st.markdown(f"""
        <div class="card">
            <h4>{task['type']} Service - Room {task['room']}</h4>
            <p>Details: {task['details']}</p>
            <p>Guest: {task['guest']} | Urgency: {task['urgency']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_vendor_completion():
    st.markdown('<div class="sub-header">✅ Confirm Service Completion</div>', unsafe_allow_html=True)
    
    task_id = st.selectbox("Select Completed Task", [f"{r['id']} - {r['type']}" for r in st.session_state.service_requests if r["type"] in ["Laundry", "Catering"]])
    
    completion_time = st.time_input("Completion Time")
    completion_notes = st.text_area("Completion Notes")
    
    if st.button("✅ Confirm Service Completion", use_container_width=True):
        st.success("Service completion confirmed! Awaiting hotel verification.")

def show_vendor_statements():
    st.markdown('<div class="sub-header">💰 Payment Statements</div>', unsafe_allow_html=True)
    
    months = ["January 2024", "December 2023", "November 2023"]
    selected_month = st.selectbox("Select Month", months)
    
    st.markdown(f"""
    <div class="card success-card">
        <h4>Statement for {selected_month}</h4>
        <p><strong>Services Completed:</strong> 24</p>
        <p><strong>Service Rate:</strong> $75 per service</p>
        <p><strong>Total Amount:</strong> $1,800</p>
        <p><strong>Service Fee (10%):</strong> $180</p>
        <hr>
        <h4>Net Payment: $1,620</h4>
        <p><strong>Status:</strong> Scheduled for payment</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📥 Download Statement", use_container_width=True):
        statement_data = f"Grand Stay Hotel - Vendor Statement\nMonth: {selected_month}\nServices: 24\nAmount: $1,800\nNet Payment: $1,620"
        st.download_button(
            label="⬇️ Download Statement",
            data=statement_data,
            file_name=f"vendor_statement_{selected_month.replace(' ', '_')}.txt",
            mime="text/plain",
        )

if __name__ == "__main__":
    main()
    