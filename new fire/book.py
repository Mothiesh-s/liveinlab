from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from twilio.rest import Client
import re
import keys
import os

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:1234@localhost:3306/course'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mothiesh370@gmail.com'
app.config['MAIL_PASSWORD'] = 'trpb rkfl frqz umlw'
app.config['MAIL_DEFAULT_SENDER'] = 'mothiesh370@gmail.com'

mail = Mail(app)


TWILIO_ACCOUNT_SID = 'AC6eab7000bf5aae09f88edb0ee6172520'
TWILIO_AUTH_TOKEN = 'c446cb1281f8b805e783228fa104d724'
TWILIO_PHONE_NUMBER = '+18148099949'
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

from twilio.rest import Client
account_sid=keys.account_sid
account_token=keys.auth_token
client=Client(account_sid,account_token)
message=client.messages.create(
    from_=keys.twilio_number,
    body="your parking slot booked successfully",
    to=keys.my_phone_number
)
print(message.sid)

def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_phone_number(phone):
    """Validate and format Indian phone number"""
    # Remove all non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # Check if the number is 10 digits
    if len(phone) == 10:
        return f'+91{phone}'
    
    # Check if the number is 12 digits and starts with 91
    if len(phone) == 12 and phone.startswith('91'):
        return f'+{phone}'
    
    return None

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)

# Parking Slot Model
class ParkingSlot(db.Model):
    __tablename__ = 'parking_slots'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), default="Available")
    booked_by = db.Column(db.String(100), nullable=True)

# Initialize Parking Slots
def initialize_slots():
    if ParkingSlot.query.count() == 0:
        for _ in range(15):
            db.session.add(ParkingSlot(status="Available"))
        db.session.commit()

# Create tables inside application context
with app.app_context():
    db.create_all()
    initialize_slots()

def send_sms(phone_number, message):
    """Send SMS using Twilio with enhanced error handling"""
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"SMS sent successfully to {phone_number}")
        return True
    except Exception as e:
        print(f"Error sending SMS to {phone_number}: {e}")
        return False

def send_booking_email(user_email, user_name, slot_id):
    """Send booking confirmation emails"""
    try:
        # User confirmation email
        user_msg = Message(
            "Parking Slot Booking Confirmation", 
            recipients=[user_email],
            body=f"Hello {user_name},\n\nYour parking slot (Slot ID: {slot_id}) has been successfully booked.\n\nThank you!"
        )
        mail.send(user_msg)

        # Admin notification email
        admin_msg = Message(
            "New Parking Slot Booking", 
            recipients=["admin@example.com"],
            body=f"A parking slot (Slot ID: {slot_id}) has been booked by {user_name} ({user_email})."
        )
        mail.send(admin_msg)
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

def send_unbooking_email(user_email, slot_id):
    """Send unbooking confirmation emails"""
    try:
        # User confirmation email
        user_msg = Message(
            "Parking Slot Unbooking Confirmation", 
            recipients=[user_email],
            body=f"Hello,\n\nYour parking slot (Slot ID: {slot_id}) has been successfully unbooked.\n\nThank you!"
        )
        mail.send(user_msg)

        # Admin notification email
        admin_msg = Message(
            "Parking Slot Unbooking", 
            recipients=["admin@example.com"],
            body=f"A parking slot (Slot ID: {slot_id}) has been unbooked by the user ({user_email})."
        )
        mail.send(admin_msg)
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

@app.route('/')
def home():
    available_slots = ParkingSlot.query.filter_by(status="Available").count()
    return render_template('register.html', available_slots=available_slots)

@app.route('/get_available_slots', methods=['GET'])
def get_available_slots():
    available_slots = ParkingSlot.query.filter_by(status="Available").count()
    return jsonify({"available_slots": available_slots})

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    
    # Validate input
    if not data.get('name') or not data.get('email') or not data.get('phone') or not data.get('vehicle_type'):
        return jsonify({"message": "All fields are required!"}), 400
    
    # Validate email
    if not validate_email(data['email']):
        return jsonify({"message": "Invalid email format!"}), 400
    
    # Validate and format phone number
    formatted_phone = validate_phone_number(data['phone'])
    if not formatted_phone:
        return jsonify({"message": "Invalid phone number! Please enter a 10-digit Indian mobile number."}), 400
    
    # Check for existing user
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"message": "Email already registered!"}), 400

    # Create new user
    new_user = User(
        name=data['name'],
        email=data['email'],
        phone=formatted_phone,
        vehicle_type=data['vehicle_type']
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Send welcome SMS
        sms_sent = send_sms(formatted_phone, f"Welcome {data['name']}! You have successfully registered for Parking Slot Booking.")
        
        return jsonify({
            "message": "User registered successfully!",
            "sms_sent": sms_sent
        })
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({"message": "Registration failed. Please try again."}), 500

@app.route('/book_slot', methods=['POST'])
def book_slot():
    data = request.form
    
    # Validate email
    if not validate_email(data.get('email', '')):
        return jsonify({"message": "Invalid email format!"}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"message": "User not found! Please register first."}), 400

    # Find available slot
    slot = ParkingSlot.query.filter_by(status="Available").first()
    if not slot:
        return jsonify({"message": "No available slots!"}), 400

    try:
        # Book the slot
        slot.status = "Booked"
        slot.booked_by = user.email
        db.session.commit()

        # Send notifications
        email_sent = send_booking_email(user.email, user.name, slot.id)
        sms_sent = send_sms(user.phone, f"Hello {user.name}, your parking slot (Slot ID: {slot.id}) has been booked successfully.")

        return jsonify({
            "message": "Slot booked successfully!",
            "email_sent": email_sent,
            "sms_sent": sms_sent
        })
    except Exception as e:
        db.session.rollback()
        print(f"Booking error: {e}")
        return jsonify({"message": "Booking failed. Please try again."}), 500

@app.route('/unbook_slot', methods=['POST'])
def unbook_slot():
    data = request.form
    
    # Validate email
    if not validate_email(data.get('email', '')):
        return jsonify({"message": "Invalid email format!"}), 400
    
    # Find booked slot
    slot = ParkingSlot.query.filter_by(booked_by=data['email']).first()
    if not slot:
        return jsonify({"message": "No booked slot found for this user!"}), 400

    # Find user
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"message": "User not found!"}), 400

    try:
        # Unbook the slot
        slot.status = "Available"
        slot.booked_by = None
        db.session.commit()

        # Send notifications
        email_sent = send_unbooking_email(user.email, slot.id)
        sms_sent = send_sms(user.phone, f"Hello {user.name}, your parking slot (Slot ID: {slot.id}) has been unbooked successfully.")

        return jsonify({
            "message": "Slot unbooked successfully!",
            "email_sent": email_sent,
            "sms_sent": sms_sent
        })
    except Exception as e:
        db.session.rollback()
        print(f"Unbooking error: {e}")
        return jsonify({"message": "Unbooking failed. Please try again."}), 500

if __name__ == "__main__":
    app.run(debug=True)





