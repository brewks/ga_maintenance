import sqlite3
import numpy as np
from datetime import datetime, timedelta

def generate_degrading_sensor_data(db_path, top_params, num_components=10, num_records=1000):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    base_time = datetime.now() - timedelta(hours=num_records)

    for comp_id in range(1, num_components + 1):
        tail_number = f"N{np.random.randint(10000, 99999)}"
        for i in range(num_records):
            timestamp = base_time + timedelta(days=i)
            for param in top_params:
                base_val = max((num_records - i) / num_records, 0)
                noise = np.random.normal(0, 0.05)
                value = max(base_val + noise, 0) * 100

                if param in ['oil_press', 'hyd_press', 'brake_press', 'manifold_press']:
                    unit = 'psi'
                elif param in ['cht', 'oil_temp']:
                    unit = '°C'
                elif param == 'rpm':
                    unit = 'rpm'
                elif param == 'bus_voltage':
                    unit = 'volts'
                elif param == 'alternator_current':
                    unit = 'amps'
                else:
                    unit = 'psi'  # safe default

                cursor.execute("""
                    INSERT INTO sensor_data (tail_number, component_id, parameter, value, unit, timestamp, sensor_health)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    tail_number, comp_id, param, value, unit,
                    timestamp.strftime('%Y-%m-%d %H:%M:%S'), 0
                ))
    conn.commit()
    conn.close()
    print(f"✅ Inserted synthetic sensor records successfully.")
