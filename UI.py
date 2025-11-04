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

# Custom CSS for sophisticated styling with improved visibility
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #A0D2E8;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Playfair Display', serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        padding: 1rem;
        border-radius: 15px;
        background: linear-gradient(145deg, #ffffff, #494D5F);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.8rem;
        color: #A0D2E8;
        margin-bottom: 1.5rem;
        font-weight: 500;
        border-bottom: 3px solid #3498DB;
        padding-bottom: 0.8rem;
        font-family: 'Montserrat', sans-serif;
    }
    .card {
        background: white;
        color: #8458B3;
        padding: 1.8rem;
        border-radius: 15px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 5px solid #3498DB;
        border: 1px solid #e0e0e0;
    }
    .success-card {
        border-left: 5px solid #27AE60;
        background: white;
        color: #2C3E50;
    }
    .warning-card {
        border-left: 5px solid #F39C12;
        background: white;
        color: #2C3E50;
    }
    .critical-card {
        border-left: 5px solid #E74C3C;
        background: white;
        color: #2C3E50;
    }
    .demo-account {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .role-selector {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stApp {
        background-color: #494D5F;
    }
    .main .block-container {
        padding-top: 2rem;
        background-color: #ffffff;
    }
    .elegant-cover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
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

# Enhanced demo accounts with more sample data
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
    ]
}

