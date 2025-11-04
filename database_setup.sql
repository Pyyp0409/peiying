-- database_setup.sql
-- Create tables for Grand Stay Hotel Management System

-- Users and Profiles table
CREATE TABLE
IF NOT EXISTS profiles
(
    id UUID REFERENCES auth.users ON
DELETE CASCADE PRIMARY KEY,
    email TEXT
UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK
(role IN
('guest', 'front_desk', 'housekeeping', 'maintenance', 'manager', 'billing', 'vendor')),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW
(),
    updated_at TIMESTAMPTZ DEFAULT NOW
()
);

-- Rooms table
CREATE TABLE
IF NOT EXISTS rooms
(
    id SERIAL PRIMARY KEY,
    room_number TEXT UNIQUE NOT NULL,
    room_type TEXT NOT NULL CHECK
(room_type IN
('single', 'double', 'suite', 'deluxe')),
    status TEXT NOT NULL CHECK
(status IN
('vacant', 'occupied', 'cleaning', 'maintenance')),
    rate_per_night DECIMAL
(10,2) NOT NULL,
    features JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW
(),
    updated_at TIMESTAMPTZ DEFAULT NOW
()
);

-- Bookings table
CREATE TABLE
IF NOT EXISTS bookings
(
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES profiles
(id) ON
DELETE CASCADE,
    room_number TEXT
REFERENCES rooms
(room_number) ON
DELETE CASCADE,
    check_in DATE
NOT NULL,
    check_out DATE NOT NULL,
    num_guests INTEGER NOT NULL CHECK
(num_guests > 0),
    room_type TEXT NOT NULL CHECK
(room_type IN
('single', 'double', 'suite', 'deluxe')),
    total_amount DECIMAL
(10,2) NOT NULL CHECK
(total_amount >= 0),
    status TEXT NOT NULL CHECK
(status IN
('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled')),
    special_requests TEXT,
    payment_status TEXT DEFAULT 'pending' CHECK
(payment_status IN
('pending', 'paid', 'failed', 'refunded')),
    created_at TIMESTAMPTZ DEFAULT NOW
()
);

-- Tasks table
CREATE TABLE
IF NOT EXISTS tasks
(
    id SERIAL PRIMARY KEY,
    task_type TEXT NOT NULL CHECK
(task_type IN
('housekeeping', 'maintenance', 'room_service', 'concierge')),
    room_number TEXT REFERENCES rooms
(room_number) ON
DELETE CASCADE,
    assigned_to UUID
REFERENCES profiles
(id) ON
DELETE
SET NULL
,
    description TEXT NOT NULL,
    priority TEXT NOT NULL CHECK
(priority IN
('low', 'medium', 'high')),
    status TEXT NOT NULL CHECK
(status IN
('pending', 'in_progress', 'completed', 'cancelled')),
    estimated_duration TEXT,
    completion_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW
(),
    updated_at TIMESTAMPTZ DEFAULT NOW
()
);

-- Invoices table
CREATE TABLE
IF NOT EXISTS invoices
(
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES bookings
(id) ON
DELETE CASCADE,
    guest_name TEXT
NOT NULL,
    amount DECIMAL
(10,2) NOT NULL CHECK
(amount >= 0),
    status TEXT NOT NULL CHECK
(status IN
('pending', 'paid', 'overdue', 'cancelled')),
    due_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW
()
);

