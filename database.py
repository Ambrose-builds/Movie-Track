import sqlite3

DB_NAME = "movietrack.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Cinemas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cinemas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL
    );
    """)

    # Screens
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS screens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cinema_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY (cinema_id) REFERENCES cinemas (id)
    );
    """)

    # Seats (Belong to Screen, not Showtime)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        screen_id INTEGER NOT NULL,
        row_label TEXT NOT NULL,
        seat_number INTEGER NOT NULL,
        FOREIGN KEY (screen_id) REFERENCES screens (id)
    );
    """)

    # Movies
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL,
        poster_url TEXT NOT NULL
    );
    """)

    # Showtimes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS showtimes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER NOT NULL,
        screen_id INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        FOREIGN KEY (screen_id) REFERENCES screens (id)
    );
    """)

    # Seat Holds (Auto-expire concept)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seat_holds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        showtime_id INTEGER NOT NULL,
        seat_id INTEGER NOT NULL,
        session_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (showtime_id) REFERENCES showtimes (id),
        FOREIGN KEY (seat_id) REFERENCES seats (id)
    );
    """)

    # Bookings (Unguessable String ID)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id TEXT PRIMARY KEY,
        showtime_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'CONFIRMED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (showtime_id) REFERENCES showtimes (id)
    );
    """)

    # Booking Seats
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS booking_seats (
        booking_id TEXT NOT NULL,
        seat_id INTEGER NOT NULL,
        FOREIGN KEY (booking_id) REFERENCES bookings (id),
        FOREIGN KEY (seat_id) REFERENCES seats (id)
    );
    """)

    conn.commit()
    conn.close()

def seed_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM cinemas")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Seed Cinema & Screen
    cursor.execute("INSERT INTO cinemas (name, location) VALUES ('Century Cinemax', 'Sarit Centre, Westlands, Nairobi')")
    cinema_id = cursor.lastrowid

    cursor.execute("INSERT INTO screens (cinema_id, name) VALUES (?, 'Screen 1 (Max VIP)')", (cinema_id,))
    screen_id = cursor.lastrowid

    # Seed Seats (Rows A-C, Seats 1-6)
    for row in ['A', 'B', 'C']:
        for num in range(1, 7):
            cursor.execute("INSERT INTO seats (screen_id, row_label, seat_number) VALUES (?, ?, ?)", (screen_id, row, num))

    # Seed Movies
    cursor.execute("INSERT INTO movies (title, duration_minutes, poster_url) VALUES ('Deadpool & Wolverine', 128, 'https://images.unsplash.com/photo-1536440136628-849c177e76a1')")
    movie1_id = cursor.lastrowid

    cursor.execute("INSERT INTO movies (title, duration_minutes, poster_url) VALUES ('Dune: Part Two', 166, 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba')")
    movie2_id = cursor.lastrowid

    # Seed Showtimes
    cursor.execute("INSERT INTO showtimes (movie_id, screen_id, start_time) VALUES (?, ?, '2026-08-30T16:00:00+03:00')", (movie1_id, screen_id))
    cursor.execute("INSERT INTO showtimes (movie_id, screen_id, start_time) VALUES (?, ?, '2026-08-30T19:30:00+03:00')", (movie2_id, screen_id))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_data()
    print("Database tables created and seeded successfully!")