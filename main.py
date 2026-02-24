from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import razorpay
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Keys provided by user
GOOGLE_MAPS_API_KEY = ""
RAZORPAY_KEY_ID = ""
RAZORPAY_KEY_SECRET = ""

# Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))



# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # change if needed
        password="",       # set your MySQL password
        database="parking_system"
    )

# Utility: Release expired bookings
def release_expired_slots():
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        UPDATE bookings SET status='expired'
        WHERE end_time < %s AND status IN ('reserved', 'active')
    """, (now,))
    conn.commit()
    cursor.close()
    conn.close()

# Utility: Get available slots for a lot
def get_available_slots(lot_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT slot_number FROM slot_status
        WHERE lot_id = %s AND slot_number NOT IN (
            SELECT slot_number FROM bookings
            WHERE lot_id = %s AND status IN ('reserved','active') AND end_time > NOW()
        )
    """, (lot_id, lot_id))
    slots = cursor.fetchall()
    cursor.close()
    conn.close()
    return slots


# Helpers
def current_user():
    
    return session.get("user")

def require_login(role=None):
    user = current_user()
    if not user:
        return False
    if role and user.get("role") != role:
        return False
    return True

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return render_template("home.html")

# Auth: Register/Login/Logout
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form["role"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,%s)",
                       (name, email, password, role))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/check_email", methods=["POST"])
