import sqlite3
import random
import time
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'factory_maintenance.db')

EQUIPMENT_LIST = [
    ('M-101', 60.0, 85.0, 1.0, 3.0, 4.0, 5.0), # (id, min_t, max_t, min_v, max_v, min_p, max_p)
    ('M-102', 65.0, 95.0, 1.2, 5.5, 3.5, 4.8),
    ('M-201', 50.0, 80.0, 1.5, 6.0, 2.5, 3.5),
    ('M-202', 55.0, 82.0, 2.0, 5.8, 2.4, 3.2),
    ('M-301', 40.0, 55.0, 0.8, 3.8, 3.5, 5.5),
]

def simulate_reading():
    if not os.path.exists(DB_PATH):
        print("Database does not exist yet. Run ETL pipeline first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_str = datetime.now().strftime('%Y-%m-%d')
    date_id = f"DATE-{date_str.replace('-', '')}"

    # Ensure date exists in dim_date
    dt = datetime.now()
    quarter = (dt.month - 1) // 3 + 1
    cursor.execute('''
        INSERT OR IGNORE INTO dim_date (date_id, date_str, year, month, day, quarter)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date_id, date_str, dt.year, dt.month, dt.day, quarter))

    inserted_count = 0
    for eq_id, min_t, max_t, min_v, max_v, min_p, max_p in EQUIPMENT_LIST:
        temp = round(random.uniform(min_t, max_t), 1)
        vib = round(random.uniform(min_v, max_v), 1)
        press = round(random.uniform(min_p, max_p), 1)
        runtime = random.randint(2000, 6500)
        defect = 1 if (temp > 85.0 or vib > 4.5) else 0

        cursor.execute('''
            INSERT INTO fact_sensor_telemetry
            (timestamp, date_id, equipment_id, temperature_c, vibration_mm_s, pressure_bar, runtime_hours, defect_flag)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (now_str, date_id, eq_id, temp, vib, press, runtime, defect))
        inserted_count += 1

    conn.commit()
    conn.close()
    print(f"[{now_str}] Inserted {inserted_count} new simulated sensor telemetry samples into SQLite.")

if __name__ == '__main__':
    print("Starting Live Telemetry Stream Simulator (Press Ctrl+C to stop)...")
    try:
        while True:
            simulate_reading()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