# Real-time data storage in session state for demo purposes
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
        <div class="elegant-subtitle">Luxury Hospitality Management System</div>
    </div>
    """, unsafe_allow_html=True)
    
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

def show_main_application():
    # Role-based navigation
    st.sidebar.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 10px; color: white; text-align: center;">
        <h3>Welcome, {st.session_state.current_user['name']}</h3>
        <p><strong>Role:</strong> {st.session_state.current_role}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Role selector for multi-role staff
    if st.session_state.current_role in ["Front Desk Officer", "Housekeeping Staff", "Maintenance Staff"]:
        available_roles = ["Front Desk Officer", "Housekeeping Staff", "Maintenance Staff"]
        selected_role = st.sidebar.selectbox(
            "Switch Role",
            available_roles,
            index=available_roles.index(st.session_state.current_role)
        )
        if selected_role != st.session_state.current_role:
            st.session_state.current_role = selected_role
            st.rerun()
    
    # Main application based on role
    if st.session_state.current_role == "Guest":
        show_guest_portal()
    elif st.session_state.current_role == "Front Desk Officer":
        show_front_desk_portal()
    elif st.session_state.current_role in ["Housekeeping Staff", "Maintenance Staff"]:
        show_staff_portal()
    elif st.session_state.current_role == "Hotel Manager":
        show_manager_portal()
    elif st.session_state.current_role == "Billing Officer":
        show_billing_portal()
    elif st.session_state.current_role == "Vendor":
        show_vendor_portal()
    
    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.current_role = None
        st.rerun()

# Guest Portal Functions
def show_guest_portal():
    st.markdown('<div class="main-header">👤 Guest Portal - Grand Stay Hotel</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Book Room", "📋 My Bookings", "🛎️ Service Requests", "⭐ Leave Review"])
    
    with tab1:
        show_booking_flow()
    
    with tab2:
        show_guest_bookings()
    
    with tab3:
        show_service_requests()
    
    with tab4:
        show_review_system()

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
                "special_requests": special_requests
            }
            st.session_state.bookings.append(new_booking)
            
            st.success("🎉 Booking confirmed! Provisional invoice generated. Please complete payment within 15 minutes.")
            
            # Display provisional invoice
            st.markdown(f"""
            <div class="card success-card">
                <h4>📄 Provisional Invoice</h4>
                <p><strong>Booking ID:</strong> {booking_id}</p>
                <p><strong>Payment Deadline:</strong> 15 minutes from now</p>
                <p><strong>Room:</strong> {room_type} for {nights} nights</p>
                <p><strong>Total Amount:</strong> ${total_price}</p>
                <p style="color: #E74C3C;"><strong>⚠️ Important:</strong> Booking will auto-cancel if payment not completed in 15 minutes</p>
            </div>
            """, unsafe_allow_html=True)

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
        st.success("Service request submitted! Our staff will attend to it shortly.")

def show_review_system():
    st.markdown('<div class="sub-header">⭐ Share Your Experience</div>', unsafe_allow_html=True)
    
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
        st.success("Thank you for your valuable feedback!")

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
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Expected Arrivals", "15", "2 from yesterday")
    with col2:
        st.metric("Scheduled Departures", "12", "-1 from yesterday")
    with col3:
        st.metric("Current Occupancy", f"{occupancy_rate:.1f}%", "5%")
    with col4:
        pending_requests = len([r for r in st.session_state.service_requests if r["status"] == "Pending"])
        st.metric("Pending Requests", str(pending_requests), "3 new")
    
    # Room Status Grid
    st.markdown("#### 🏨 Room Status Overview")
    
    # Convert room data to DataFrame
    room_data = []
    for room in st.session_state.rooms:
        room_data.append({
            'Room': room['number'],
            'Type': room['type'],
            'Status': room['status'].title(),
            'Guest': room['guest'] if room['guest'] else '-'
        })
    
    df_rooms = pd.DataFrame(room_data)
    st.dataframe(df_rooms, use_container_width=True)

def show_room_management():
    st.markdown('<div class="sub-header">🛏️ Room Rack Management</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Color-coded room grid
        st.markdown("#### Color-Coded Room Status")
        
        # Create room grid
        cols = st.columns(4)
        for idx, room in enumerate(st.session_state.rooms):
            with cols[idx % 4]:
                status_colors = {
                    "occupied": "#E74C3C",
                    "vacant": "#27AE60", 
                    "cleaning": "#F39C12",
                    "maintenance": "#3CC2CB"
                }
                status_text = {
                    "occupied": "Occupied",
                    "vacant": "Vacant", 
                    "cleaning": "Cleaning",
                    "maintenance": "Maintenance"
                }
                st.markdown(f"""
                <div style="background-color: {status_colors[room['status']]}; 
                            color: white; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 0.5rem;">
                    <h4>Room {room['number']}</h4>
                    <p>{room['type']}</p>
                    <p><strong>{status_text[room['status']]}</strong></p>
                    {f"<p><small>{room['guest']}</small></p>" if room['guest'] else ""}
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Quick Status Update")
        room_numbers = [r["number"] for r in st.session_state.rooms]
        room_number = st.selectbox("Room Number", room_numbers)
        new_status = st.selectbox("Update Status", 
                                 ["vacant", "occupied", "cleaning", "maintenance"])
        
        if st.button("🔄 Update Status", use_container_width=True):
            # Update room status
            for room in st.session_state.rooms:
                if room["number"] == room_number:
                    room["status"] = new_status
                    if new_status == "vacant":
                        room["guest"] = ""
                    break
            st.success(f"Room {room_number} status updated to {new_status}")

