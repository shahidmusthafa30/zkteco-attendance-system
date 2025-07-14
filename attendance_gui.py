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
        
        # Load saved devices (move this to the very start of __init__)
        import json, os
        self.devices_file = "devices.json"
        self.saved_devices = []
        if os.path.exists(self.devices_file):
            with open(self.devices_file, "r") as f:
                try:
                    self.saved_devices = json.load(f)
                except Exception:
                    self.saved_devices = []

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Device connection frame
        connection_frame = ttk.LabelFrame(main_frame, text="Device Connection", padding="10 10 10 10")
        connection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10, ipadx=5, ipady=5)

        # Device info subframe for better grouping
        device_info_frame = ttk.Frame(connection_frame)
        device_info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Label(device_info_frame, text="IP Address:").grid(row=0, column=0, padx=5, pady=2)
        self.ip_var = tk.StringVar(value="172.31.11.252")
        ttk.Entry(device_info_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(device_info_frame, text="Port:").grid(row=0, column=2, padx=5, pady=2)
        self.port_var = tk.StringVar(value="4370")
        port_entry = ttk.Entry(device_info_frame, textvariable=self.port_var, width=6)
        port_entry.grid(row=0, column=3, padx=5, pady=2)
        port_entry.bind('<FocusOut>', lambda e: self.port_var.set(self.port_var.get() or '4370'))
        ttk.Label(device_info_frame, text="Device Name:").grid(row=0, column=4, padx=5, pady=2)
        self.device_name_var = tk.StringVar()
        ttk.Entry(device_info_frame, textvariable=self.device_name_var, width=15).grid(row=0, column=5, padx=5, pady=2)
        self.connect_button = ttk.Button(device_info_frame, text="Connect", command=self.connect_device)
        self.connect_button.grid(row=0, column=6, padx=5, pady=2)

        # Device management subframe
        device_mgmt_frame = ttk.Frame(connection_frame)
        device_mgmt_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Label(device_mgmt_frame, text="Select Device:").grid(row=0, column=0, padx=5, pady=2)
        self.selected_device_var = tk.StringVar()
        self.device_dropdown = ttk.Combobox(device_mgmt_frame, textvariable=self.selected_device_var, values=[d["name"] for d in self.saved_devices], state="readonly", width=18)
        self.device_dropdown.grid(row=0, column=1, padx=5, pady=2)
        self.device_dropdown.bind("<<ComboboxSelected>>", self.on_device_selected)
        self.edit_device_button = ttk.Button(device_mgmt_frame, text="Edit", command=self.edit_selected_device, width=6)
        self.edit_device_button.grid(row=0, column=2, padx=2, pady=2)
        self.delete_device_button = ttk.Button(device_mgmt_frame, text="Delete", command=self.delete_selected_device, width=6)
        self.delete_device_button.grid(row=0, column=3, padx=2, pady=2)

        # Date filter frame
        date_frame = ttk.LabelFrame(main_frame, text="Date Filter", padding="10 10 10 10")
        date_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10, ipadx=5, ipady=5)
        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=2)
        self.start_date = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.start_date.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, padx=5, pady=2)
        self.end_date = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date.grid(row=0, column=3, padx=5, pady=2)
        self.retrieve_button = ttk.Button(date_frame, text="Retrieve Records", command=self.retrieve_records, state=tk.DISABLED)
        self.retrieve_button.grid(row=0, column=4, padx=5, pady=2)
        self.export_button = ttk.Button(date_frame, text="Export to CSV", command=self.export_records, state=tk.DISABLED)
        self.export_button.grid(row=0, column=5, padx=5, pady=2)
        self.export_pdf_button = ttk.Button(date_frame, text="Export to PDF", command=self.export_records_pdf, state=tk.DISABLED)
        self.export_pdf_button.grid(row=0, column=6, padx=5, pady=2)

        # Status label above the table for feedback
        self.status_var = tk.StringVar()
        self.status_var.set("Not connected")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding="5 5 5 5")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # Create Treeview with scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create Treeview
        columns = ('user_id', 'user_name', 'date', 'check_in', 'check_out', 'duration', 'device_name')
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
        self.tree.heading('device_name', text='Device Name')
        
        self.tree.column('user_id', width=100)
        self.tree.column('user_name', width=150)
        self.tree.column('date', width=100)
        self.tree.column('check_in', width=150)
        self.tree.column('check_out', width=150)
        self.tree.column('duration', width=100)
        self.tree.column('device_name', width=120)
        
        self.tree.pack(expand=True, fill=tk.BOTH)
        
        # Enable column resizing
        for col in columns:
            self.tree.heading(col, text=self.tree.heading(col)['text'], command=lambda _col=col: self.sort_by_column(_col, False))
            self.tree.column(col, width=self.tree.column(col)['width'], minwidth=50, stretch=True)
        
        # Initialize attendance system
        self.attendance_system = None
        
    def connect_device(self):
        import json
        import os
        try:
            ip = self.ip_var.get()
            port = int(self.port_var.get())
            device_name = self.device_name_var.get().strip() or f"Device_{ip}"
            self.current_device_name = device_name
            self.attendance_system = ZKTecoAttendance(ip, port=port)
            self.attendance_system.connect()
            if self.attendance_system.conn:
                # Save device info
                device_info = {"name": device_name, "ip": ip, "port": port}
                devices_file = "devices.json"
                devices = []
                if os.path.exists(devices_file):
                    with open(devices_file, "r") as f:
                        try:
                            devices = json.load(f)
                        except Exception:
                            devices = []
                # Avoid duplicates
                if not any(d["ip"] == ip and d["port"] == port for d in devices):
                    devices.append(device_info)
                    with open(devices_file, "w") as f:
                        json.dump(devices, f, indent=2)
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
            for item in self.tree.get_children():
                self.tree.delete(item)
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            records = self.attendance_system.get_attendance(start_date, end_date)
            if records is not None and not records.empty:
                # Add device name column
                records['device_name'] = getattr(self, 'current_device_name', 'Unknown')
                for _, row in records.iterrows():
                    duration = f"{row['duration']:.2f}" if pd.notnull(row['duration']) else "N/A"
                    self.tree.insert('', tk.END, values=(
                        row['user_id'],
                        row['user_name'],
                        row['date'].strftime('%Y-%m-%d'),
                        row['check_in'].strftime('%H:%M:%S') if pd.notnull(row['check_in']) else "N/A",
                        row['check_out'].strftime('%H:%M:%S') if pd.notnull(row['check_out']) else "N/A",
                        duration,
                        row['device_name']
                    ))
                self.status_var.set(f"Retrieved {len(records)} records")
                self.export_button.config(state=tk.NORMAL)
                self.export_pdf_button.config(state=tk.NORMAL)
            else:
                self.status_var.set("No records found")
                self.export_button.config(state=tk.DISABLED)
                self.export_pdf_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error retrieving records")
    
    def export_records(self):
        if not self.attendance_system or not self.attendance_system.conn:
            messagebox.showerror("Error", "Please connect to the device first")
            return
        try:
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            records = self.attendance_system.get_attendance(start_date, end_date)
            if records is not None and not records.empty:
                records['device_name'] = getattr(self, 'current_device_name', 'Unknown')
                filename = f"attendance_records_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                records.to_csv(filename, index=False)
                self.status_var.set(f"Records exported to {filename}")
                messagebox.showinfo("Success", f"Records exported to {filename}")
            else:
                self.status_var.set("No records to export")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error exporting records")

    def export_records_pdf(self):
        import os
        from tkinter import filedialog
        from fpdf import FPDF
        if not self.attendance_system or not self.attendance_system.conn:
            messagebox.showerror("Error", "Please connect to the device first")
            return
        try:
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            records = self.attendance_system.get_attendance(start_date, end_date)
            if records is not None and not records.empty:
                records['device_name'] = getattr(self, 'current_device_name', 'Unknown')
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    title="Save PDF as"
                )
                if not filename:
                    return
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                pdf.cell(0, 10, f"Attendance Records: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", ln=True, align='C')
                pdf.ln(5)
                col_widths = [20, 35, 25, 25, 25, 30, 30]
                headers = ['User ID', 'Name', 'Date', 'Check In', 'Check Out', 'Duration (hours)', 'Device Name']
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 8, header, border=1, align='C')
                pdf.ln()
                for _, row in records.iterrows():
                    duration = f"{row['duration']:.2f}" if pd.notnull(row['duration']) else "N/A"
                    pdf.cell(col_widths[0], 8, str(row['user_id']), border=1)
                    pdf.cell(col_widths[1], 8, str(row['user_name']), border=1)
                    pdf.cell(col_widths[2], 8, row['date'].strftime('%Y-%m-%d'), border=1)
                    pdf.cell(col_widths[3], 8, row['check_in'].strftime('%H:%M:%S') if pd.notnull(row['check_in']) else "N/A", border=1)
                    pdf.cell(col_widths[4], 8, row['check_out'].strftime('%H:%M:%S') if pd.notnull(row['check_out']) else "N/A", border=1)
                    pdf.cell(col_widths[5], 8, duration, border=1)
                    pdf.cell(col_widths[6], 8, row['device_name'], border=1)
                    pdf.ln()
                pdf.output(filename)
                self.status_var.set(f"Records exported to {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Records exported to {filename}")
            else:
                self.status_var.set("No records to export")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error exporting records to PDF")

    def refresh_device_dropdown(self):
        # Reload devices and update dropdown
        import json, os
        self.saved_devices = []
        if os.path.exists(self.devices_file):
            with open(self.devices_file, "r") as f:
                try:
                    self.saved_devices = json.load(f)
                except Exception:
                    self.saved_devices = []
        device_names = [d["name"] for d in self.saved_devices]
        self.device_dropdown['values'] = device_names
        self.selected_device_var.set("")

    def edit_selected_device(self):
        import json
        selected_name = self.selected_device_var.get()
        if not selected_name:
            messagebox.showwarning("No Selection", "Please select a device to edit.")
            return
        for d in self.saved_devices:
            if d["name"] == selected_name:
                # Update with current field values
                d["ip"] = self.ip_var.get()
                d["port"] = int(self.port_var.get())
                d["name"] = self.device_name_var.get().strip() or f"Device_{d['ip']}"
                break
        with open(self.devices_file, "w") as f:
            json.dump(self.saved_devices, f, indent=2)
        self.refresh_device_dropdown()
        messagebox.showinfo("Device Edited", "Device information updated.")

    def delete_selected_device(self):
        import json
        selected_name = self.selected_device_var.get()
        if not selected_name:
            messagebox.showwarning("No Selection", "Please select a device to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete device '{selected_name}'?"):
            return
        self.saved_devices = [d for d in self.saved_devices if d["name"] != selected_name]
        with open(self.devices_file, "w") as f:
            json.dump(self.saved_devices, f, indent=2)
        self.refresh_device_dropdown()
        # Clear fields if deleted device was selected
        if self.device_name_var.get() == selected_name:
            self.ip_var.set("")
            self.port_var.set("")
            self.device_name_var.set("")
        messagebox.showinfo("Device Deleted", f"Device '{selected_name}' deleted.")

    def on_device_selected(self, event=None):
        selected_name = self.selected_device_var.get()
        for d in self.saved_devices:
            if d["name"] == selected_name:
                self.ip_var.set(d["ip"])
                self.port_var.set(str(d["port"]))
                self.device_name_var.set(d["name"])
                break

    def sort_by_column(self, col, reverse):
        # Get all items and sort them
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0]) if col == 'duration' else t[0], reverse=reverse)
        except Exception:
            l.sort(key=lambda t: t[0], reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        # Reverse sort next time
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

def main():
    root = tk.Tk()
    app = AttendanceGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 