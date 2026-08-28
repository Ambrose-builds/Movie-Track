import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Film, CheckCircle2 } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [showtimes, setShowtimes] = useState([]);
  const [selectedShowtime, setSelectedShowtime] = useState(null);
  const [seats, setSeats] = useState([]);
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [booking, setBooking] = useState(null);
  const [form, setForm] = useState({ name: '', phone: '', email: '' });

  useEffect(() => {
    axios.get(`${API_BASE}/api/showtimes`)
      .then(res => setShowtimes(res.data))
      .catch(err => console.error("Error loading showtimes:", err));
  }, []);

  const selectShowtime = (st) => {
    setSelectedShowtime(st);
    setSelectedSeats([]);
    setBooking(null);
    axios.get(`${API_BASE}/api/showtimes/${st.id}/seats`)
      .then(res => setSeats(res.data))
      .catch(err => console.error("Error loading seats:", err));
  };

  const toggleSeat = (id) => {
    setSelectedSeats(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  const handleBooking = (e) => {
    e.preventDefault();
    if (!selectedSeats.length) return alert('Please select at least one seat.');

    axios.post(`${API_BASE}/api/bookings`, {
      showtime_id: selectedShowtime.id,
      customer_name: form.name,
      customer_phone: form.phone,
      customer_email: form.email,
      seat_ids: selectedSeats
    })
    .then(res => {
      setBooking(res.data);
      selectShowtime(selectedShowtime);
    })
    .catch(err => alert("Booking failed: " + err.message));
  };

  return (
    <div style={{ fontFamily: 'sans-serif', backgroundColor: '#0f172a', color: '#f8fafc', minHeight: '100vh', padding: '2rem' }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem', borderBottom: '1px solid #334155', paddingBottom: '1rem' }}>
        <Film size={32} color="#38bdf8" />
        <h1 style={{ margin: 0, fontSize: '1.75rem' }}>MovieTrack Cinema</h1>
      </header>

      <main style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <section>
          <h2>Available Showtimes</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {showtimes.map(st => (
              <div
                key={st.id}
                onClick={() => selectShowtime(st)}
                style={{
                  padding: '1rem',
                  borderRadius: '8px',
                  backgroundColor: selectedShowtime?.id === st.id ? '#1e293b' : '#334155',
                  border: selectedShowtime?.id === st.id ? '2px solid #38bdf8' : '1px solid transparent',
                  cursor: 'pointer'
                }}
              >
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#38bdf8' }}>{st.title}</h3>
                <p style={{ margin: 0, fontSize: '0.9rem', color: '#94a3b8' }}>
                  {st.cinema_name} • {st.screen_name}
                </p>
                <p style={{ margin: '0.25rem 0 0 0', fontWeight: 'bold' }}>{st.start_time}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          {selectedShowtime ? (
            <div>
              <h2>Select Seats for {selectedShowtime.title}</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.5rem', marginBottom: '1.5rem' }}>
                {seats.map(seat => {
                  const isSelected = selectedSeats.includes(seat.id);
                  const isAvailable = seat.is_available;
                  return (
                    <button
                      key={seat.id}
                      disabled={!isAvailable}
                      onClick={() => toggleSeat(seat.id)}
                      style={{
                        padding: '0.75rem',
                        borderRadius: '6px',
                        border: 'none',
                        cursor: isAvailable ? 'pointer' : 'not-allowed',
                        backgroundColor: !isAvailable ? '#475569' : isSelected ? '#22c55e' : '#0284c7',
                        color: '#fff',
                        fontWeight: 'bold'
                      }}
                    >
                      {seat.row_label}{seat.seat_number}
                    </button>
                  );
                })}
              </div>

              {selectedSeats.length > 0 && !booking && (
                <form onSubmit={handleBooking} style={{ backgroundColor: '#1e293b', padding: '1rem', borderRadius: '8px' }}>
                  <h3>Confirm Booking ({selectedSeats.length} seat(s))</h3>
                  <input
                    type="text"
                    placeholder="Full Name"
                    required
                    style={{ width: '90%', padding: '0.5rem', marginBottom: '0.5rem' }}
                    onChange={e => setForm({ ...form, name: e.target.value })}
                  />
                  <input
                    type="text"
                    placeholder="Phone Number"
                    required
                    style={{ width: '90%', padding: '0.5rem', marginBottom: '0.5rem' }}
                    onChange={e => setForm({ ...form, phone: e.target.value })}
                  />
                  <input
                    type="email"
                    placeholder="Email Address"
                    required
                    style={{ width: '90%', padding: '0.5rem', marginBottom: '1rem' }}
                    onChange={e => setForm({ ...form, email: e.target.value })}
                  />
                  <button type="submit" style={{ padding: '0.75rem 1.5rem', backgroundColor: '#22c55e', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                    Book Tickets
                  </button>
                </form>
              )}

              {booking && (
                <div style={{ backgroundColor: '#064e3b', border: '1px solid #10b981', padding: '1rem', borderRadius: '8px', marginTop: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <CheckCircle2 color="#10b981" />
                    <h3 style={{ margin: 0, color: '#10b981' }}>Booking Confirmed!</h3>
                  </div>
                  <p>Confirmation Reference: <strong>{booking.booking_id}</strong></p>
                </div>
              )}
            </div>
          ) : (
            <p style={{ color: '#94a3b8' }}>Select a showtime from the left to pick your seats.</p>
          )}
        </section>
      </main>
    </div>
  );
}