def show_checkin_checkout():
    st.markdown('<div class="sub-header">👥 Check-In / Check-Out Workflow</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["✅ Check-In", "🚪 Check-Out"])
    
    with tab1:
        st.markdown("#### Guest Check-In Process")
        
        col1, col2 = st.columns(2)
        with col1:
            booking_ref = st.text_input("Booking Reference")
            guest_name = st.text_input("Guest Name")
            id_type = st.selectbox("ID Type", ["Passport", "Driver's License", "National ID"])
        
        with col2:
            id_number = st.text_input("ID Number")
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
            st.success(f"Guest checked into Room {assigned_room} successfully!")
    
    with tab2:
        st.markdown("#### Guest Check-Out Process")
        
        col1, col2 = st.columns(2)
        with col1:
            occupied_rooms = [r["number"] for r in st.session_state.rooms if r["status"] == "occupied"]
            checkout_room = st.selectbox("Select Room", occupied_rooms)
            final_bill_review = st.checkbox("Review and confirm final bill")
        
        with col2:
            room_inspection = st.checkbox("Room inspection completed")
            key_return = st.checkbox("Room key returned")
        
        if st.button("💰 Process Check-Out & Payment", use_container_width=True):
            # Update room status
            for room in st.session_state.rooms:
                if room["number"] == checkout_room:
                    room["status"] = "cleaning"
                    room["guest"] = ""
                    break
            st.success("Check-out completed successfully!")

def show_request_queue():
    st.markdown('<div class="sub-header">📋 Service Request Queue</div>', unsafe_allow_html=True)
    
    # Filter pending requests
    pending_requests = [r for r in st.session_state.service_requests if r["status"] == "Pending"]
    
    if not pending_requests:
        st.info("No pending service requests.")
        return
    
    for req in pending_requests:
        urgency_color = {"High": "critical-card", "Medium": "warning-card", "Low": "card"}[req["urgency"]]
        
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"""
            <div class="card {urgency_color}">
                <h4>{req['type']} - Room {req['room']}</h4>
                <p>Request ID: {req['id']} | Submitted: {req['time']}</p>
                <p>Guest: {req['guest']}</p>
                <p>Status: <strong>{req['status']}</strong> | Urgency: {req['urgency']}</p>
                <p>Details: {req['details']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            assign_to = st.selectbox(f"Assign Staff", ["Housekeeping", "Maintenance", "Catering"], key=f"assign_{req['id']}")
        
        with col3:
            if st.button("✅ Complete", key=f"complete_{req['id']}"):
                req["status"] = "Completed"
                st.success(f"Request {req['id']} marked as completed!")

# Staff Portal Functions
def show_staff_portal():
    st.markdown(f'<div class="main-header">👷 {st.session_state.current_role} Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 My Tasks", "🔄 Task Details", "👥 Role Switch"])
    
    with tab1:
        show_staff_tasks()
    
    with tab2:
        show_task_details()
    
    with tab3:
        show_role_selector()

def show_staff_tasks():
    st.markdown('<div class="sub-header">📋 My Assigned Tasks</div>', unsafe_allow_html=True)
    
    # Filter tasks based on role
    if st.session_state.current_role == "Housekeeping Staff":
        tasks = [r for r in st.session_state.service_requests if r["type"] in ["Housekeeping", "Room Service"] and r["status"] == "Pending"]
    else:  # Maintenance Staff
        tasks = [r for r in st.session_state.service_requests if r["type"] == "Maintenance" and r["status"] == "Pending"]
    
    if not tasks:
        st.info("No tasks assigned.")
        return
    
    for task in tasks:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            priority_color = {"High": "critical-card", "Medium": "warning-card", "Low": "card"}[task["urgency"]]
            st.markdown(f"""
            <div class="card {priority_color}">
                <h4>{task['type']} - {task['room']}</h4>
                <p>Task ID: {task['id']} | Guest: {task['guest']}</p>
                <p>Priority: <strong>{task['priority']}</strong> | Status: {task['status']}</p>
                <p>Details: {task['details']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            new_status = st.selectbox("Update Status", 
                                    ["Pending", "In Progress", "Completed", "On Hold"],
                                    key=f"status_{task['id']}")
        
        with col3:
            if st.button("🔄 Update", key=f"update_{task['id']}"):
                task["status"] = new_status
                st.success(f"Task {task['id']} status updated!")

def show_task_details():
    st.markdown('<div class="sub-header">📝 Task Details & Notes</div>', unsafe_allow_html=True)
    
    # Get tasks for current staff role
    if st.session_state.current_role == "Housekeeping Staff":
        tasks = [r for r in st.session_state.service_requests if r["type"] in ["Housekeeping", "Room Service"]]
    else:  # Maintenance Staff
        tasks = [r for r in st.session_state.service_requests if r["type"] == "Maintenance"]
    
    task_options = [f"{t['id']} - Room {t['room']} {t['type']}" for t in tasks]
    selected_task = st.selectbox("Select Task", task_options)
    
    if selected_task:
        task_id = selected_task.split(" - ")[0]
        task = next((t for t in tasks if t["id"] == task_id), None)
        
        if task:
            col1, col2 = st.columns(2)
            with col1:
                st.text_area("Task Notes", value=task.get("notes", ""), placeholder="Add notes about the task...", key=f"notes_{task_id}")
                st.file_uploader("Attach Photos", type=['jpg', 'png', 'jpeg'], key=f"upload_{task_id}")
            
            with col2:
                st.markdown("#### Completion Proof")
                completion_time = st.time_input("Actual Completion Time", datetime.now().time(), key=f"time_{task_id}")
                materials_used = st.text_input("Materials Used", key=f"materials_{task_id}")
                
                if st.button("✅ Mark as Complete", use_container_width=True, key=f"complete_{task_id}"):
                    task["status"] = "Completed"
                    st.success("Task completed and submitted for review!")

def show_role_selector():
    st.markdown('<div class="role-selector">👥 Multi-Role Access Switch</div>', unsafe_allow_html=True)
    
    st.info("As a multi-role staff member, you can switch between different department views:")
    
    available_roles = ["Housekeeping Staff", "Maintenance Staff", "Front Desk Officer"]
    current_index = available_roles.index(st.session_state.current_role)
    
    new_role = st.selectbox("Select Role View", available_roles, index=current_index)
    
    if new_role != st.session_state.current_role:
        if st.button("🔄 Switch Role View", use_container_width=True):
            st.session_state.current_role = new_role
            st.rerun()

# Manager Portal Functions
def show_manager_portal():
    st.markdown('<div class="main-header">👨‍💼 Hotel Manager Dashboard</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Analytics", "👥 Staff Management", "📊 Reports", "⚙️ Settings"])
    
    with tab1:
        show_manager_analytics()
    
    with tab2:
        show_staff_management()
    
    with tab3:
        show_manager_reports()
    
    with tab4:
        show_system_settings()

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
    st.markdown('<div class="sub-header">👥 Staff Performance & Scheduling</div>', unsafe_allow_html=True)
    
    # Staff data
    staff_data = [
        {"name": "Emily Frontdesk", "role": "Front Desk", "shift": "Morning", "performance": 95},
        {"name": "Maria Cleaner", "role": "Housekeeping", "shift": "Day", "performance": 88},
        {"name": "Mike Technician", "role": "Maintenance", "shift": "Evening", "performance": 92},
        {"name": "Lisa Accountant", "role": "Billing", "shift": "Morning", "performance": 96}
    ]
    
    # Display staff performance
    for staff in staff_data:
        with st.expander(f"{staff['name']} - {staff['role']} ({staff['shift']} Shift)"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Performance Score", f"{staff['performance']}%")
            with col2:
                st.metric("Tasks Completed", "24/25")
            with col3:
                st.metric("Guest Rating", "4.8/5")
            
            # Schedule adjustment
            new_shift = st.selectbox("Adjust Shift", ["Morning", "Day", "Evening", "Night"], 
                                   key=f"shift_{staff['name']}")
            if st.button("Update Schedule", key=f"update_{staff['name']}"):
                st.success(f"Schedule updated for {staff['name']}")

def show_manager_reports():
    st.markdown('<div class="sub-header">📊 Management Reports</div>', unsafe_allow_html=True)
    
    report_type = st.selectbox("Select Report Type", 
                              ["Daily Occupancy Report", "Revenue Analysis", "Guest Satisfaction", "Staff Performance"])
    
    if report_type == "Daily Occupancy Report":
        # Generate sample occupancy data
        dates = pd.date_range(start='2024-01-01', end='2024-01-07')
        occupancy_rates = [65, 72, 68, 85, 92, 95, 88]
        
        fig = px.line(x=dates, y=occupancy_rates, title='Weekly Occupancy Rates')
        st.plotly_chart(fig, use_container_width=True)
        
        # Export option
        if st.button("📄 Generate PDF Report"):
            st.success("PDF report generated and saved to system!")

def show_system_settings():
    st.markdown('<div class="sub-header">⚙️ System Configuration</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Room Rate Configuration")
        room_types = ["Single", "Double", "Suite", "Deluxe"]
        for room_type in room_types:
            new_rate = st.number_input(f"{room_type} Rate ($)", min_value=50, max_value=1000, value=150, step=10, key=f"rate_{room_type}")
        
        st.markdown("#### System Preferences")
        auto_checkout = st.checkbox("Automatic Check-out at 11:00 AM")
        maintenance_mode = st.checkbox("Enable Maintenance Mode")
    
    with col2:
        st.markdown("#### Notification Settings")
        email_alerts = st.checkbox("Email Alerts for High Priority Issues")
        sms_alerts = st.checkbox("SMS Alerts for Critical Issues")
        report_frequency = st.selectbox("Report Frequency", ["Daily", "Weekly", "Monthly"])
        
        if st.button("💾 Save Configuration", use_container_width=True):
            st.success("System configuration saved successfully!")

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
    st.markdown('<div class="sub-header">🧾 Invoice Generation & Tracking</div>', unsafe_allow_html=True)
    
    # Sample invoices
    sample_invoices = [
        {"id": "INV001", "guest": "John Smith", "amount": "$450", "status": "Paid", "due_date": "2024-01-15"},
        {"id": "INV002", "guest": "Sarah Johnson", "amount": "$320", "status": "Pending", "due_date": "2024-01-16"},
        {"id": "INV003", "guest": "Mike Brown", "amount": "$680", "status": "Overdue", "due_date": "2024-01-10"},
        {"id": "INV004", "guest": "Robert Wilson", "amount": "$540", "status": "Paid", "due_date": "2024-01-14"}
    ]
    
    # Display invoices
    for invoice in sample_invoices:
        status_color = "success-card" if invoice["status"] == "Paid" else "warning-card" if invoice["status"] == "Pending" else "critical-card"
        
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"""
            <div class="card {status_color}">
                <h4>Invoice {invoice['id']}</h4>
                <p>Guest: {invoice['guest']} | Amount: {invoice['amount']}</p>
                <p>Status: <strong>{invoice['status']}</strong> | Due Date: {invoice['due_date']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("📄 Generate PDF", key=f"pdf_{invoice['id']}"):
                st.success(f"PDF invoice {invoice['id']} generated!")
        
        with col3:
            if st.button("📧 Email", key=f"email_{invoice['id']}"):
                st.success(f"Invoice {invoice['id']} sent to guest!")

def show_payment_processing():
    st.markdown('<div class="sub-header">💳 Payment Collection & Reconciliation</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Process Payment")
        invoice_id = st.text_input("Invoice ID")
        payment_amount = st.number_input("Payment Amount ($)", min_value=1.0, step=10.0)
        payment_method = st.selectbox("Payment Method", 
                                     ["Credit Card", "Debit Card", "Cash", "Bank Transfer", "Digital Wallet"])
        
        if st.button("✅ Record Payment", use_container_width=True):
            st.success(f"Payment of ${payment_amount} recorded for invoice {invoice_id}")
    
    with col2:
        st.markdown("#### Payment Reconciliation")
        st.file_uploader("Upload Bank Statement", type=['csv', 'xlsx'])
        reconciliation_date = st.date_input("Reconciliation Date")
        
        if st.button("🔄 Reconcile Payments", use_container_width=True):
            st.success("Payments reconciled successfully!")

def show_financial_reports():
    st.markdown('<div class="sub-header">📈 Financial Analytics</div>', unsafe_allow_html=True)
    
    # Sample financial data
    revenue_data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [125000, 118000, 132000, 145000, 158000, 167000],
        'Expenses': [85000, 82000, 88000, 92000, 95000, 98000]
    }
    
    fig = px.line(revenue_data, x='Month', y=['Revenue', 'Expenses'], 
                  title='Monthly Revenue vs Expenses')
    st.plotly_chart(fig, use_container_width=True)
    
    # Key financial metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Monthly Revenue", "$167,000", "8.2%")
    with col2:
        st.metric("Monthly Profit", "$69,000", "12.5%")
    with col3:
        st.metric("Occupancy Revenue", "$145,200", "7.8%")
    with col4:
        st.metric("Other Revenue", "$21,800", "15.3%")

# Vendor Portal Functions (Updated)
def show_vendor_portal():
    st.markdown('<div class="main-header">🚚 Vendor Management Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📦 Supply Orders", "💰 Billing", "📊 Performance"])
    
    with tab1:
        show_vendor_orders()
    
    with tab2:
        show_vendor_billing()
    
    with tab3:
        show_vendor_performance()

def show_vendor_orders():
    st.markdown('<div class="sub-header">📦 Supply Chain Management</div>', unsafe_allow_html=True)
    
    # Sample vendor orders
    vendor_orders = [
        {"id": "VO001", "item": "Linens & Bedding", "quantity": "50 sets", "status": "Delivered", "date": "2024-01-10"},
        {"id": "VO002", "item": "Toiletries", "quantity": "200 units", "status": "In Transit", "date": "2024-01-12"},
        {"id": "VO003", "item": "Cleaning Supplies", "quantity": "25 cases", "status": "Processing", "date": "2024-01-15"},
        {"id": "VO004", "item": "Mini-bar Items", "quantity": "150 units", "status": "Delivered", "date": "2024-01-08"}
    ]
    
    # Display orders without view button
    for order in vendor_orders:
        status_color = "success-card" if order["status"] == "Delivered" else "warning-card" if order["status"] == "In Transit" else "card"
        
        st.markdown(f"""
        <div class="card {status_color}">
            <h4>Order {order['id']}</h4>
            <p><strong>Item:</strong> {order['item']}</p>
            <p><strong>Quantity:</strong> {order['quantity']}</p>
            <p><strong>Status:</strong> {order['status']} | <strong>Order Date:</strong> {order['date']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_vendor_billing():
    st.markdown('<div class="sub-header">💰 Vendor Payments & Statements</div>', unsafe_allow_html=True)
    
    # Sample vendor invoices
    vendor_invoices = [
        {"id": "VINV001", "amount": "$2,450", "status": "Paid", "due_date": "2024-01-05", "period": "Dec 2023"},
        {"id": "VINV002", "amount": "$3,120", "status": "Pending", "due_date": "2024-01-20", "period": "Jan 2024"},
        {"id": "VINV003", "amount": "$1,890", "status": "Approved", "due_date": "2024-02-05", "period": "Jan 2024"}
    ]
    
    for invoice in vendor_invoices:
        status_color = "success-card" if invoice["status"] == "Paid" else "warning-card" if invoice["status"] == "Approved" else "card"
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class="card {status_color}">
                <h4>Invoice {invoice['id']}</h4>
                <p><strong>Amount:</strong> {invoice['amount']} | <strong>Status:</strong> {invoice['status']}</p>
                <p><strong>Period:</strong> {invoice['period']} | <strong>Due Date:</strong> {invoice['due_date']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("📄 Download PDF", key=f"vendor_pdf_{invoice['id']}"):
                # Create a sample PDF (in real implementation, generate actual PDF)
                pdf_data = f"""
                Grand Stay Hotel - Vendor Statement
                Invoice ID: {invoice['id']}
                Amount: {invoice['amount']}
                Period: {invoice['period']}
                Status: {invoice['status']}
                Due Date: {invoice['due_date']}
                
                Thank you for your partnership!
                """
                
                # Create download button for PDF
                st.download_button(
                    label="⬇️ Save PDF",
                    data=pdf_data,
                    file_name=f"vendor_statement_{invoice['id']}.txt",
                    mime="text/plain",
                    key=f"download_{invoice['id']}"
                )
                st.success("PDF statement ready for download!")

def show_vendor_performance():
    st.markdown('<div class="sub-header">📊 Vendor Performance Metrics</div>', unsafe_allow_html=True)
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("On-Time Delivery", "94%", "2%")
    with col2:
        st.metric("Quality Rating", "4.7/5", "0.2")
    with col3:
        st.metric("Orders This Month", "18", "3")
    with col4:
        st.metric("Response Time", "2.1 hrs", "-0.5 hrs")
    
    # Performance chart
    performance_data = {
        'Month': ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'OnTime Delivery %': [89, 92, 91, 94, 93, 94],
        'Quality Score': [4.5, 4.6, 4.5, 4.7, 4.7, 4.7]
    }
    
    fig = px.line(performance_data, x='Month', y=['OnTime Delivery %', 'Quality Score'],
                  title='Vendor Performance Trend')
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()