from zk import ZK, const
import pandas as pd
from dateutil import parser
from datetime import datetime, time

class ZKTecoAttendance:
    def __init__(self, ip_address, port=4370, timeout=5, password=0):
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.password = password
        self.zk = ZK(self.ip_address, port=self.port, timeout=self.timeout, password=self.password)
        self.conn = None
        self.users = {}  # Cache for user information

    def connect(self):
        try:
            self.conn = self.zk.connect()
            # Load user information
            self.load_users()
            print(f"Successfully connected to device at {self.ip_address}")
        except Exception as e:
            print(f"Error connecting to device: {str(e)}")
            self.conn = None

    def disconnect(self):
        if self.conn:
            self.conn.disconnect()
            print("Disconnected from device")
            self.conn = None
            self.users = {}

    def load_users(self):
        """Load all users from the device"""
        if not self.conn:
            return
        try:
            users = self.conn.get_users()
            self.users = {user.user_id: user.name for user in users}
            print(f"Loaded {len(self.users)} users from device")
        except Exception as e:
            print(f"Error loading users: {str(e)}")

    def get_attendance_status(self, punch):
        """Convert punch value to check-in/check-out status"""
        # According to ZKTeco documentation:
        # 0: Check In
        # 1: Check Out
        punch_map = {
            0: "Check In",
            1: "Check Out"
        }
        return punch_map.get(punch, f"Unknown Punch ({punch})")

    def get_attendance(self, start_date=None, end_date=None):
        if not self.conn:
            print("Not connected to device. Please connect first.")
            return None
        try:
            attendance = self.conn.get_attendance()
            if not attendance:
                print("No attendance records found")
                return None

            print(f"Retrieved {len(attendance)} attendance records")
            
            # Convert dates to datetime objects if they're not already
            if start_date and not isinstance(start_date, datetime):
                start_date = datetime.combine(start_date, time.min)
            if end_date and not isinstance(end_date, datetime):
                end_date = datetime.combine(end_date, time.max)

            # First, collect all records
            raw_records = []
            for att in attendance:
                dt = att.timestamp
                if start_date and end_date:
                    if not (start_date <= dt <= end_date):
                        continue
                user_name = self.users.get(att.user_id, "Unknown")
                raw_records.append({
                    'user_id': att.user_id,
                    'user_name': user_name,
                    'timestamp': dt,
                    'raw_status': att.status,
                    'punch': att.punch,
                    'status': self.get_attendance_status(att.punch)
                })

            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(raw_records)
            if df.empty:
                return None

            # Sort by user_id and timestamp
            df = df.sort_values(['user_id', 'timestamp'])

            # Group records by user and date
            grouped_records = []
            current_user = None
            current_date = None
            check_in = None
            check_out = None

            for _, row in df.iterrows():
                user_id = row['user_id']
                user_name = row['user_name']
                timestamp = row['timestamp']
                date = timestamp.date()
                punch = row['punch']

                # If new user or new date, save previous record and start new one
                if current_user != user_id or current_date != date:
                    if current_user is not None and check_in is not None:
                        grouped_records.append({
                            'user_id': current_user,
                            'user_name': current_user_name,
                            'date': current_date,
                            'check_in': check_in,
                            'check_out': check_out
                        })
                    current_user = user_id
                    current_user_name = user_name
                    current_date = date
                    check_in = None
                    check_out = None

                # Update check-in or check-out time
                if punch == 0:  # Check In
                    check_in = timestamp
                elif punch == 1:  # Check Out
                    check_out = timestamp

            # Add the last record
            if current_user is not None and check_in is not None:
                grouped_records.append({
                    'user_id': current_user,
                    'user_name': current_user_name,
                    'date': current_date,
                    'check_in': check_in,
                    'check_out': check_out
                })

            # Convert to DataFrame
            result_df = pd.DataFrame(grouped_records)
            
            # Calculate duration if both check-in and check-out are present
            if not result_df.empty:
                result_df['duration'] = result_df.apply(
                    lambda row: (row['check_out'] - row['check_in']).total_seconds() / 3600 
                    if pd.notnull(row['check_out']) else None, 
                    axis=1
                )

            print(f"\nGrouped into {len(result_df)} attendance records")
            if not result_df.empty:
                print("\nSample of grouped records:")
                print(result_df.head())
            return result_df

        except Exception as e:
            print(f"Error retrieving attendance records: {str(e)}")
            return None

def main():
    device_ip = "192.168.1.201"  # Replace with your device's IP address
    attendance_system = ZKTecoAttendance(device_ip)
    try:
        attendance_system.connect()
        if attendance_system.conn:
            attendance_records = attendance_system.get_attendance()
            if attendance_records is not None:
                print("\nAttendance Records:")
                print(attendance_records)
                attendance_records.to_csv('attendance_records.csv', index=False)
                print("\nRecords saved to 'attendance_records.csv'")
    finally:
        attendance_system.disconnect()

if __name__ == "__main__":
    main() 