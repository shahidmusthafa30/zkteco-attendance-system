import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from attendance_system import ZKTecoAttendance
import pandas as pd

class AttendanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ZKTeco Attendance System")
        self.root.geometry("1300x600")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Device connection frame
        connection_frame = ttk.LabelFrame(main_frame, text="Device Connection", padding="5")
        connection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(connection_frame, text="IP Address:").grid(row=0, column=0, padx=5)
        self.ip_var = tk.StringVar(value="172.31.11.252")
        ttk.Entry(connection_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(connection_frame, text="Port:").grid(row=0, column=2, padx=5)
        self.port_var = tk.StringVar(value="4370")
        ttk.Entry(connection_frame, textvariable=self.port_var, width=6).grid(row=0, column=3, padx=5)
        
        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect_device)
        self.connect_button.grid(row=0, column=4, padx=5)
        
        # Date filter frame
        date_frame = ttk.LabelFrame(main_frame, text="Date Filter", padding="5")
        date_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=5)
        self.start_date = DateEntry(date_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.start_date.grid(row=0, column=1, padx=5)
        
        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, padx=5)
        self.end_date = DateEntry(date_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2)
        self.end_date.grid(row=0, column=3, padx=5)
        
        self.retrieve_button = ttk.Button(date_frame, text="Retrieve Records", 
                                        command=self.retrieve_records, state=tk.DISABLED)
        self.retrieve_button.grid(row=0, column=4, padx=5)
        
        self.export_button = ttk.Button(date_frame, text="Export to CSV", 
                                      command=self.export_records, state=tk.DISABLED)
        self.export_button.grid(row=0, column=5, padx=5)
        
        # Create Treeview with scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create Treeview
        columns = ('user_id', 'user_name', 'date', 'check_in', 'check_out', 'duration')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                yscrollcommand=y_scrollbar.set,
                                xscrollcommand=x_scrollbar.set)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading('user_id', text='User ID')
        self.tree.heading('user_name', text='Name')
        self.tree.heading('date', text='Date')
        self.tree.heading('check_in', text='Check In')
        self.tree.heading('check_out', text='Check Out')
        self.tree.heading('duration', text='Duration (hours)')
        
        self.tree.column('user_id', width=100)
        self.tree.column('user_name', width=150)
        self.tree.column('date', width=100)
        self.tree.column('check_in', width=150)
        self.tree.column('check_out', width=150)
        self.tree.column('duration', width=100)
        
        self.tree.pack(expand=True, fill=tk.BOTH)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Not connected")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Initialize attendance system
        self.attendance_system = None
        
    def connect_device(self):
        try:
            ip = self.ip_var.get()
            port = int(self.port_var.get())
            
            self.attendance_system = ZKTecoAttendance(ip, port=port)
            self.attendance_system.connect()
            
            if self.attendance_system.conn:
                self.status_var.set(f"Connected to {ip}")
                self.connect_button.config(state=tk.DISABLED)
                self.retrieve_button.config(state=tk.NORMAL)
            else:
                self.status_var.set("Connection failed")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.status_var.set("Connection failed")
    
    def retrieve_records(self):
        if not self.attendance_system or not self.attendance_system.conn:
            messagebox.showerror("Error", "Please connect to the device first")
            return
        
        try:
            # Clear existing records
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get date range
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            
            # Retrieve records
            records = self.attendance_system.get_attendance(start_date, end_date)
            
            if records is not None and not records.empty:
                # Insert records into treeview
                for _, row in records.iterrows():
                    # Format duration to 2 decimal places if not None
                    duration = f"{row['duration']:.2f}" if pd.notnull(row['duration']) else "N/A"
                    
                    self.tree.insert('', tk.END, values=(
                        row['user_id'],
                        row['user_name'],
                        row['date'].strftime('%Y-%m-%d'),
                        row['check_in'].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(row['check_in']) else "N/A",
                        row['check_out'].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(row['check_out']) else "N/A",
                        duration
                    ))
                
                self.status_var.set(f"Retrieved {len(records)} records")
                self.export_button.config(state=tk.NORMAL)
            else:
                self.status_var.set("No records found")
                self.export_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error retrieving records")
    
    def export_records(self):
        if not self.attendance_system or not self.attendance_system.conn:
            messagebox.showerror("Error", "Please connect to the device first")
            return
        
        try:
            # Get date range
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            
            # Retrieve and export records
            records = self.attendance_system.get_attendance(start_date, end_date)
            
            if records is not None and not records.empty:
                filename = f"attendance_records_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                records.to_csv(filename, index=False)
                self.status_var.set(f"Records exported to {filename}")
                messagebox.showinfo("Success", f"Records exported to {filename}")
            else:
                self.status_var.set("No records to export")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error exporting records")

def main():
    root = tk.Tk()
    app = AttendanceGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 