def check_email():
    email = request.form["email"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"exists": bool(user)}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, role FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["user"] = user
            return redirect(url_for("owner_dashboard" if user["role"] == "owner" else "home"))
        return render_template("login.html", error="Invalid password", email=email)

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# Owner: dashboard (manage lots)
@app.route("/owner/dashboard", methods=["GET","POST"])
def owner_dashboard():
    if not require_login(role="owner"):
        return redirect(url_for("login"))

    owner_id = current_user()["id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        price = float(request.form["price"])
        slots = int(request.form["slots"])
        lat = request.form.get("latitude") or None
        lng = request.form.get("longitude") or None

        cursor.execute(
            "INSERT INTO parking_lots (owner_id,name,location,latitude,longitude,price,slots) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (owner_id, name, location, lat, lng, price, slots)
        )
        conn.commit()

        # Initialize slot_status rows
        cursor.execute("SELECT LAST_INSERT_ID() AS lot_id")
        lot_id = cursor.fetchone()["lot_id"]
        for s in range(1, slots+1):
            cursor.execute("INSERT INTO slot_status (lot_id, slot_number, status) VALUES (%s,%s,'available')", (lot_id, s))
        conn.commit()

    cursor.execute("SELECT * FROM parking_lots WHERE owner_id=%s", (owner_id,))
    lots = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("owner_dashboard.html", lots=lots)

# Owner: unified analytics
@app.route("/owner/dashboard/<int:owner_id>")
def owner_full_dashboard(owner_id):
    if not require_login(role="owner") or current_user()["id"] != owner_id:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, name, slots, price FROM parking_lots WHERE owner_id=%s", (owner_id,))
    lots = cursor.fetchall()
    occupancy_data = []
    total_revenue = 0

    for lot in lots:
        cursor.execute("SELECT COUNT(*) AS occupied FROM slot_status WHERE lot_id=%s AND status='occupied'", (lot["id"],))
        occupied = cursor.fetchone()["occupied"]

        cursor.execute("SELECT COUNT(*) AS reserved FROM slot_status WHERE lot_id=%s AND status='reserved'", (lot["id"],))
        reserved = cursor.fetchone()["reserved"]

        total_slots = lot["slots"]
        available = total_slots - (occupied + reserved)
        occupancy_rate = round(((occupied + reserved) / total_slots) * 100, 2) if total_slots > 0 else 0

        cursor.execute("SELECT COALESCE(SUM(amount),0) AS revenue FROM bookings WHERE lot_id=%s AND status='reserved'", (lot["id"],))
        revenue = cursor.fetchone()["revenue"] or 0
        total_revenue += revenue

        occupancy_data.append({
            "lot_name": lot["name"],
            "total_slots": total_slots,
            "occupied": occupied,
            "reserved": reserved,
            "available": available,
            "occupancy_rate": occupancy_rate,
            "revenue": revenue
        })

    cursor.execute("""
                SELECT DATE(start_time) AS day, COALESCE(SUM(amount),0) AS total
                FROM bookings b
                JOIN parking_lots l ON b.lot_id = l.id
                WHERE l.owner_id=%s AND b.status='reserved'
                GROUP BY day ORDER BY day ASC
            """, (owner_id,))
    trend = cursor.fetchall()

    commission = round(float(total_revenue) * 0.10, 2)
    net_revenue = round(float(total_revenue) - commission, 2)

    cursor.close()
    conn.close()

    return render_template("owner_full_dashboard.html",
                           occupancy_data=occupancy_data,
                           trend=trend,
                           total_revenue=total_revenue,
                           commission=commission,
                           net_revenue=net_revenue,
                           owner_id=owner_id)

# User: Find parking (Google Maps placeholder)
@app.route("/user/find_parking")
def find_parking():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, location, latitude, longitude, price, slots FROM parking_lots")
    lots = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("find_parking.html", google_api=GOOGLE_MAPS_API_KEY, lots=lots)

# Lot view: interactive grid with live updates and select
@app.route("/lot/<int:lot_id>")
def lot_view(lot_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id,name,price,slots FROM parking_lots WHERE id=%s", (lot_id,))
    lot = cursor.fetchone()
    cursor.close()
    conn.close()
    if not lot:
        return "Lot not found", 404
    return render_template("lot_view.html", lot=lot)

# API: slot statuses



@app.route("/api/lot/<int:lot_id>/slots")
def api_lot_slots(lot_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    now = datetime.now()

    # Get all slots
    cursor.execute("SELECT slot_number, status FROM slot_status WHERE lot_id=%s ORDER BY slot_number ASC", (lot_id,))
    slots = cursor.fetchall()

    for slot in slots:
        if slot["status"] == "reserved":
            cursor.execute("""
                SELECT end_time FROM bookings
                WHERE lot_id = %s AND slot_number = %s AND status = 'reserved'
                ORDER BY end_time DESC LIMIT 1
            """, (lot_id, slot["slot_number"]))
            booking = cursor.fetchone()

            if booking:
                # Convert MySQL DATETIME to Python datetime if needed
                end_time = booking["end_time"]
                if isinstance(end_time, str):
                    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

                # If booking expired, release slot + mark booking expired
                if end_time < now:
                    cursor.execute("""
                        UPDATE slot_status SET status = 'available'
                        WHERE lot_id = %s AND slot_number = %s
                    """, (lot_id, slot["slot_number"]))
                    cursor.execute("""
                        UPDATE bookings SET status = 'expired'
                        WHERE lot_id = %s AND slot_number = %s AND status = 'reserved' AND end_time < %s
                    """, (lot_id, slot["slot_number"], now))
                    slot["status"] = "available"

    conn.commit()

    # Re-fetch updated slots so frontend sees fresh data
    cursor.execute("SELECT slot_number, status FROM slot_status WHERE lot_id=%s ORDER BY slot_number ASC", (lot_id,))
    updated_slots = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(updated_slots)

# Booking: choose slot -> pay -> reserve
# Booking route
from decimal import Decimal
from datetime import datetime
from flask import render_template, request, redirect, url_for, session

@app.route("/book/<int:lot_id>/<int:slot_number>", methods=["GET", "POST"])
def book_slot(lot_id, slot_number):
    if not require_login(role="user"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, price FROM parking_lots WHERE id=%s", (lot_id,))
    lot = cursor.fetchone()
    cursor.execute("SELECT status FROM slot_status WHERE lot_id=%s AND slot_number=%s", (lot_id, slot_number))
    slot = cursor.fetchone()
    cursor.close()
    conn.close()

    if not lot or not slot:
        return "Invalid lot or slot", 404
    if slot["status"] != "available":
        return render_template("book.html", lot_id=lot_id, slot_number=slot_number, lot=lot, error="Slot not available")

    if request.method == "POST":
        vehicle = request.form.get("vehicle")
        start_str = request.form.get("start_time")
        end_str = request.form.get("end_time")

        try:
            start_time = datetime.fromisoformat(start_str)
            end_time = datetime.fromisoformat(end_str)
        except ValueError:
            return render_template("book.html", lot_id=lot_id, slot_number=slot_number, lot=lot, error="Invalid time format")

        if end_time <= start_time:
            return render_template("book.html", lot_id=lot_id, slot_number=slot_number, lot=lot, error="End time must be after start time")

        duration_hours = Decimal(str((end_time - start_time).total_seconds() / 3600))
        price_per_hour = Decimal(str(lot["price"]))
        amount_rupees = round(duration_hours * price_per_hour, 2)
        amount_paise = int(amount_rupees * 100)

        try:
            order = razorpay_client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1
            })
        except razorpay.errors.BadRequestError as e:
            return render_template("book.html", lot_id=lot_id, slot_number=slot_number, lot=lot, error=str(e))

        order["key"] = RAZORPAY_KEY_ID

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO temp_booking_context (razorpay_order_id, user_id, lot_id, slot_number, vehicle, start_time, end_time, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            order["id"],
            current_user()["id"],
            lot_id,
            slot_number,
            vehicle,
            start_time,
            end_time,
            float(amount_rupees)  # store as float if DB column is FLOAT/DECIMAL
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template("payment.html", payment=order, lot_id=lot_id, slot_number=slot_number, amount=amount_rupees, lot=lot)

    return render_template("book.html", lot_id=lot_id, slot_number=slot_number, lot=lot)# Payment confirmation webhook simulator (simple form post)



@app.route("/payment/confirm", methods=["POST"])
def payment_confirm():
    data = request.get_json()
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": data["order_id"],
            "razorpay_payment_id": data["payment_id"],
            "razorpay_signature": data["signature"]
        })

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Fetch temp context by order id
        cursor.execute(
            "SELECT * FROM temp_booking_context WHERE razorpay_order_id = %s",
            (data["order_id"],)
        )
        context = cursor.fetchone()
        print("TEMP CONTEXT:", context)  # DEBUG

        if not context:
            cursor.close()
            conn.close()
            return jsonify({"status": "context_missing"}), 404

        # 2. Insert into bookings
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings (
                user_id,
                lot_id,
                slot_number,
                vehicle,
                start_time,
                end_time,
                status,
                payment_id,
                amount,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'reserved', %s, %s, NOW())
        """, (
            context["user_id"],
            context["lot_id"],
            context["slot_number"],
            context["vehicle"],        # make sure column name in temp is `vehicle`
            context["start_time"],
            context["end_time"],
            data["payment_id"],
            context["amount"]
        ))

        # 3. Update slot status
        cursor.execute("""
            UPDATE slot_status
            SET status = 'occupied'
            WHERE lot_id = %s AND slot_number = %s
        """, (context["lot_id"], context["slot_number"]))

        # 4. Delete temp context
        cursor.execute(
            "DELETE FROM temp_booking_context WHERE razorpay_order_id = %s",
            (data["order_id"],)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"})

    except razorpay.errors.SignatureVerificationError:
        return jsonify({"status": "failure"}), 400

@app.route("/webhook", methods=["POST"])
def razorpay_webhook():
    import hmac
    import hashlib

    webhook_secret = "123456"  # Set this in Razorpay dashboard
    payload = request.data
    received_signature = request.headers.get('X-Razorpay-Signature')

    # Verify signature
    generated_signature = hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if hmac.compare_digest(received_signature, generated_signature):
        event = request.get_json()

        if event["event"] == "payment.captured":
            payment_id = event["payload"]["payment"]["entity"]["id"]
            order_id = event["payload"]["payment"]["entity"]["order_id"]

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch temp booking
            cursor.execute("SELECT * FROM temp_booking_context WHERE razorpay_order_id = %s", (order_id,))
            temp = cursor.fetchone()

            if temp:
                # Insert into bookings
                cursor.execute("""
                    INSERT INTO bookings (user_id, lot_id, slot_number, vehicle, start_time, end_time, amount, status, payment_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'reserved', %s)
                """, (
                    temp["user_id"], temp["lot_id"], temp["slot_number"], temp["vehicle"],
                    temp["start_time"], temp["end_time"], temp["amount"], payment_id
                ))

                # Update slot status to reserved
                cursor.execute("""
                    UPDATE slot_status
                    SET status = 'reserved'
                    WHERE lot_id = %s AND slot_number = %s
                """, (temp["lot_id"], temp["slot_number"]))

                # Delete temp record
                cursor.execute("DELETE FROM temp_booking_context WHERE razorpay_order_id = %s", (order_id,))

            conn.commit()
            cursor.close()
            conn.close()

        elif event["event"] == "payment.failed":
            payment_id = event["payload"]["payment"]["entity"]["id"]

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE bookings SET status='cancelled' WHERE payment_id=%s", (payment_id,))
            conn.commit()
            cursor.close()
            conn.close()

        return "Webhook received", 200
    else:
        return "Invalid signature", 400

# Booking history
@app.route("/history")
def history():
    if not require_login():
        return redirect(url_for("login"))
    user_id = current_user()["id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.id,pl.name AS lot_name, b.slot_number, b.start_time, b.end_time, b.status,b.amount
        FROM bookings b
        JOIN parking_lots pl ON b.lot_id = pl.id
        WHERE b.user_id = %s
        ORDER BY b.start_time DESC
    """, (user_id,))
    bookings = cursor.fetchall()

    print("DEBUG BOOKINGS:", bookings)
    cursor.close()
    conn.close()
    return render_template("history.html", bookings=bookings)

# Cancel booking
@app.route("/cancel/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if not require_login():
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT lot_id, slot_number, status FROM bookings WHERE id=%s", (booking_id,))
    booking = cursor.fetchone()

    if booking and booking["status"] == "reserved":
        cursor.execute("UPDATE bookings SET status='cancelled' WHERE id=%s", (booking_id,))
        cursor.execute("UPDATE slot_status SET status='available' WHERE lot_id=%s AND slot_number=%s",
                       (booking["lot_id"], booking["slot_number"]))
        conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for("history"))

# ------------------ MAIN ------------------
if __name__ == "__main__":

    app.run(debug=True)