-- Vendors table
CREATE TABLE
IF NOT EXISTS vendors
(
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    service_type TEXT NOT NULL CHECK
(service_type IN
('laundry', 'catering', 'transport', 'maintenance', 'entertainment')),
    contact_email TEXT NOT NULL,
    contact_phone TEXT,
    service_rate DECIMAL
(10,2) NOT NULL CHECK
(service_rate >= 0),
    approval_status TEXT DEFAULT 'pending' CHECK
(approval_status IN
('pending', 'approved', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW
()
);

-- Service Requests table
CREATE TABLE
IF NOT EXISTS service_requests
(
    id SERIAL PRIMARY KEY,
    guest_name TEXT NOT NULL,
    room_number TEXT NOT NULL,
    service_type TEXT NOT NULL,
    description TEXT NOT NULL,
    urgency TEXT NOT NULL CHECK
(urgency IN
('low', 'medium', 'high')),
    status TEXT DEFAULT 'pending' CHECK
(status IN
('pending', 'assigned', 'in_progress', 'completed')),
    assigned_to UUID REFERENCES profiles
(id) ON
DELETE
SET NULL
,
    created_at TIMESTAMPTZ DEFAULT NOW
()
);

-- Reviews table
CREATE TABLE
IF NOT EXISTS reviews
(
    id SERIAL PRIMARY KEY,
    guest_name TEXT NOT NULL,
    room_number TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK
(rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW
()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for clean setup)
DO $$ 
BEGIN
    DROP POLICY
    IF EXISTS "Public profiles are viewable by everyone" ON profiles;
DROP POLICY
IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY
IF EXISTS "Rooms are viewable by everyone" ON rooms;
DROP POLICY
IF EXISTS "Only managers can modify rooms" ON rooms;
DROP POLICY
IF EXISTS "Users can view own bookings" ON bookings;
DROP POLICY
IF EXISTS "Staff can view all bookings" ON bookings;
DROP POLICY
IF EXISTS "Guests can create bookings" ON bookings;
EXCEPTION
    WHEN undefined_object THEN NULL;
END $$;

-- Create RLS Policies

-- Profiles policies
CREATE POLICY "Public profiles are viewable by everyone" ON profiles 
FOR
SELECT USING (true);

CREATE POLICY "Users can update own profile" ON profiles 
FOR
UPDATE USING (auth.uid()
= id);

CREATE POLICY "Users can insert own profile" ON profiles 
FOR
INSERT WITH CHECK (auth.uid() =
id);

-- Rooms policies
CREATE POLICY "Rooms are viewable by everyone" ON rooms 
FOR
SELECT USING (true);

CREATE POLICY "Only managers can modify rooms" ON rooms 
FOR ALL USING
(
    EXISTS
(SELECT 1
FROM profiles
WHERE id = auth.uid() AND role = 'manager')
);

-- Bookings policies
CREATE POLICY "Users can view own bookings" ON bookings 
FOR
SELECT USING (auth.uid() = user_id);

CREATE POLICY "Staff can view all bookings" ON bookings 
FOR
SELECT USING (
    EXISTS (SELECT 1
    FROM profiles
    WHERE id = auth.uid() AND role IN ('front_desk', 'manager', 'billing'))
);

CREATE POLICY "Guests can create bookings" ON bookings 
FOR
INSERT WITH CHECK (auth.uid() =
user_id);

CREATE POLICY "Staff can modify bookings" ON bookings 
FOR ALL USING
(
    EXISTS
(SELECT 1
FROM profiles
WHERE id = auth.uid() AND role IN ('front_desk', 'manager', 'billing'))
);

-- Tasks policies
CREATE POLICY "Staff can view tasks" ON tasks 
FOR
SELECT USING (
    EXISTS (SELECT 1
    FROM profiles
    WHERE id = auth.uid() AND role IN ('front_desk', 'housekeeping', 'maintenance', 'manager'))
);

CREATE POLICY "Staff can modify tasks" ON tasks 
FOR ALL USING
(
    EXISTS
(SELECT 1
FROM profiles
WHERE id = auth.uid() AND role IN ('front_desk', 'housekeeping', 'maintenance', 'manager'))
);

-- Invoices policies
CREATE POLICY "Users can view own invoices" ON invoices 
FOR
SELECT USING (
    EXISTS (SELECT 1
    FROM bookings
    WHERE bookings.id = invoices.booking_id AND bookings.user_id = auth.uid())
);

CREATE POLICY "Billing staff can manage invoices" ON invoices 
FOR ALL USING
(
    EXISTS
(SELECT 1
FROM profiles
WHERE id = auth.uid() AND role IN ('billing', 'manager'))
);

-- Vendors policies
CREATE POLICY "Vendors are viewable by staff" ON vendors 
FOR
SELECT USING (
    EXISTS (SELECT 1
    FROM profiles
    WHERE id = auth.uid() AND role IN ('front_desk', 'manager', 'billing'))
);

CREATE POLICY "Managers can manage vendors" ON vendors 
FOR ALL USING
(
    EXISTS
(SELECT 1
FROM profiles
WHERE id = auth.uid() AND role = 'manager')
);

-- Service Requests policies
CREATE POLICY "Staff can manage service requests" ON service_requests 
FOR ALL USING
(
    EXISTS
(SELECT 1
FROM profiles
WHERE id = auth.uid() AND role IN ('front_desk', 'housekeeping', 'maintenance', 'manager'))
);

-- Reviews policies
CREATE POLICY "Reviews are viewable by everyone" ON reviews 
FOR
SELECT USING (true);

CREATE POLICY "Anyone can insert reviews" ON reviews 
FOR
INSERT WITH CHECK
    (true)
;

-- Insert sample data (only if tables are empty)
DO $$
BEGIN
    -- Insert sample rooms if none exist
    IF NOT EXISTS (SELECT 1
    FROM rooms LIMIT 1) THEN
    INSERT INTO rooms
        (room_number, room_type, status, rate_per_night)
    VALUES
        ('101', 'single', 'vacant', 150.00),
        ('102', 'double', 'vacant', 200.00),
        ('103', 'suite', 'occupied', 350.00),
        ('104', 'deluxe', 'vacant', 500.00),
        ('201', 'single', 'cleaning', 150.00),
        ('202', 'double', 'maintenance', 200.00),
        ('203', 'suite', 'vacant', 350.00),
        ('204', 'deluxe', 'occupied', 500.00),
        ('301', 'single', 'vacant', 150.00),
        ('302', 'double', 'vacant', 200.00);
END
IF;

    -- Insert sample vendors if none exist
    IF NOT EXISTS (SELECT 1
FROM vendors LIMIT 1) THEN
INSERT INTO vendors
    (company_name, service_type, contact_email, contact_phone, service_rate, approval_status)
VALUES
    ('ABC Laundry Services', 'laundry', 'contact@abclaundry.com', '+1234567890', 50.00, 'approved'),
    ('XYZ Catering', 'catering', 'info@xyzcatering.com', '+1234567891', 200.00, 'approved'),
    ('Quick Transport', 'transport', 'book@quicktransport.com', '+1234567892', 75.00, 'pending'),
    ('City Maintenance Co.', 'maintenance', 'service@citymaintenance.com', '+1234567893', 100.00, 'approved'),
    ('Entertainment Plus', 'entertainment', 'events@entertainmentplus.com', '+1234567894', 150.00, 'approved');
END
IF;

    -- Insert sample reviews if none exist
    IF NOT EXISTS (SELECT 1
FROM reviews LIMIT 1) THEN
INSERT INTO reviews
    (guest_name, room_number, rating, review_text)
VALUES
    ('John Smith', '101', 5, 'Excellent stay! Very clean and comfortable.'),
    ('Sarah Johnson', '203', 4, 'Great service, but the room was a bit noisy.'),
    ('Mike Brown', '104', 5, 'Absolutely wonderful experience! Will definitely return.'),
    ('Emily Davis', '102', 3, 'Good value for money, but breakfast could be better.');
END
IF;
END $$;

-- Create indexes for better performance
CREATE INDEX
IF NOT EXISTS idx_profiles_email ON profiles
(email);
CREATE INDEX
IF NOT EXISTS idx_profiles_role ON profiles
(role);
CREATE INDEX
IF NOT EXISTS idx_rooms_status ON rooms
(status);
CREATE INDEX
IF NOT EXISTS idx_rooms_type ON rooms
(room_type);
CREATE INDEX
IF NOT EXISTS idx_bookings_user_id ON bookings
(user_id);
CREATE INDEX
IF NOT EXISTS idx_bookings_status ON bookings
(status);
CREATE INDEX
IF NOT EXISTS idx_bookings_dates ON bookings
(check_in, check_out);
CREATE INDEX
IF NOT EXISTS idx_tasks_assigned_to ON tasks
(assigned_to);
CREATE INDEX
IF NOT EXISTS idx_tasks_status ON tasks
(status);
CREATE INDEX
IF NOT EXISTS idx_invoices_status ON invoices
(status);
CREATE INDEX
IF NOT EXISTS idx_vendors_approval_status ON vendors
(approval_status);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column
()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW
();
RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_profiles_updated_at BEFORE
UPDATE ON profiles
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column
();

CREATE TRIGGER update_rooms_updated_at BEFORE
UPDATE ON rooms
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column
();

CREATE TRIGGER update_tasks_updated_at BEFORE
UPDATE ON tasks
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column
();

-- Create function to handle room status updates
CREATE OR REPLACE FUNCTION update_room_status_on_booking
()
RETURNS TRIGGER AS $$
BEGIN
    -- When booking is confirmed or checked in, update room status to occupied
    IF NEW.status IN ('confirmed', 'checked_in') AND OLD.status NOT IN ('confirmed', 'checked_in') THEN
    UPDATE rooms SET status = 'occupied', updated_at = NOW() 
        WHERE room_number = NEW.room_number;
    -- When booking is checked out or cancelled, update room status to cleaning
    ELSIF NEW.status IN
    ('checked_out', 'cancelled') AND OLD.status NOT IN
    ('checked_out', 'cancelled') THEN
    UPDATE rooms SET status = 'cleaning', updated_at = NOW() 
        WHERE room_number = NEW.room_number;
END
IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply booking trigger
CREATE TRIGGER update_room_status_on_booking_change 
    AFTER
UPDATE ON bookings
    FOR EACH ROW
EXECUTE FUNCTION update_room_status_on_booking
();

-- Display success message
DO $$
BEGIN
    RAISE NOTICE 'Grand Stay Hotel database setup completed successfully!';
    RAISE NOTICE 'Tables created: profiles, rooms, bookings, tasks, invoices, vendors, service_requests, reviews';
    RAISE NOTICE 'RLS policies applied for all tables';
    RAISE NOTICE 'Sample data inserted for rooms, vendors, and reviews';
    RAISE NOTICE 'Indexes and triggers created for optimal performance';
END $$;