from flask import Flask, Response, jsonify, render_template, request
from ultralytics import YOLO
import cv2
from datetime import datetime, timedelta

app = Flask(__name__)

# Parking system class
class ParkingSystem:
    def __init__(self, total_slots):
        self.total_slots = total_slots
        self.available_slots = total_slots
        self.booked_slots = []

    def book_slot(self, name, hours):
        if self.available_slots > 0:
            booking_time = datetime.now()
            end_time = booking_time + timedelta(hours=hours)
            self.booked_slots.append({'name': name, 'booking_time': booking_time, 'end_time': end_time})
            self.available_slots -= 1
            return True, booking_time, end_time
        return False, None, None

    def unbook_slot(self, name):
        for booking in self.booked_slots:
            if booking['name'] == name:
                self.booked_slots.remove(booking)
                self.available_slots += 1
                return True
        return False

    def free_slot(self):
        self.booked_slots = []
        self.available_slots = self.total_slots

# Initialize the parking system
parking_system = ParkingSystem(total_slots=12)

model = YOLO('yolov8n.pt')
vehicle_classes = [2, 3, 5, 7]
video_path = "parking1.mp4"
camera = cv2.VideoCapture(video_path)


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        results = model(frame, verbose=False)[0]
        occupied_slots = 0
        for detection in results.boxes.data.tolist():
            x1, y1, x2, y2, confidence, class_id = detection
            if confidence > 0.3 and int(class_id) in vehicle_classes:
                occupied_slots += 1
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                label = f"{results.names[int(class_id)]} {confidence:.2f}"
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        parking_system.available_slots = parking_system.total_slots - occupied_slots
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('render.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/book_slot', methods=['POST'])
def book_slot():
    data = request.get_json()
    name = data.get('name')
    hours = int(data.get('hours'))
    success, booking_time, end_time = parking_system.book_slot(name, hours)
    if success:
        return jsonify({'message': f"Slot booked successfully for {name} from {booking_time} to {end_time}"})
    return jsonify({'message': 'No available slots to book'})


@app.route('/unbook_slot', methods=['POST'])
def unbook_slot():
    data = request.get_json()
    name = data.get('name')
    success = parking_system.unbook_slot(name)
    if success:
        return jsonify({'message': f"Slot unbooked successfully for {name}"})
    return jsonify({'message': f"No booking found for {name}"})


@app.route('/get_stats')
def get_stats():
    return jsonify({
        'available_slots': parking_system.available_slots,
        'booked_slots': parking_system.booked_slots,
        'booking_details': [{
            'name': booking['name'],
            'booking_time': booking['booking_time'].strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': booking['end_time'].strftime('%Y-%m-%d %H:%M:%S')
        } for booking in parking_system.booked_slots]
    })


if __name__ == '__main__':
    app.run(debug=True)

