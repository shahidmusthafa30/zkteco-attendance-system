import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from attendance_system import ZKTecoAttendance
import pandas as pd
import json
import os

class AttendanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ZKTeco Attendance System")
        self.root.geometry("1300x600")
        
        # Load saved devices (move this to the very start of __init__)
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
        # Configure root grid to reserve last row for footer
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
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
        self.disconnect_button = ttk.Button(device_info_frame, text="Disconnect", command=self.disconnect_device, state=tk.DISABLED)
        self.disconnect_button.grid(row=0, column=7, padx=5, pady=2)

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
        self.export_button = ttk.Button(date_frame, text="Export to CSV", command=self.export_records, state=tk.DISABLED)
        self.export_button.grid(row=0, column=4, padx=5, pady=2)
        self.export_pdf_button = ttk.Button(date_frame, text="Export to PDF", command=self.export_records_pdf, state=tk.DISABLED)
        self.export_pdf_button.grid(row=0, column=5, padx=5, pady=2)
        self.show_raw_button = ttk.Button(date_frame, text="Get Attendance Logs", command=self.show_raw_logs, state=tk.DISABLED)
        self.show_raw_button.grid(row=0, column=6, padx=5, pady=2)

        # Add summary panel below date_frame, above table
        self.summary_frame = ttk.Frame(main_frame, padding="5 5 5 5")
        self.summary_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        self.checkin_var = tk.StringVar(value="Total Check-ins: 0")
        self.checkout_var = tk.StringVar(value="Total Check-outs: 0")
        self.unique_users_var = tk.StringVar(value="Unique Users: 0")
        ttk.Label(self.summary_frame, textvariable=self.checkin_var, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Label(self.summary_frame, textvariable=self.checkout_var, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Label(self.summary_frame, textvariable=self.unique_users_var, width=20).pack(side=tk.LEFT, padx=10)

        # Status label above the table for feedback
        self.status_var = tk.StringVar()
        self.status_var.set("Not connected")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding="5 5 5 5")
        # Move status label below the table for better visibility
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # Footer label (branding) as clickable link
        def open_github(event=None):
            import webbrowser
            webbrowser.open_new("https://github.com/shahidmusthafa30")
        self.footer_label = tk.Label(self.root, text="Developed by Shahid | github.com/shahidmusthafa30", anchor="center", font=("Arial", 9), fg="blue", cursor="hand2")
        self.footer_label.grid(row=1, column=0, sticky="ew", pady=(0, 2))
        self.footer_label.bind("<Button-1>", open_github)

        # Add menu bar with About dialog
        self._add_menu_bar()
        
        # Create Treeview with scrollbars
        tree_frame = ttk.Frame(main_frame)
        # Center the table and improve spacing
        tree_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), padx=30, pady=10)
        
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create Treeview
        columns = ('user_id', 'user_name', 'date', 'check_in', 'check_out', 'device_name')
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
        self.tree.heading('device_name', text='Device Name')
        
        self.tree.column('user_id', width=100)
        self.tree.column('user_name', width=150)
        self.tree.column('date', width=100)
        self.tree.column('check_in', width=150)
        self.tree.column('check_out', width=150)
        self.tree.column('device_name', width=120)
        
        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        # Bind double-click event to treeview for user details popup (after treeview is created)
        self.tree.bind('<Double-1>', self.on_row_double_click)
        
        # Enable column resizing
        for col in columns:
            self.tree.heading(col, text=self.tree.heading(col)['text'], command=lambda _col=col: self.sort_by_column(_col, False))
            self.tree.column(col, width=self.tree.column(col)['width'], minwidth=50, stretch=True)
        
        # Initialize attendance system
        self.attendance_system = None
        
    def connect_device(self):
        try:
            # If already connected, disconnect first
            if hasattr(self, 'attendance_system') and self.attendance_system and self.attendance_system.conn:
                self.attendance_system.disconnect()
                # Clear the table and summary
                for item in self.tree.get_children():
                    self.tree.delete(item)
                self.checkin_var.set("Total Check-ins: 0")
                self.checkout_var.set("Total Check-outs: 0")
                self.unique_users_var.set("Unique Users: 0")
                self.status_var.set("Not connected")
                self.connect_button.config(state=tk.NORMAL)
                self.disconnect_button.config(state=tk.DISABLED)
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
                self.disconnect_button.config(state=tk.NORMAL)
                self.show_raw_button.config(state=tk.NORMAL)
                self.export_button.config(state=tk.NORMAL)
                self.export_pdf_button.config(state=tk.NORMAL)
            else:
                self.status_var.set("Connection failed")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.status_var.set("Connection failed")

    def disconnect_device(self):
        if hasattr(self, 'attendance_system') and self.attendance_system and self.attendance_system.conn:
            self.attendance_system.disconnect()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.checkin_var.set("Total Check-ins: 0")
        self.checkout_var.set("Total Check-outs: 0")
        self.unique_users_var.set("Unique Users: 0")
        self.status_var.set("Disconnected")
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.show_raw_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)
        self.export_pdf_button.config(state=tk.DISABLED)
    
    def export_records(self):
        if not self.attendance_system or not self.attendance_system.conn:
            messagebox.showerror("Error", "Please connect to the device first")
            return
        try:
            import datetime
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            records = self.attendance_system.get_attendance(start_date, end_date)
            if records is not None and not records.empty:
                device_name = getattr(self, 'current_device_name', 'Unknown')
                safe_device = str(device_name).replace(' ', '_').replace('/', '_')
                records['device_name'] = device_name
                now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                default_filename = f"attendance_{safe_device}_{now}.csv"
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv")],
                    initialfile=default_filename
                )
                if filename:
                    records.to_csv(filename, index=False)
                    self.status_var.set(f"Records exported to {filename}")
                    messagebox.showinfo("Success", f"Records exported to {filename}")
            else:
                self.status_var.set("No records to export")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error exporting records")

    def export_records_pdf(self):
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("Missing Dependency", "Please install fpdf to export PDF.")
            return
        if not self.attendance_system or not self.attendance_system.conn:
            messagebox.showerror("Error", "Please connect to the device first")
            return
        try:
            import datetime
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            records = self.attendance_system.get_attendance(start_date, end_date)
            if records is not None and not records.empty:
                device_name = getattr(self, 'current_device_name', 'Unknown')
                safe_device = str(device_name).replace(' ', '_').replace('/', '_')
                records['device_name'] = device_name
                now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                default_filename = f"attendance_{safe_device}_{now}.pdf"
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=default_filename
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
                    duration = f"{row['duration']:.2f}" if 'duration' in row and pd.notnull(row['duration']) else "N/A"
                    pdf.cell(col_widths[0], 8, str(row['user_id']), border=1)
                    pdf.cell(col_widths[1], 8, str(row['user_name']), border=1)
                    pdf.cell(col_widths[2], 8, row['date'].strftime('%Y-%m-%d') if 'date' in row and pd.notnull(row['date']) else "N/A", border=1)
                    pdf.cell(col_widths[3], 8, row['check_in'].strftime('%H:%M:%S') if 'check_in' in row and pd.notnull(row['check_in']) else "N/A", border=1)
                    pdf.cell(col_widths[4], 8, row['check_out'].strftime('%H:%M:%S') if 'check_out' in row and pd.notnull(row['check_out']) else "N/A", border=1)
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

    def show_raw_logs(self):
        if not self.attendance_system or not self.attendance_system.conn:
            messagebox.showerror("Error", "Please connect to the device first")
            return
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            device_name = getattr(self, 'current_device_name', 'Unknown')
            records = self.attendance_system.get_raw_attendance(start_date, end_date, device_name=device_name)
            # Update summary panel
            if records is not None and not records.empty:
                total_checkins = (records['status'] == 'Check In').sum()
                total_checkouts = (records['status'] == 'Check Out').sum()
                unique_users = records['user_id'].nunique()
                self.checkin_var.set(f"Total Check-ins: {total_checkins}")
                self.checkout_var.set(f"Total Check-outs: {total_checkouts}")
                self.unique_users_var.set(f"Unique Users: {unique_users}")
                # Define tag styles for row colors
                self.tree.tag_configure('checkin', background='#d4f7d4')  # light green
                self.tree.tag_configure('checkout', background='#d4e6f7')  # light blue
                for _, row in records.iterrows():
                    if row['status'] == 'Check In':
                        check_in = row['timestamp'].strftime('%H:%M:%S')
                        check_out = ''
                        tag = 'checkin'
                    elif row['status'] == 'Check Out':
                        check_in = ''
                        check_out = row['timestamp'].strftime('%H:%M:%S')
                        tag = 'checkout'
                    else:
                        check_in = ''
                        check_out = ''
                        tag = ''
                    self.tree.insert('', tk.END, values=(
                        row['user_id'],
                        row['user_name'],
                        row['timestamp'].strftime('%Y-%m-%d'),
                        check_in,
                        check_out,
                        row['device_name']
                    ), tags=(tag,))
                self.status_var.set(f"Retrieved {len(records)} raw logs")
                self._last_raw_records = records  # Store for user details popup
            else:
                self.checkin_var.set("Total Check-ins: 0")
                self.checkout_var.set("Total Check-outs: 0")
                self.unique_users_var.set("Unique Users: 0")
                self.status_var.set("No raw logs found")
                self._last_raw_records = None
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error retrieving raw logs")

    def refresh_device_dropdown(self):
        # Reload devices and update dropdown
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

    def on_row_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        user_id = self.tree.item(item, 'values')[0]
        user_name = self.tree.item(item, 'values')[1]
        # Get all logs for this user in the current date range
        records = getattr(self, '_last_raw_records', None)
        if records is None or records.empty:
            return
        user_logs = records[records['user_id'] == user_id]
        if user_logs.empty:
            return
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Attendance Details for {user_name} ({user_id})")
        popup.geometry("700x400")
        # Summary
        total_checkins = (user_logs['status'] == 'Check In').sum()
        total_checkouts = (user_logs['status'] == 'Check Out').sum()
        summary = f"Check-ins: {total_checkins}    Check-outs: {total_checkouts}    Total logs: {len(user_logs)}"
        ttk.Label(popup, text=summary, font=("Arial", 12, "bold")).pack(pady=10)
        # Table
        columns = ('date', 'check_in', 'check_out', 'device_name')
        tree = ttk.Treeview(popup, columns=columns, show='headings')
        tree.heading('date', text='Date')
        tree.heading('check_in', text='Check In')
        tree.heading('check_out', text='Check Out')
        tree.heading('device_name', text='Device Name')
        tree.column('date', width=120)
        tree.column('check_in', width=120)
        tree.column('check_out', width=120)
        tree.column('device_name', width=120)
        # Apply row coloring tags
        tree.tag_configure('checkin', background='#d4f7d4')  # light green
        tree.tag_configure('checkout', background='#d4e6f7')  # light blue
        tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        for _, row in user_logs.iterrows():
            if row['status'] == 'Check In':
                check_in = row['timestamp'].strftime('%H:%M:%S')
                check_out = ''
                tag = 'checkin'
            elif row['status'] == 'Check Out':
                check_in = ''
                check_out = row['timestamp'].strftime('%H:%M:%S')
                tag = 'checkout'
            else:
                check_in = ''
                check_out = ''
                tag = ''
            tree.insert('', tk.END, values=(
                row['timestamp'].strftime('%Y-%m-%d'),
                check_in,
                check_out,
                row['device_name']
            ), tags=(tag,))
        # Export dropdown button
        import datetime
        def get_export_filename(ext):
            now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_user = str(user_name).replace(' ', '_').replace('/', '_')
            return f"attendance_{user_id}_{safe_user}_{now}.{ext}"
        def export_csv():
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=get_export_filename('csv')
            )
            if filename:
                export_df = user_logs.copy()
                export_df['date'] = export_df['timestamp'].dt.strftime('%Y-%m-%d')
                export_df['check_in'] = export_df.apply(lambda r: r['timestamp'].strftime('%H:%M:%S') if r['status'] == 'Check In' else '', axis=1)
                export_df['check_out'] = export_df.apply(lambda r: r['timestamp'].strftime('%H:%M:%S') if r['status'] == 'Check Out' else '', axis=1)
                export_df = export_df[['user_id', 'user_name', 'date', 'check_in', 'check_out', 'device_name']]
                export_df.to_csv(filename, index=False)
                messagebox.showinfo("Exported", f"User summary exported to {filename}")
        def export_pdf():
            try:
                from fpdf import FPDF
            except ImportError:
                messagebox.showerror("Missing Dependency", "Please install fpdf to export PDF.")
                return
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=get_export_filename('pdf')
            )
            if not filename:
                return
            export_df = user_logs.copy()
            export_df['date'] = export_df['timestamp'].dt.strftime('%Y-%m-%d')
            export_df['check_in'] = export_df.apply(lambda r: r['timestamp'].strftime('%H:%M:%S') if r['status'] == 'Check In' else '', axis=1)
            export_df['check_out'] = export_df.apply(lambda r: r['timestamp'].strftime('%H:%M:%S') if r['status'] == 'Check Out' else '', axis=1)
            export_df = export_df[['user_id', 'user_name', 'date', 'check_in', 'check_out', 'device_name']]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 10, f"Attendance Details for {user_name} ({user_id})", ln=True, align='C')
            pdf.ln(5)
            col_widths = [30] * len(export_df.columns)
            for col in export_df.columns:
                pdf.cell(30, 8, str(col), border=1, align='C')
            pdf.ln()
            for _, row in export_df.iterrows():
                for col in export_df.columns:
                    pdf.cell(30, 8, str(row[col]), border=1)
                pdf.ln()
            pdf.output(filename)
            messagebox.showinfo("Exported", f"User summary exported to {filename}")
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        export_menu = tk.Menu(btn_frame, tearoff=0)
        export_menu.add_command(label="Export as CSV", command=export_csv)
        export_menu.add_command(label="Export as PDF", command=export_pdf)
        def show_export_menu(event=None):
            export_menu.tk_popup(btn_frame.winfo_rootx(), btn_frame.winfo_rooty() + btn_frame.winfo_height())
        export_btn = ttk.Button(btn_frame, text="Export", command=show_export_menu)
        export_btn.pack(side=tk.LEFT, padx=10)

    def _add_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about_dialog)
        menubar.add_cascade(label="Help", menu=help_menu)

    def _show_about_dialog(self):
        about = tk.Toplevel(self.root)
        about.title("About ZKTeco Attendance System")
        about.geometry("400x200")
        about.resizable(False, False)
        ttk.Label(about, text="ZKTeco Attendance System", font=("Arial", 14, "bold")).pack(pady=(20, 5))
        ttk.Label(about, text="A Python-based attendance management system for ZKTeco biometric devices.", wraplength=380, justify="center").pack(pady=5)
        ttk.Label(about, text="Developed by Shahid", font=("Arial", 11)).pack(pady=(10, 2))
        # Clickable GitHub link
        def open_github(event=None):
            import webbrowser
            webbrowser.open_new("https://github.com/shahidmusthafa30")
        github_label = tk.Label(about, text="https://github.com/shahidmusthafa30", fg="blue", cursor="hand2", font=("Arial", 10, "underline"))
        github_label.pack()
        github_label.bind("<Button-1>", open_github)
        ttk.Button(about, text="Close", command=about.destroy).pack(pady=15)
        about.transient(self.root)
        about.grab_set()
        self.root.wait_window(about)

def main():
    root = tk.Tk()
    app = AttendanceGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 