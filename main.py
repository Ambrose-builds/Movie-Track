import sqlite3
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Movie Track API")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "movietrack.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def home():
    return {"status": "ok", "message": "Movie Track API is running"}

# 1. Fetch all movies
@app.get("/api/movies")
def get_movies():
    conn = get_db()
    cursor = conn.cursor()
    movies = cursor.execute("SELECT * FROM movies").fetchall()
    conn.close()
    return [dict(movie) for movie in movies]

# 2. Fetch all showtimes with cinema & movie details
@app.get("/api/showtimes")
def get_showtimes():
    conn = get_db()
    cursor = conn.cursor()
    query = """
    SELECT s.id, m.title, m.poster_url, c.name as cinema_name, sc.name as screen_name, s.start_time
    FROM showtimes s
    JOIN movies m ON s.movie_id = m.id
    JOIN screens sc ON s.screen_id = sc.id
    JOIN cinemas c ON sc.cinema_id = c.id
    """
    showtimes = cursor.execute(query).fetchall()
    conn.close()
    return [dict(st) for st in showtimes]

# 3. Fetch seats and calculated availability for a showtime
@app.get("/api/showtimes/{showtime_id}/seats")
def get_seats_for_showtime(showtime_id: int):
    conn = get_db()
    cursor = conn.cursor()

    st = cursor.execute("SELECT screen_id FROM showtimes WHERE id = ?", (showtime_id,)).fetchone()
    if not st:
        conn.close()
        raise HTTPException(status_code=404, detail="Showtime not found")

    screen_id = st["screen_id"]
    seats = cursor.execute("SELECT id, row_label, seat_number FROM seats WHERE screen_id = ?", (screen_id,)).fetchall()

    booked = cursor.execute("""
        SELECT seat_id FROM booking_seats bs
        JOIN bookings b ON bs.booking_id = b.id
        WHERE b.showtime_id = ? AND b.status = 'CONFIRMED'
    """, (showtime_id,)).fetchall()
    booked_ids = {b["seat_id"] for b in booked}

    seat_list = []
    for s in seats:
        seat_dict = dict(s)
        seat_dict["is_available"] = s["id"] not in booked_ids
        seat_list.append(seat_dict)

    conn.close()
    return seat_list

# 4. Create a booking
class BookingRequest(BaseModel):
    showtime_id: int
    customer_name: str
    customer_phone: str
    customer_email: str
    seat_ids: list[int]

@app.post("/api/bookings")
def create_booking(req: BookingRequest):
    conn = get_db()
    cursor = conn.cursor()

    booking_id = f"MT-{str(uuid.uuid4())[:8].upper()}"

    try:
        cursor.execute("""
            INSERT INTO bookings (id, showtime_id, customer_name, customer_phone, customer_email, status)
            VALUES (?, ?, ?, ?, ?, 'CONFIRMED')
        """, (booking_id, req.showtime_id, req.customer_name, req.customer_phone, req.customer_email))

        for seat_id in req.seat_ids:
            cursor.execute("INSERT INTO booking_seats (booking_id, seat_id) VALUES (?, ?)", (booking_id, seat_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

    conn.close()
    return {"booking_id": booking_id, "status": "CONFIRMED", "message": "Booking successful"}