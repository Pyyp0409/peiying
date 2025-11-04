# app.py
import streamlit as st
import supabase
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

# Page configuration
st.set_page_config(
    page_title="Grand Stay Hotel Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for sophisticated styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #34495E;
        margin-bottom: 1rem;
        font-weight: 400;
        border-bottom: 2px solid #3498DB;
        padding-bottom: 0.5rem;
    }
    .card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #3498DB;
    }
    .success-card {
        border-left: 4px solid #27AE60;
    }
    .warning-card {
        border-left: 4px solid #F39C12;
    }
    .critical-card {
        border-left: 4px solid #E74C3C;
    }
    .demo-account {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .role-selector {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
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

# Authentication system
def authenticate_user(email, password, role):
    # In a real application, this would verify against Supabase
    for account_role, accounts in DEMO_ACCOUNTS.items():
        if role == account_role:
            for account in accounts:
                if account["email"] == email and account["password"] == password:
                    return account
    return None

# Main application
def main():
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
    st.markdown('<div class="main-header">🏨 Grand Stay Hotel Management System</div>', unsafe_allow_html=True)
    
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
            st.success("🎉 Booking confirmed! Provisional invoice generated. Please complete payment within 15 minutes.")
            
            # Display provisional invoice
            st.markdown("""
            <div class="card success-card">
                <h4>📄 Provisional Invoice</h4>
                <p><strong>Payment Deadline:</strong> 15 minutes from now</p>
                <p><strong>Room:</strong> {room_type} for {nights} nights</p>
                <p><strong>Total Amount:</strong> ${total_price}</p>
                <p style="color: #E74C3C;"><strong>⚠️ Important:</strong> Booking will auto-cancel if payment not completed in 15 minutes</p>
            </div>
            """.format(room_type=room_type, nights=nights, total_price=total_price), unsafe_allow_html=True)

def show_guest_bookings():
    st.markdown('<div class="sub-header">📋 My Current Bookings</div>', unsafe_allow_html=True)
    
    # Sample booking data
    sample_bookings = [
        {"id": "BK001", "room": "Deluxe Suite", "check_in": "2024-01-15", "check_out": "2024-01-18", "status": "Confirmed", "amount": "$1500"},
        {"id": "BK002", "room": "Single Room", "check_in": "2024-02-01", "check_out": "2024-02-03", "status": "Pending", "amount": "$300"}
    ]
    
    for booking in sample_bookings:
        status_color = "success-card" if booking["status"] == "Confirmed" else "warning-card"
        st.markdown(f"""
        <div class="card {status_color}">
            <h4>Booking #{booking['id']} - {booking['room']}</h4>
            <p><strong>Dates:</strong> {booking['check_in']} to {booking['check_out']}</p>
            <p><strong>Status:</strong> {booking['status']} | <strong>Amount:</strong> {booking['amount']}</p>
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
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Expected Arrivals", "15", "2 from yesterday")
    with col2:
        st.metric("Scheduled Departures", "12", "-1 from yesterday")
    with col3:
        st.metric("Current Occupancy", "78%", "5%")
    with col4:
        st.metric("Pending Requests", "8", "3 new")
    
    # Room Status Grid
    st.markdown("#### 🏨 Room Status Overview")
    room_data = {
        'Room': ['101', '102', '103', '201', '202', '203', '301', '302'],
        'Type': ['Single', 'Double', 'Suite', 'Single', 'Double', 'Suite', 'Deluxe', 'Deluxe'],
        'Status': ['Occupied', 'Vacant Clean', 'Under Cleaning', 'Occupied', 'Under Maintenance', 'Vacant Clean', 'Occupied', 'Vacant Clean'],
        'Guest': ['John Smith', '-', '-', 'Sarah Johnson', '-', '-', 'Mike Brown', '-']
    }
    
    df_rooms = pd.DataFrame(room_data)
    st.dataframe(df_rooms, use_container_width=True)

def show_room_management():
    st.markdown('<div class="sub-header">🛏️ Room Rack Management</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Color-coded room grid
        st.markdown("#### Color-Coded Room Status")
        rooms = [
            {"number": "101", "status": "occupied", "type": "Single"},
            {"number": "102", "status": "vacant", "type": "Double"},
            {"number": "103", "status": "cleaning", "type": "Suite"},
            {"number": "201", "status": "maintenance", "type": "Single"},
        ]
        
        cols = st.columns(4)
        for idx, room in enumerate(rooms):
            with cols[idx % 4]:
                status_colors = {
                    "occupied": "#E74C3C",
                    "vacant": "#27AE60", 
                    "cleaning": "#F39C12",
                    "maintenance": "#95A5A6"
                }
                st.markdown(f"""
                <div style="background-color: {status_colors[room['status']]}; 
                            color: black; padding: 1rem; border-radius: 10px; text-align: center;">
                    <h4>Room {room['number']}</h4>
                    <p>{room['type']}</p>
                    <p><strong>{room['status'].title()}</strong></p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Quick Status Update")
        room_number = st.selectbox("Room Number", ["101", "102", "103", "201", "202", "203"])
        new_status = st.selectbox("Update Status", 
                                 ["Vacant Clean", "Occupied", "Under Cleaning", "Under Maintenance"])
        
        if st.button("🔄 Update Status", use_container_width=True):
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
            assigned_room = st.selectbox("Assign Room", ["101", "102", "103", "201", "202", "203"])
            payment_method = st.selectbox("Payment Method", ["Credit Card", "Cash", "Corporate Account"])
        
        if st.button("✅ Complete Check-In", use_container_width=True):
            st.success(f"Guest checked into Room {assigned_room} successfully!")
    
    with tab2:
        st.markdown("#### Guest Check-Out Process")
        
        col1, col2 = st.columns(2)
        with col1:
            checkout_room = st.selectbox("Select Room", ["101", "102", "103", "201", "202", "203"])
            final_bill_review = st.checkbox("Review and confirm final bill")
        
        with col2:
            room_inspection = st.checkbox("Room inspection completed")
            key_return = st.checkbox("Room key returned")
        
        if st.button("💰 Process Check-Out & Payment", use_container_width=True):
            st.success("Check-out completed successfully!")

def show_request_queue():
    st.markdown('<div class="sub-header">📋 Service Request Queue</div>', unsafe_allow_html=True)
    
    # Sample service requests
    requests = [
        {"id": "SR001", "room": "101", "type": "Housekeeping", "urgency": "High", "status": "Pending", "time": "10:30 AM"},
        {"id": "SR002", "room": "203", "type": "Maintenance", "urgency": "Medium", "status": "In Progress", "time": "11:15 AM"},
        {"id": "SR003", "room": "105", "type": "Room Service", "urgency": "Low", "status": "Pending", "time": "11:45 AM"},
    ]
    
    for req in requests:
        urgency_color = {"High": "critical-card", "Medium": "warning-card", "Low": "card"}[req["urgency"]]
        
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"""
            <div class="card {urgency_color}">
                <h4>{req['type']} - Room {req['room']}</h4>
                <p>Request ID: {req['id']} | Submitted: {req['time']}</p>
                <p>Status: <strong>{req['status']}</strong> | Urgency: {req['urgency']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            assign_to = st.selectbox(f"Assign Staff", ["Housekeeping", "Maintenance", "Catering"], key=f"assign_{req['id']}")
        
        with col3:
            if st.button("✅ Complete", key=f"complete_{req['id']}"):
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
    
    # Sample tasks based on role
    if st.session_state.current_role == "Housekeeping Staff":
        tasks = [
            {"id": "T001", "room": "101", "type": "Cleaning", "priority": "High", "status": "Pending", "estimated_time": "45 min"},
            {"id": "T002", "room": "203", "type": "Turndown Service", "priority": "Medium", "status": "Pending", "estimated_time": "20 min"},
        ]
    else:  # Maintenance Staff
        tasks = [
            {"id": "T003", "room": "105", "type": "AC Repair", "priority": "High", "status": "Pending", "estimated_time": "2 hours"},
            {"id": "T004", "room": "Public", "type": "Elevator Check", "priority": "Medium", "status": "Pending", "estimated_time": "1 hour"},
        ]
    
    for task in tasks:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            priority_color = {"High": "critical-card", "Medium": "warning-card", "Low": "card"}[task["priority"]]
            st.markdown(f"""
            <div class="card {priority_color}">
                <h4>{task['type']} - {task['room']}</h4>
                <p>Task ID: {task['id']} | Est. Time: {task['estimated_time']}</p>
                <p>Priority: <strong>{task['priority']}</strong> | Status: {task['status']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            new_status = st.selectbox("Update Status", 
                                    ["Pending", "In Progress", "Completed", "On Hold"],
                                    key=f"status_{task['id']}")
        
        with col3:
            if st.button("🔄 Update", key=f"update_{task['id']}"):
                st.success(f"Task {task['id']} status updated!")

def show_task_details():
    st.markdown('<div class="sub-header">📝 Task Details & Notes</div>', unsafe_allow_html=True)
    
    selected_task = st.selectbox("Select Task", ["T001 - Room 101 Cleaning", "T002 - Room 203 Turndown", "T003 - AC Repair"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_area("Task Notes", placeholder="Add notes about the task...")
        st.file_uploader("Attach Photos", type=['jpg', 'png', 'jpeg'])
    
    with col2:
        st.markdown("#### Completion Proof")
        completion_time = st.time_input("Actual Completion Time", datetime.now().time())
        materials_used = st.text_input("Materials Used")
        
        if st.button("✅ Mark as Complete", use_container_width=True):
            st.success("Task completed and submitted for review!")

def show_role_selector():
    st.markdown('<div class="role-selector">👥 Multi-Role Access Switch</div>', unsafe_allow_html=True)
    
    st.info("As a multi-role staff member, you can switch between different department views:")
    
    available_roles = ["Housekeeping Staff", "Maintenance Staff", "Front Desk Officer"]
    current_index = available_roles.index(st.session_state.current_role)
    
    new_role = st.selectbox("Select Role to Switch To", available_roles, index=current_index)
    
    if new_role != st.session_state.current_role:
        if st.button("🔄 Switch Role", use_container_width=True):
            st.session_state.current_role = new_role
            st.rerun()

# Manager Portal Functions
def show_manager_portal():
    st.markdown('<div class="main-header">👨‍💼 Manager Administration Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Dashboard", "📊 Reports", "🤝 Vendors", "👥 Staff", "⚙️ Config"])
    
    with tab1:
        show_manager_dashboard()
    
    with tab2:
        show_reporting_system()
    
    with tab3:
        show_vendor_management()
    
    with tab4:
        show_staff_management()
    
    with tab5:
        show_system_config()

def show_manager_dashboard():
    st.markdown('<div class="sub-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Occupancy Rate", "78%", "5%")
    with col2:
        st.metric("RevPAR", "$156", "$12")
    with col3:
        st.metric("ADR", "$200", "$15")
    with col4:
        st.metric("Guest Satisfaction", "4.2/5", "0.3")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue chart
        revenue_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Revenue': [120000, 150000, 140000, 160000, 180000, 175000]
        })
        fig = px.line(revenue_data, x='Month', y='Revenue', title='Monthly Revenue Trend')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Occupancy chart
        occupancy_data = pd.DataFrame({
            'Room Type': ['Single', 'Double', 'Suite', 'Deluxe'],
            'Occupancy': [75, 82, 65, 90]
        })
        fig = px.bar(occupancy_data, x='Room Type', y='Occupancy', title='Occupancy by Room Type')
        st.plotly_chart(fig, use_container_width=True)

def show_reporting_system():
    st.markdown('<div class="sub-header">📊 Business Intelligence Reports</div>', unsafe_allow_html=True)
    
    report_type = st.selectbox("Select Report Type", [
        "Occupancy & Revenue Report",
        "Reservation Trends", 
        "Cancellation Analysis",
        "Accounts Receivable",
        "Vendor Expense Breakdown",
        "Staff Performance"
    ])
    
    date_range = st.date_input("Report Period", 
                              [datetime.now() - timedelta(days=30), datetime.now()])
    
    if st.button("📄 Generate Report", use_container_width=True):
        st.success(f"Generating {report_type} for selected period...")
        
        # Sample report data
        report_data = pd.DataFrame({
            'Metric': ['Total Revenue', 'Average Occupancy', 'RevPAR', 'ADR', 'Cancellation Rate'],
            'Value': ['$850,000', '78%', '$156', '$200', '12%'],
            'Change': ['+15%', '+5%', '+8%', '+7%', '-3%']
        })
        
        st.dataframe(report_data, use_container_width=True)
        
        # Export options
        st.download_button("📥 Export as CSV", report_data.to_csv(), "hotel_report.csv")

def show_vendor_management():
    st.markdown('<div class="sub-header">🤝 Vendor Management</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Vendor Verification", "Performance", "Payments"])
    
    with tab1:
        st.markdown("#### Vendor Registration & Verification")
        
        col1, col2 = st.columns(2)
        with col1:
            vendor_name = st.text_input("Vendor Company Name")
            service_type = st.selectbox("Service Type", ["Laundry", "Catering", "Transport", "Maintenance", "Entertainment"])
            contact_email = st.text_input("Contact Email")
        
        with col2:
            service_rate = st.number_input("Service Rate ($)", min_value=0)
            contact_phone = st.text_input("Contact Phone")
            documents = st.file_uploader("Business Documents", type=['pdf', 'doc'])
        
        if st.button("✅ Approve Vendor", use_container_width=True):
            st.success(f"Vendor {vendor_name} approved successfully!")
    
    with tab2:
        st.markdown("#### Vendor Performance Evaluation")
        
        vendors = ["ABC Laundry", "XYZ Catering", "Quick Transport"]
        selected_vendor = st.selectbox("Select Vendor", vendors)
        
        rating = st.slider("Service Quality Rating", 1, 5, 4)
        reliability = st.slider("Reliability Score", 1, 5, 4)
        comments = st.text_area("Performance Comments")
        
        if st.button("💾 Save Evaluation", use_container_width=True):
            st.success("Vendor evaluation saved!")

def show_staff_management():
    st.markdown('<div class="sub-header">👥 Staff Scheduling & Management</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Create Duty Roster")
        
        staff_member = st.selectbox("Staff Member", ["Emily Frontdesk", "Maria Cleaner", "Mike Technician"])
        shift_date = st.date_input("Shift Date", datetime.now())
        shift_type = st.selectbox("Shift Type", ["Morning (7AM-3PM)", "Evening (3PM-11PM)", "Night (11PM-7AM)"])
        
        if st.button("📅 Assign Shift", use_container_width=True):
            st.success(f"Shift assigned to {staff_member}")
    
    with col2:
        st.markdown("#### Staff Performance")
        
        # Sample performance data
        performance_data = pd.DataFrame({
            'Staff': ['Emily', 'Maria', 'Mike', 'David'],
            'Tasks Completed': [45, 38, 25, 52],
            'Avg. Rating': [4.5, 4.2, 4.7, 4.8],
            'Attendance': ['95%', '98%', '92%', '100%']
        })
        
        st.dataframe(performance_data, use_container_width=True)

def show_system_config():
    st.markdown('<div class="sub-header">⚙️ System Configuration</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Hotel Settings")
        hotel_name = st.text_input("Hotel Name", "Grand Stay Hotel")
        check_in_time = st.time_input("Standard Check-in Time", datetime.strptime("14:00", "%H:%M").time())
        check_out_time = st.time_input("Standard Check-out Time", datetime.strptime("11:00", "%H:%M").time())
    
    with col2:
        st.markdown("#### Booking Policies")
        auto_cancel_minutes = st.number_input("Auto-cancel Time (minutes)", min_value=1, value=15)
        max_guests_per_room = st.number_input("Max Guests per Room", min_value=1, value=4)
        advance_booking_days = st.number_input("Max Advance Booking (days)", min_value=1, value=365)
    
    if st.button("💾 Save Configuration", use_container_width=True):
        st.success("System configuration updated successfully!")

# Billing Portal Functions
def show_billing_portal():
    st.markdown('<div class="main-header">💰 Billing & Finance Portal</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🧾 Invoices", "💸 Refunds", "📊 Receivables", "🤝 Vendor Payments"])
    
    with tab1:
        show_invoice_management()
    
    with tab2:
        show_refund_processing()
    
    with tab3:
        show_receivables_tracking()
    
    with tab4:
        show_vendor_payments()

def show_invoice_management():
    st.markdown('<div class="sub-header">🧾 Invoice Management</div>', unsafe_allow_html=True)
    
    # Sample invoices
    invoices = [
        {"id": "INV001", "guest": "John Smith", "amount": "$450", "status": "Paid", "due_date": "2024-01-10"},
        {"id": "INV002", "guest": "Sarah Johnson", "amount": "$320", "status": "Overdue", "due_date": "2024-01-05"},
        {"id": "INV003", "guest": "Mike Brown", "amount": "$680", "status": "Pending", "due_date": "2024-01-15"},
    ]
    
    for invoice in invoices:
        status_color = "success-card" if invoice["status"] == "Paid" else "critical-card" if invoice["status"] == "Overdue" else "warning-card"
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"""
            <div class="card {status_color}">
                <h4>Invoice {invoice['id']}</h4>
                <p>Guest: {invoice['guest']} | Amount: {invoice['amount']}</p>
                <p>Status: <strong>{invoice['status']}</strong> | Due: {invoice['due_date']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("📧 Send Reminder", key=f"remind_{invoice['id']}"):
                st.success(f"Reminder sent for {invoice['id']}")
        
        with col3:
            if st.button("📄 View", key=f"view_{invoice['id']}"):
                st.info(f"Showing details for {invoice['id']}")

def show_refund_processing():
    st.markdown('<div class="sub-header">💸 Refund Processing</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Refund Request")
        booking_id = st.text_input("Booking Reference")
        refund_reason = st.selectbox("Refund Reason", ["Cancellation", "Service Issue", "Overcharge", "Other"])
        original_amount = st.number_input("Original Amount ($)", min_value=0.0)
        refund_amount = st.number_input("Refund Amount ($)", min_value=0.0, max_value=original_amount)
        
        if st.button("🔄 Process Refund", use_container_width=True):
            st.success(f"Refund of ${refund_amount} processed successfully!")
    
    with col2:
        st.markdown("#### Refund Calculator")
        cancellation_fee = st.number_input("Cancellation Fee (%)", min_value=0, max_value=100, value=10)
        nights_stayed = st.number_input("Nights Stayed", min_value=0)
        total_nights = st.number_input("Total Booked Nights", min_value=1)
        
        if total_nights > 0:
            refund_percent = max(0, 100 - cancellation_fee - (nights_stayed / total_nights * 100))
            st.metric("Eligible Refund", f"{refund_percent:.1f}%")

def show_receivables_tracking():
    st.markdown('<div class="sub-header">📊 Accounts Receivable Tracking</div>', unsafe_allow_html=True)
    
    # Sample receivables data
    receivables_data = pd.DataFrame({
        'Customer': ['Corporate A', 'Travel Agency B', 'Individual C', 'Group Booking D'],
        'Amount Due': [5000, 3200, 450, 1800],
        'Due Date': ['2024-01-15', '2024-01-20', '2024-01-10', '2024-01-25'],
        'Status': ['Current', 'Current', 'Overdue', 'Current']
    })
    
    st.dataframe(receivables_data, use_container_width=True)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Receivable", "$10,450")
    with col2:
        st.metric("Overdue Amount", "$450")
    with col3:
        st.metric("Avg. Days Outstanding", "15.2")

def show_vendor_payments():
    st.markdown('<div class="sub-header">🤝 Vendor Payment Processing</div>', unsafe_allow_html=True)
    
    # Sample vendor statements
    vendors = [
        {"name": "ABC Laundry", "completed_tasks": 45, "rate": "$50", "total": "$2250", "service_fee": "$225", "net_payable": "$2025"},
        {"name": "XYZ Catering", "completed_tasks": 12, "rate": "$200", "total": "$2400", "service_fee": "$240", "net_payable": "$2160"},
    ]
    
    for vendor in vendors:
        st.markdown(f"""
        <div class="card">
            <h4>{vendor['name']} - Monthly Statement</h4>
            <p>Completed Tasks: {vendor['completed_tasks']} × Rate: {vendor['rate']} = Total: {vendor['total']}</p>
            <p>Service Fee (10%): {vendor['service_fee']} | <strong>Net Payable: {vendor['net_payable']}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"📄 Generate Statement", key=f"stmt_{vendor['name']}"):
                st.success(f"Statement generated for {vendor['name']}")
        with col2:
            if st.button(f"💳 Process Payment", key=f"pay_{vendor['name']}"):
                st.success(f"Payment processed for {vendor['name']}")

# Vendor Portal Functions
def show_vendor_portal():
    st.markdown('<div class="main-header">🤝 Vendor Portal - Grand Stay Hotel</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Assigned Tasks", "✅ Task Completion", "💰 Payment Statements"])
    
    with tab1:
        show_vendor_tasks()
    
    with tab2:
        show_vendor_completion()
    
    with tab3:
        show_vendor_statements()

def show_vendor_tasks():
    st.markdown('<div class="sub-header">📋 Tasks Assigned to Your Company</div>', unsafe_allow_html=True)
    
    # Sample vendor tasks
    tasks = [
        {"id": "VT001", "type": "Laundry Service", "location": "Main Hotel", "urgency": "High", "deadline": "Today 4:00 PM"},
        {"id": "VT002", "type": "Catering Setup", "location": "Conference Room A", "urgency": "Medium", "deadline": "Tomorrow 9:00 AM"},
    ]
    
    for task in tasks:
        col1, col2 = st.columns([3, 1])
        with col1:
            urgency_color = {"High": "critical-card", "Medium": "warning-card", "Low": "card"}[task["urgency"]]
            st.markdown(f"""
            <div class="card {urgency_color}">
                <h4>{task['type']}</h4>
                <p>Task ID: {task['id']} | Location: {task['location']}</p>
                <p>Deadline: <strong>{task['deadline']}</strong> | Urgency: {task['urgency']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("👀 View Details", key=f"view_{task['id']}"):
                st.info(f"Showing details for task {task['id']}")

def show_vendor_completion():
    st.markdown('<div class="sub-header">✅ Confirm Task Completion</div>', unsafe_allow_html=True)
    
    task_id = st.selectbox("Select Completed Task", ["VT001 - Laundry Service", "VT002 - Catering Setup"])
    
    col1, col2 = st.columns(2)
    with col1:
        completion_time = st.time_input("Actual Completion Time", datetime.now().time())
        materials_used = st.text_area("Materials/Costs Incurred")
    
    with col2:
        completion_notes = st.text_area("Completion Notes")
        upload_proof = st.file_uploader("Upload Completion Proof", type=['jpg', 'png', 'pdf'])
    
    if st.button("✅ Confirm Service Completion", use_container_width=True):
        st.success("Service completion confirmed! Awaiting hotel verification.")

def show_vendor_statements():
    st.markdown('<div class="sub-header">💰 Monthly Payment Statements</div>', unsafe_allow_html=True)
    
    # Sample statement data
    months = ["January 2024", "December 2023", "November 2023"]
    selected_month = st.selectbox("Select Month", months)
    
    st.markdown(f"""
    <div class="card success-card">
        <h4>Statement for {selected_month}</h4>
        <p><strong>Total Completed Tasks:</strong> 45</p>
        <p><strong>Agreed Rate:</strong> $50 per task</p>
        <p><strong>Gross Amount:</strong> $2,250</p>
        <p><strong>Grand Stay Service Fee (10%):</strong> $225</p>
        <hr>
        <h4>Net Payment Due: $2,025</h4>
        <p><strong>Payment Status:</strong> Scheduled for 2024-01-15</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📄 Download Statement PDF", use_container_width=True):
        st.success("Statement PDF generated for download!")

if __name__ == "__main__":
    main()