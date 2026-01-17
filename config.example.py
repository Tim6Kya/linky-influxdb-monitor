"""
Linky Smart Meter Data Logger
==============================
This script reads data from a French Linky smart meter via TIC (Télé-Information Client)
interface and sends it to an InfluxDB time-series database for visualization with Grafana.

Hardware Setup:
- Raspberry Pi Zero WH connected to Linky meter TIC terminals
- Raspberry Pi 3 Model B+ running InfluxDB on local network

Author: Your Name
License: MIT
"""

import serial
import time
import csv
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# =============================================================================
# CONFIGURATION
# =============================================================================
# InfluxDB connection settings
# TODO: Replace with your actual values before running
URL = "http://192.168.1.XXX:8086"  # Your InfluxDB server IP
TOKEN = "YOUR_INFLUXDB_TOKEN_HERE"  # Your InfluxDB authentication token
ORG = "YOUR_ORGANIZATION"  # Your InfluxDB organization name
BUCKET = "YOUR_BUCKET_NAME"  # Your InfluxDB bucket name

# Serial port configuration for Linky TIC interface
# Standard mode: 1200 bauds, 7 data bits, even parity, 1 stop bit
SERIAL_PORT = '/dev/ttyAMA0'
SERIAL_BAUDRATE = 1200
SERIAL_PARITY = serial.PARITY_EVEN
SERIAL_STOPBITS = serial.STOPBITS_ONE
SERIAL_BYTESIZE = serial.SEVENBITS
SERIAL_TIMEOUT = 1

# Data collection interval in seconds
SAMPLING_INTERVAL = 10

# Local CSV backup file
CSV_FILENAME = 'conso_electrique.csv'

# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_influxdb():
    """Initialize connection to InfluxDB server"""
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    return client, write_api

def initialize_serial():
    """Initialize serial connection to Linky meter"""
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=SERIAL_BAUDRATE,
        parity=SERIAL_PARITY,
        stopbits=SERIAL_STOPBITS,
        bytesize=SERIAL_BYTESIZE,
        timeout=SERIAL_TIMEOUT
    )
    return ser

# =============================================================================
# DATA PROCESSING
# =============================================================================

def get_linky_data(serial_connection):
    """
    Read one complete frame from Linky meter
    
    Args:
        serial_connection: Active serial connection to the meter
        
    Returns:
        dict: Dictionary containing meter data labels and values
    """
    data = {}
    # Read up to 30 lines to capture a complete frame
    for _ in range(30):
        line = serial_connection.readline().decode('ascii', errors='replace').strip()
        parts = line.split()
        # Extract label and value from valid lines
        if len(parts) >= 2:
            data[parts[0]] = parts[1]
    return data

def send_to_influxdb(write_api, index_wh, power_va, timestamp):
    """
    Send meter data to InfluxDB
    
    Args:
        write_api: InfluxDB write API instance
        index_wh: Energy index in Watt-hours
        power_va: Apparent power in Volt-Amperes
        timestamp: Timestamp string for logging
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        point = Point("consommation") \
            .tag("device", "linky") \
            .field("index", index_wh) \
            .field("power", power_va)
        write_api.write(bucket=BUCKET, org=ORG, record=point)
        print(f"[{timestamp}] Data sent successfully: {power_va} VA")
        return True
    except Exception as e:
        print(f"[{timestamp}] InfluxDB connection error: {e}")
        return False

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution loop"""
    # Initialize connections
    print("🚀 Starting Linky monitor: CSV logging + InfluxDB transmission")
    
    client, write_api = initialize_influxdb()
    ser = initialize_serial()
    
    # Open CSV file for local data backup
    with open(CSV_FILENAME, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write CSV header if file is new
        if csv_file.tell() == 0:
            writer.writerow(['Date', 'Index_Wh', 'Power_VA'])
        
        try:
            while True:
                # Read data from Linky meter
                meter_data = get_linky_data(ser)
                
                # Process data if essential fields are present
                if 'BASE' in meter_data and 'PAPP' in meter_data:
                    # Extract and format values
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    index_wh = int(meter_data['BASE'])
                    power_va = int(meter_data['PAPP'])
                    
                    # Save to local CSV file
                    writer.writerow([timestamp, index_wh, power_va])
                    csv_file.flush()
                    
                    # Send to InfluxDB server
                    send_to_influxdb(write_api, index_wh, power_va, timestamp)
                
                # Wait before next measurement
                time.sleep(SAMPLING_INTERVAL)
                
        except KeyboardInterrupt:
            print("\nScript stopped by user")
        finally:
            # Clean up connections
            print("🔌 Closing connections...")
            client.close()
            ser.close()
            print("Shutdown complete")

if __name__ == "__main__":
    main()
