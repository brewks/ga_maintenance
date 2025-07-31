import sqlite3
import numpy as np
from datetime import datetime, timedelta
import random

def generate_degrading_sensor_data(
    db_path, top_params, num_components=10, num_records=1000
):
    # Define thresholds for sensor health (below = unhealthy)
    thresholds = {
        'oil_press': 30,
        'hyd_press': 40,
        'brake_press': 50,
        'manifold_press': 25,
        'cht': 100,  # °C
        'oil_temp': 90,
        'rpm': 1000,
        'bus_voltage': 11,
        'alternator_current': 15
    }

    # Define sampling intervals per parameter (in seconds)
    sampling_intervals = {
        'oil_press': 60,
        'cht': 30,
        'rpm': 10,
        'bus_voltage': 60,
        'alternator_current': 30
    }

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    base_time = datetime.now()

    for comp_id in range(1, num_components + 1):
        tail_number = f"N{np.random.randint(10000, 99999)}"

        # Randomly choose if this component fails early (accelerated degradation)
        failure_point = random.randint(int(num_records * 0.5), num_records)

        for param in top_params:
            interval_sec = sampling_intervals.get(param, 60)  # default 60s
            time_offset = 0  # seconds from base_time

            for i in range(num_records):
                # Accelerated degradation after failure_point
                if i < failure_point:
                    base_val = max((num_records - i) / num_records, 0)
                else:
                    base_val = max((num_records - i) / num_records, 0) * 0.5  # more rapid drop

                noise = np.random.normal(0, 0.05)
                value = max(base_val + noise, 0) * 100

                # Determine unit
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
                    unit = 'psi'

                # Health classification based on thresholds
                threshold = thresholds.get(param, 20)  # fallback threshold
                sensor_health = 0 if value >= threshold else 1

                timestamp = base_time + timedelta(seconds=time_offset)
                time_offset += interval_sec

                # Insert into DB
                cursor.execute("""
                    INSERT INTO sensor_data (
                        tail_number, component_id, parameter,
                        value, unit, timestamp, sensor_health
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    tail_number, comp_id, param, value, unit,
                    timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    sensor_health
                ))

    conn.commit()
    conn.close()
    print(f"✅ Inserted synthetic sensor records with degradation, failures, and variable sampling rates.")
