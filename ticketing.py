import sqlite3
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        severity_level TEXT NOT NULL,
                        affected_components TEXT NOT NULL,
                        steps_to_reproduce TEXT NOT NULL,
                        attachments TEXT,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT
                    )''')
    conn.commit()
    conn.close()

# Function to create a new ticket
def create_ticket(title, description, severity_level, affected_components, steps_to_reproduce, attachments=None):
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "open"
    cursor.execute('''INSERT INTO tickets (title, description, severity_level, affected_components, steps_to_reproduce, attachments, status, created_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (title, description, severity_level, affected_components, steps_to_reproduce, attachments, status, created_at))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id

# Function to get a ticket by ID
def get_ticket(ticket_id):
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets WHERE id=?', (ticket_id,))
    ticket = cursor.fetchone()
    conn.close()
    return ticket

# Function to update ticket status
def update_ticket_status(ticket_id, status):
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('UPDATE tickets SET status=?, updated_at=? WHERE id=?', (status, updated_at, ticket_id))
    conn.commit()
    conn.close()

# Function to get all tickets
def get_all_tickets():
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets')
    tickets = cursor.fetchall()
    conn.close()
    return tickets

# Initialize the database when the module is imported
init_db()
