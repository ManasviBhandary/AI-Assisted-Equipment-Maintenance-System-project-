import os
import csv
import sqlite3
from datetime import datetime

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
DB_PATH = os.path.join(BASE_DIR, 'factory_maintenance.db')

def create_star_schema(cursor):
    """Create Star Schema tables: Dimensions and Fact Tables."""
    # Dimension: Equipment
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_equipment (
            equipment_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            location_plant TEXT NOT NULL,
            location_sector TEXT NOT NULL
        )
    ''')

    # Dimension: Location
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_location (
            location_id TEXT PRIMARY KEY,
            plant TEXT NOT NULL,
            sector TEXT NOT NULL
        )
    ''')

    # Dimension: Technician
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_technician (
            technician_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Dimension: Date
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_date (
            date_id TEXT PRIMARY KEY,
            date_str TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,
            quarter INTEGER NOT NULL
        )
    ''')

    # Fact: Maintenance Events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_maintenance_events (
            event_id TEXT PRIMARY KEY,
            date_id TEXT NOT NULL,
            equipment_id TEXT NOT NULL,
            technician_id TEXT NOT NULL,
            location_id TEXT NOT NULL,
            downtime_hours REAL NOT NULL,
            defect_flag INTEGER NOT NULL,
            maintenance_cost_usd REAL NOT NULL,
            maintenance_type TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
            FOREIGN KEY (equipment_id) REFERENCES dim_equipment(equipment_id),
            FOREIGN KEY (technician_id) REFERENCES dim_technician(technician_id),
            FOREIGN KEY (location_id) REFERENCES dim_location(location_id)
        )
    ''')

    # Fact: Sensor Telemetry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_sensor_telemetry (
            telemetry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            date_id TEXT NOT NULL,
            equipment_id TEXT NOT NULL,
            temperature_c REAL NOT NULL,
            vibration_mm_s REAL NOT NULL,
            pressure_bar REAL NOT NULL,
            runtime_hours INTEGER NOT NULL,
            defect_flag INTEGER NOT NULL,
            FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
            FOREIGN KEY (equipment_id) REFERENCES dim_equipment(equipment_id)
        )
    ''')

def run_etl():
    """Run extraction, cleaning, transformation and loading pipeline."""
    print("=" * 60)
    print("STARTING ETL PIPELINE - SMART FACTORY MAINTENANCE SYSTEM")
    print("=" * 60)

    sensor_csv = os.path.join(DATA_RAW_DIR, 'sensor_logs.csv')
    maintenance_csv = os.path.join(DATA_RAW_DIR, 'maintenance_logs.csv')

    if not os.path.exists(sensor_csv) or not os.path.exists(maintenance_csv):
        raise FileNotFoundError("Raw CSV files missing in data/raw directory.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_star_schema(cursor)

    # Dictionaries to track dimension records
    locations = {}
    equipment = {}
    technicians = {}
    dates = {}

    # Helper function to get or add date_id
    def get_or_add_date(date_str_raw):
        # Format date as YYYY-MM-DD
        dt = datetime.strptime(date_str_raw.split()[0], '%Y-%m-%d')
        date_str = dt.strftime('%Y-%m-%d')
        date_id = f"DATE-{date_str.replace('-', '')}"
        if date_id not in dates:
            quarter = (dt.month - 1) // 3 + 1
            dates[date_id] = (date_id, date_str, dt.year, dt.month, dt.day, quarter)
        return date_id

    # 1. Process Sensor Telemetry CSV
    print("[1/3] Extracting & Transforming Sensor Telemetry...")
    sensor_rows = []
    with open(sensor_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            eq_id = row['machine_id'].strip()
            plant = row['location_plant'].strip()
            sector = row['location_sector'].strip()
            loc_id = f"LOC-{plant.replace(' ', '')}-{sector.replace(' ', '')}"

            locations[loc_id] = (loc_id, plant, sector)
            equipment[eq_id] = (eq_id, row['machine_name'].strip(), row['machine_type'].strip(), plant, sector)

            date_id = get_or_add_date(row['timestamp'])
            sensor_rows.append((
                row['timestamp'].strip(),
                date_id,
                eq_id,
                float(row['temperature_c']),
                float(row['vibration_mm_s']),
                float(row['pressure_bar']),
                int(row['runtime_hours']),
                int(row['defect_flag'])
            ))

    # 2. Process Maintenance Logs CSV
    print("[2/3] Extracting & Transforming Maintenance Logs...")
    maintenance_rows = []
    with open(maintenance_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tech_id = row['technician_id'].strip()
            technicians[tech_id] = (tech_id, row['technician_name'].strip(), row['technician_role'].strip())

            eq_id = row['machine_id'].strip()
            # Lookup plant/sector for equipment
            plant = equipment[eq_id][3] if eq_id in equipment else "Plant Alpha"
            sector = equipment[eq_id][4] if eq_id in equipment else "Sector A"
            loc_id = f"LOC-{plant.replace(' ', '')}-{sector.replace(' ', '')}"

            date_id = get_or_add_date(row['event_date'])

            maintenance_rows.append((
                row['event_id'].strip(),
                date_id,
                eq_id,
                tech_id,
                loc_id,
                float(row['downtime_hours']),
                int(row['defect_flag']),
                float(row['maintenance_cost_usd']),
                row['maintenance_type'].strip(),
                row['description'].strip()
            ))

    # 3. Load Into SQLite Database
    print("[3/3] Loading Data into Star Schema Data Warehouse...")

    # Load Dimensions
    cursor.executemany('INSERT OR REPLACE INTO dim_location VALUES (?,?,?)', list(locations.values()))
    cursor.executemany('INSERT OR REPLACE INTO dim_equipment VALUES (?,?,?,?,?)', list(equipment.values()))
    cursor.executemany('INSERT OR REPLACE INTO dim_technician VALUES (?,?,?)', list(technicians.values()))
    cursor.executemany('INSERT OR REPLACE INTO dim_date VALUES (?,?,?,?,?,?)', list(dates.values()))

    # Clear and Load Facts
    cursor.execute('DELETE FROM fact_maintenance_events')
    cursor.execute('DELETE FROM fact_sensor_telemetry')

    cursor.executemany('''
        INSERT INTO fact_maintenance_events 
        (event_id, date_id, equipment_id, technician_id, location_id, downtime_hours, defect_flag, maintenance_cost_usd, maintenance_type, description)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    ''', maintenance_rows)

    cursor.executemany('''
        INSERT INTO fact_sensor_telemetry
        (timestamp, date_id, equipment_id, temperature_c, vibration_mm_s, pressure_bar, runtime_hours, defect_flag)
        VALUES (?,?,?,?,?,?,?,?)
    ''', sensor_rows)

    conn.commit()

    # Print ETL Summary Statistics
    print("\n" + "=" * 60)
    print("ETL PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Database Location: {DB_PATH}")
    print(f"Loaded {len(locations)} Location Records into dim_location")
    print(f"Loaded {len(equipment)} Equipment Records into dim_equipment")
    print(f"Loaded {len(technicians)} Technician Records into dim_technician")
    print(f"Loaded {len(dates)} Date Records into dim_date")
    print(f"Loaded {len(maintenance_rows)} Maintenance Events into fact_maintenance_events")
    print(f"Loaded {len(sensor_rows)} Telemetry Records into fact_sensor_telemetry")
    print("=" * 60)

    conn.close()

if __name__ == '__main__':
    run_etl()
