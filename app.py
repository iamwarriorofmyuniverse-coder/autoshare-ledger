"""
AutoShare Ledger - Vehicle Rental & Bike-Share Database System
DBMS Laboratory - GUI Database Application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import neu_theme as neu

class RentalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoShare Ledger - Vehicle Rental & Bike-Share System")
        self.root.geometry("1160x780")
        self.root.minsize(1020, 660)
        self.root.configure(bg=neu.BG_COLOR)

        # Initialize database tables, constraints, triggers
        database.init_database()

        # Configure ttk styles for dark glass tables and inputs
        self.setup_ttk_styles()

        # Build Main UI
        self.build_ui()
        self.refresh_all_data()

    def setup_ttk_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Modern Dark Glass Table Styling
        self.style.configure("Treeview",
                             background="#141c2e",
                             foreground="#f1f5f9",
                             rowheight=38,
                             fieldbackground="#141c2e",
                             font=('Segoe UI', 10),
                             borderwidth=0)
        self.style.configure("Treeview.Heading",
                             font=('Segoe UI', 10, 'bold'),
                             background="#1e293b",
                             foreground="#38bdf8",
                             relief="flat",
                             padding=8)
        self.style.map("Treeview",
                       background=[('selected', '#3b82f6')],
                       foreground=[('selected', '#ffffff')])

        # Combobox & Inputs
        self.style.configure("TCombobox",
                             font=('Segoe UI', 10),
                             fieldbackground="#1e293b",
                             background="#334155",
                             foreground="#f8fafc",
                             padding=5)
        self.style.map("TCombobox",
                       fieldbackground=[('readonly', '#1e293b')],
                       foreground=[('readonly', '#f8fafc')])

        self.style.configure("Vertical.TScrollbar", gripcount=0, background="#1e293b", troughcolor=neu.BG_COLOR, borderwidth=0)
        self.style.configure("Horizontal.TScrollbar", gripcount=0, background="#1e293b", troughcolor=neu.BG_COLOR, borderwidth=0)

    def build_ui(self):
        # 1. Top Header Bar
        header_frame = tk.Frame(self.root, bg=neu.BG_COLOR)
        header_frame.pack(fill=tk.X, padx=25, pady=(16, 6))

        title_container = tk.Frame(header_frame, bg=neu.BG_COLOR)
        title_container.pack(side=tk.LEFT)

        tk.Label(title_container, text="⚡ AutoShare Ledger", font=('Segoe UI', 20, 'bold'),
                 fg="#38bdf8", bg=neu.BG_COLOR).pack(anchor="w")
        tk.Label(title_container, text="Car Rental & Bike-Share Database Ledger System",
                 font=('Segoe UI', 10), fg=neu.TEXT_SECONDARY, bg=neu.BG_COLOR).pack(anchor="w")

        # Top Right Live Badge with Emerald Glow
        badge_canvas = tk.Canvas(header_frame, width=205, height=38, bg=neu.BG_COLOR, highlightthickness=0)
        badge_canvas.pack(side=tk.RIGHT, pady=4)
        photo, pad = neu.get_glow_card_image(185, 30, radius=15, theme="emerald", offset=2, blur=3)
        badge_canvas.image = photo
        badge_canvas.create_image(pad + 92, pad + 15, image=photo)
        badge_canvas.create_oval(pad + 18, pad + 11, pad + 26, pad + 19, fill="#10b981", outline="")
        badge_canvas.create_text(pad + 102, pad + 15, text="System Active & Ready", font=('Segoe UI', 9, 'bold'), fill="#34d399")

        # 2. Glowing Stat Cards (Blue, Emerald, Rose, Amber)
        stats_frame = tk.Frame(self.root, bg=neu.BG_COLOR)
        stats_frame.pack(fill=tk.X, padx=20, pady=(10, 15))

        self.card_total = neu.ModernStatCard(stats_frame, title="TOTAL FLEET", value="0", icon="🚘", theme="blue", width=225)
        self.card_total.grid(row=0, column=0, padx=6, sticky="ew")

        self.card_avail = neu.ModernStatCard(stats_frame, title="AVAILABLE", value="0", icon="🟢", theme="emerald", width=225)
        self.card_avail.grid(row=0, column=1, padx=6, sticky="ew")

        self.card_rented = neu.ModernStatCard(stats_frame, title="RENTED OUT", value="0", icon="🔴", theme="rose", width=225)
        self.card_rented.grid(row=0, column=2, padx=6, sticky="ew")

        self.card_rev = neu.ModernStatCard(stats_frame, title="TOTAL REVENUE", value="₹0", icon="💰", theme="amber", width=225)
        self.card_rev.grid(row=0, column=3, padx=6, sticky="ew")

        for c in range(4):
            stats_frame.grid_columnconfigure(c, weight=1)

        # 3. Futuristic Segmented Tab Switcher
        tab_container = tk.Frame(self.root, bg=neu.BG_COLOR)
        tab_container.pack(fill=tk.X, padx=25, pady=(0, 10))

        tabs = ["  🚗 Fleet Status  ", "  📜 Rental Ledger  ", "  👤 Customers  ", "  🎓 SQL Inspector  "]
        self.segmented_tab = neu.ModernSegmentedTab(tab_container, tabs=tabs, on_select=self.switch_tab, width=760, height=44)
        self.segmented_tab.pack(anchor="w")

        # 4. Tab Views Container
        self.content_container = tk.Frame(self.root, bg=neu.BG_COLOR)
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 15))

        # Build individual tabs
        self.tab_frames = []
        self.build_fleet_tab()
        self.build_history_tab()
        self.build_customers_tab()
        self.build_sql_tab()

        # Show initial tab
        self.switch_tab(0)

    def switch_tab(self, index):
        for i, frame in enumerate(self.tab_frames):
            if i == index:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()

    # ==========================================
    # TAB 1: FLEET & LIVE STATUS
    # ==========================================
    def build_fleet_tab(self):
        tab_frame = tk.Frame(self.content_container, bg=neu.BG_COLOR)
        self.tab_frames.append(tab_frame)

        # Action Toolbar with glowing buttons
        toolbar = tk.Frame(tab_frame, bg=neu.BG_COLOR)
        toolbar.pack(fill=tk.X, pady=(0, 12))

        # Filter
        filter_box = tk.Frame(toolbar, bg=neu.BG_COLOR)
        filter_box.pack(side=tk.LEFT)
        tk.Label(filter_box, text="Filter Status:", font=('Segoe UI', 10, 'bold'), fg=neu.TEXT_SECONDARY, bg=neu.BG_COLOR).pack(side=tk.LEFT, padx=(0, 8))
        
        self.filter_var = tk.StringVar(value="All")
        filter_cb = ttk.Combobox(filter_box, textvariable=self.filter_var, values=["All", "Available", "Rented", "Car", "Bike"], state="readonly", width=12)
        filter_cb.pack(side=tk.LEFT)
        filter_cb.bind("<<ComboboxSelected>>", lambda e: self.load_vehicles())

        # Buttons on Right
        btn_refresh = neu.ModernButton(toolbar, text="⟳ Refresh", width=95, height=36, theme="default", command=self.refresh_all_data)
        btn_refresh.pack(side=tk.RIGHT, padx=4)

        btn_delete_veh = neu.ModernButton(toolbar, text="🗑️ Delete Vehicle", width=140, height=36, theme="rose", command=self.delete_selected_vehicle)
        btn_delete_veh.pack(side=tk.RIGHT, padx=4)

        btn_add_veh = neu.ModernButton(toolbar, text="➕ Add Vehicle", width=125, height=36, theme="indigo", command=self.open_add_vehicle_dialog)
        btn_add_veh.pack(side=tk.RIGHT, padx=4)

        btn_return = neu.ModernButton(toolbar, text="🔄 Return (Procedure)", width=165, height=36, theme="blue", command=self.open_return_dialog)
        btn_return.pack(side=tk.RIGHT, padx=4)

        btn_checkout = neu.ModernButton(toolbar, text="🚀 Check Out (Rent)", width=155, height=36, theme="emerald", command=self.open_checkout_dialog)
        btn_checkout.pack(side=tk.RIGHT, padx=4)

        # Table Container
        table_card = tk.Frame(tab_frame, bg="#1e293b", bd=1, relief=tk.SOLID, highlightthickness=0)
        table_card.pack(fill=tk.BOTH, expand=True)

        columns = ("Vehicle_Number", "Model_Name", "Vehicle_Type", "Daily_Rate", "Fuel_Level", "Status", "Action_Hint")
        self.veh_tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.veh_tree.heading("Vehicle_Number", text="Vehicle No (Primary Key)")
        self.veh_tree.heading("Model_Name", text="Model Name")
        self.veh_tree.heading("Vehicle_Type", text="Type")
        self.veh_tree.heading("Daily_Rate", text="Daily Rate (₹)")
        self.veh_tree.heading("Fuel_Level", text="Current Fuel")
        self.veh_tree.heading("Status", text="Availability Status")
        self.veh_tree.heading("Action_Hint", text="Quick Action")

        self.veh_tree.column("Vehicle_Number", width=140, anchor="center")
        self.veh_tree.column("Model_Name", width=250)
        self.veh_tree.column("Vehicle_Type", width=90, anchor="center")
        self.veh_tree.column("Daily_Rate", width=110, anchor="e")
        self.veh_tree.column("Fuel_Level", width=110, anchor="center")
        self.veh_tree.column("Status", width=140, anchor="center")
        self.veh_tree.column("Action_Hint", width=160, anchor="center")

        vsb = ttk.Scrollbar(table_card, orient="vertical", command=self.veh_tree.yview)
        hsb = ttk.Scrollbar(table_card, orient="horizontal", command=self.veh_tree.xview)
        self.veh_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.veh_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_card.grid_rowconfigure(0, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        # High-Contrast Tags
        self.veh_tree.tag_configure("available", background="#0d2818", foreground="#34d399")
        self.veh_tree.tag_configure("rented", background="#2a1215", foreground="#fb7185")

        self.veh_tree.bind("<Double-1>", self.on_vehicle_double_click)

    def load_vehicles(self):
        for item in self.veh_tree.get_children():
            self.veh_tree.delete(item)

        conn = database.get_connection()
        cursor = conn.cursor()

        f_val = self.filter_var.get()
        if f_val == "All":
            cursor.execute("SELECT Vehicle_Number, Model_Name, Vehicle_Type, Daily_Rate, Fuel_Level, Status FROM Vehicles ORDER BY Vehicle_Number;")
        elif f_val in ("Available", "Rented"):
            cursor.execute("SELECT Vehicle_Number, Model_Name, Vehicle_Type, Daily_Rate, Fuel_Level, Status FROM Vehicles WHERE Status = ? ORDER BY Vehicle_Number;", (f_val,))
        elif f_val in ("Car", "Bike"):
            cursor.execute("SELECT Vehicle_Number, Model_Name, Vehicle_Type, Daily_Rate, Fuel_Level, Status FROM Vehicles WHERE Vehicle_Type = ? ORDER BY Vehicle_Number;", (f_val,))

        for row in cursor.fetchall():
            v_num, model, v_type, rate, fuel, status = row
            status_display = "🟢 Available" if status == "Available" else "🔴 Rented"
            action_hint = "👉 Double Click to Rent" if status == "Available" else "👉 Double Click to Return"
            tag = "available" if status == "Available" else "rented"

            self.veh_tree.insert("", "end", values=(
                v_num, model, v_type, f"₹{rate:.2f}", f"{fuel:.1f}%", status_display, action_hint
            ), tags=(tag,))
        conn.close()

    def on_vehicle_double_click(self, event):
        selected = self.veh_tree.selection()
        if not selected:
            return
        item = self.veh_tree.item(selected[0])
        v_num = item['values'][0]
        status = item['values'][5]

        if "Available" in status:
            self.open_checkout_dialog(preselect_vehicle=v_num)
        else:
            self.open_return_dialog(preselect_vehicle=v_num)

    # ==========================================
    # TAB 2: RENTAL HISTORY & AUDIT LEDGER
    # ==========================================
    def build_history_tab(self):
        tab_frame = tk.Frame(self.content_container, bg=neu.BG_COLOR)
        self.tab_frames.append(tab_frame)

        toolbar = tk.Frame(tab_frame, bg=neu.BG_COLOR)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(toolbar, text="📜 Complete Rental Audit Ledger • Tracks Fuel %, Penalties, and Procedure Status",
                 font=('Segoe UI', 10, 'italic'), fg=neu.TEXT_SECONDARY, bg=neu.BG_COLOR).pack(side=tk.LEFT)

        btn_refresh = neu.ModernButton(toolbar, text="⟳ Refresh Log", width=125, height=34, theme="default", command=self.load_history)
        btn_refresh.pack(side=tk.RIGHT)

        table_card = tk.Frame(tab_frame, bg="#1e293b", bd=1, relief=tk.SOLID, highlightthickness=0)
        table_card.pack(fill=tk.BOTH, expand=True)

        cols = ("Rental_ID", "Vehicle", "Customer", "License", "Rental_Date", "Return_Date", "Start_Fuel", "Return_Fuel", "Extra_Fee", "Total_Amount", "Status")
        self.hist_tree = ttk.Treeview(table_card, columns=cols, show="headings")

        self.hist_tree.heading("Rental_ID", text="ID")
        self.hist_tree.heading("Vehicle", text="Vehicle No")
        self.hist_tree.heading("Customer", text="Customer Name")
        self.hist_tree.heading("License", text="Driving License (UNIQUE)")
        self.hist_tree.heading("Rental_Date", text="Rental Date")
        self.hist_tree.heading("Return_Date", text="Return Date")
        self.hist_tree.heading("Start_Fuel", text="Start Fuel")
        self.hist_tree.heading("Return_Fuel", text="Return Fuel")
        self.hist_tree.heading("Extra_Fee", text="Low Fuel Fee")
        self.hist_tree.heading("Total_Amount", text="Total Paid")
        self.hist_tree.heading("Status", text="Status")

        self.hist_tree.column("Rental_ID", width=50, anchor="center")
        self.hist_tree.column("Vehicle", width=110, anchor="center")
        self.hist_tree.column("Customer", width=150)
        self.hist_tree.column("License", width=160)
        self.hist_tree.column("Rental_Date", width=140, anchor="center")
        self.hist_tree.column("Return_Date", width=140, anchor="center")
        self.hist_tree.column("Start_Fuel", width=80, anchor="center")
        self.hist_tree.column("Return_Fuel", width=90, anchor="center")
        self.hist_tree.column("Extra_Fee", width=100, anchor="e")
        self.hist_tree.column("Total_Amount", width=110, anchor="e")
        self.hist_tree.column("Status", width=90, anchor="center")

        vsb = ttk.Scrollbar(table_card, orient="vertical", command=self.hist_tree.yview)
        self.hist_tree.configure(yscrollcommand=vsb.set)
        self.hist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.hist_tree.tag_configure("penalty", background="#2d121b", foreground="#fb7185")
        self.hist_tree.tag_configure("active", background="#0d2138", foreground="#38bdf8")

    def load_history(self):
        for item in self.hist_tree.get_children():
            self.hist_tree.delete(item)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.Rental_ID, r.Vehicle_Number, c.Full_Name, c.Driving_License_Number,
                   r.Rental_Date, r.Return_Date, r.Start_Fuel_Level, r.Return_Fuel_Level,
                   r.Extra_Fee, r.Total_Amount, r.Rental_Status
            FROM Rentals r
            JOIN Customers c ON r.Customer_ID = c.Customer_ID
            ORDER BY r.Rental_ID DESC;
        """)
        for row in cursor.fetchall():
            r_id, v_num, c_name, c_lic, r_date, ret_date, s_fuel, ret_fuel, extra_fee, total, status = row
            ret_fuel_str = f"{ret_fuel:.1f}%" if ret_fuel is not None else "-"
            ret_date_str = ret_date if ret_date else "— Active —"
            tag = "penalty" if extra_fee and extra_fee > 0 else ("active" if status == "Active" else "")

            self.hist_tree.insert("", "end", values=(
                r_id, v_num, c_name, c_lic, r_date, ret_date_str,
                f"{s_fuel:.1f}%", ret_fuel_str, f"₹{extra_fee:.2f}", f"₹{total:.2f}", status
            ), tags=(tag,))
        conn.close()

    # ==========================================
    # TAB 3: CUSTOMER DIRECTORY
    # ==========================================
    def build_customers_tab(self):
        tab_frame = tk.Frame(self.content_container, bg=neu.BG_COLOR)
        self.tab_frames.append(tab_frame)

        toolbar = tk.Frame(tab_frame, bg=neu.BG_COLOR)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(toolbar, text="👤 Customer Registry • Driving License is Enforced UNIQUE",
                 font=('Segoe UI', 10, 'bold'), fg=neu.TEXT_PRIMARY, bg=neu.BG_COLOR).pack(side=tk.LEFT)

        btn_refresh = neu.ModernButton(toolbar, text="⟳ Refresh", width=95, height=34, theme="default", command=self.load_customers)
        btn_refresh.pack(side=tk.RIGHT, padx=4)

        btn_delete_cust = neu.ModernButton(toolbar, text="🗑️ Delete Customer", width=150, height=34, theme="rose", command=self.delete_selected_customer)
        btn_delete_cust.pack(side=tk.RIGHT, padx=4)

        btn_add = neu.ModernButton(toolbar, text="➕ Add Customer", width=145, height=34, theme="indigo", command=self.open_add_customer_dialog)
        btn_add.pack(side=tk.RIGHT, padx=4)

        table_card = tk.Frame(tab_frame, bg="#1e293b", bd=1, relief=tk.SOLID, highlightthickness=0)
        table_card.pack(fill=tk.BOTH, expand=True)

        cols = ("Customer_ID", "Full_Name", "Driving_License_Number", "Phone_Number", "Active_Rentals")
        self.cust_tree = ttk.Treeview(table_card, columns=cols, show="headings")

        self.cust_tree.heading("Customer_ID", text="Customer ID (PK)")
        self.cust_tree.heading("Full_Name", text="Full Name")
        self.cust_tree.heading("Driving_License_Number", text="Driving License (UNIQUE)")
        self.cust_tree.heading("Phone_Number", text="Phone Number")
        self.cust_tree.heading("Active_Rentals", text="Active Rentals")

        self.cust_tree.column("Customer_ID", width=120, anchor="center")
        self.cust_tree.column("Full_Name", width=220)
        self.cust_tree.column("Driving_License_Number", width=250)
        self.cust_tree.column("Phone_Number", width=180, anchor="center")
        self.cust_tree.column("Active_Rentals", width=120, anchor="center")

        vsb = ttk.Scrollbar(table_card, orient="vertical", command=self.cust_tree.yview)
        self.cust_tree.configure(yscrollcommand=vsb.set)
        self.cust_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def load_customers(self):
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.Customer_ID, c.Full_Name, c.Driving_License_Number, c.Phone_Number,
                   COUNT(CASE WHEN r.Rental_Status = 'Active' THEN 1 END) as active_count
            FROM Customers c
            LEFT JOIN Rentals r ON c.Customer_ID = r.Customer_ID
            GROUP BY c.Customer_ID;
        """)
        for row in cursor.fetchall():
            self.cust_tree.insert("", "end", values=row)
        conn.close()

    # ==========================================
    # TAB 4: SQL CODE & INSPECTOR
    # ==========================================
    def build_sql_tab(self):
        tab_frame = tk.Frame(self.content_container, bg=neu.BG_COLOR)
        self.tab_frames.append(tab_frame)

        text_container = tk.Frame(tab_frame, bg="#0d1322", bd=1, relief=tk.SOLID)
        text_container.pack(fill=tk.BOTH, expand=True, pady=5)

        text_area = tk.Text(text_container, font=('Consolas', 10), bg="#0d1322", fg="#e2e8f0", insertbackground="#38bdf8", wrap=tk.NONE)
        ysb = ttk.Scrollbar(text_container, orient="vertical", command=text_area.yview)
        xsb = ttk.Scrollbar(text_container, orient="horizontal", command=text_area.xview)
        text_area.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

        text_area.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")

        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)

        sql_code = """-- =========================================================================
-- DATABASE MANAGEMENT SYSTEM LABORATORY
-- Key Constraints, Integrity, Database Triggers & Stored Procedures
-- =========================================================================

-- 1. VEHICLES TABLE WITH PRIMARY KEY & CHECK CONSTRAINTS
CREATE TABLE Vehicles (
    Vehicle_Number VARCHAR(50) PRIMARY KEY,
    Model_Name VARCHAR(100) NOT NULL,
    Vehicle_Type VARCHAR(20) NOT NULL CHECK(Vehicle_Type IN ('Car', 'Bike')),
    Daily_Rate DECIMAL(10, 2) NOT NULL CHECK(Daily_Rate > 0),
    Status VARCHAR(20) NOT NULL DEFAULT 'Available' CHECK(Status IN ('Available', 'Rented', 'Maintenance')),
    Fuel_Level DECIMAL(5, 2) NOT NULL DEFAULT 100.0 CHECK(Fuel_Level >= 0 AND Fuel_Level <= 100)
);

-- 2. CUSTOMERS TABLE WITH UNIQUE DRIVING LICENSE CONSTRAINT
CREATE TABLE Customers (
    Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Full_Name VARCHAR(100) NOT NULL,
    Driving_License_Number VARCHAR(50) NOT NULL UNIQUE,  -- UNIQUE Constraint
    Phone_Number VARCHAR(20) NOT NULL
);

-- 3. RENTALS TRANSACTION LEDGER
CREATE TABLE Rentals (
    Rental_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Vehicle_Number VARCHAR(50) NOT NULL,
    Customer_ID INTEGER NOT NULL,
    Rental_Date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Return_Date TIMESTAMP NULL,
    Start_Fuel_Level DECIMAL(5, 2) NOT NULL,
    Return_Fuel_Level DECIMAL(5, 2) NULL,
    Daily_Rate DECIMAL(10, 2) NOT NULL,
    Extra_Fee DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
    Total_Amount DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
    Rental_Status VARCHAR(20) NOT NULL DEFAULT 'Active',
    FOREIGN KEY (Vehicle_Number) REFERENCES Vehicles(Vehicle_Number) ON UPDATE CASCADE,
    FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID) ON UPDATE CASCADE
);

-- 4. THE SIMPLE TRIGGER: Switches Vehicle Status to 'Rented' the instant booking row is inserted
CREATE TRIGGER trg_after_booking_insert
AFTER INSERT ON Rentals
WHEN NEW.Rental_Status = 'Active'
BEGIN
    UPDATE Vehicles
    SET Status = 'Rented'
    WHERE Vehicle_Number = NEW.Vehicle_Number;
END;

-- 5. THE STORED PROCEDURE: ReturnVehicle(vehicle_id, fuel_level)
-- Updates rental log, flags vehicle as 'Available', and assesses extra penalty fee if fuel drops < 20%
CREATE PROCEDURE ReturnVehicle(
    IN p_vehicle_num VARCHAR(50),
    IN p_fuel_level DECIMAL(5, 2),
    OUT p_extra_fee DECIMAL(10, 2),
    OUT p_total_amount DECIMAL(10, 2)
)
BEGIN
    DECLARE v_rental_id INT;
    -- Logic: If p_fuel_level < 20.0 Then Extra_Fee = 500.00 Else 0.00
    -- Updates Rentals table and sets Vehicles.Status = 'Available'
END;
"""
        text_area.insert("1.0", sql_code)
        text_area.configure(state="disabled")

    # ==========================================
    # MODAL DIALOGS
    # ==========================================
    def open_checkout_dialog(self, preselect_vehicle=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Check Out Vehicle")
        dialog.geometry("500x420")
        dialog.resizable(False, False)
        dialog.configure(bg="#0f172a")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="🚀 Check Out Vehicle", font=('Segoe UI', 15, 'bold'),
                 fg="#38bdf8", bg="#0f172a").pack(pady=(18, 4))
        tk.Label(dialog, text="Creates a booking row. The database trigger automatically sets status to 'Rented'.",
                 font=('Segoe UI', 9), fg=neu.TEXT_SECONDARY, bg="#0f172a", wraplength=450).pack(pady=(0, 15))

        form = tk.Frame(dialog, bg="#0f172a", padx=30)
        form.pack(fill=tk.BOTH, expand=True)

        # Vehicle Selection
        tk.Label(form, text="Select Available Vehicle:", font=('Segoe UI', 10, 'bold'),
                 fg="#f8fafc", bg="#0f172a").grid(row=0, column=0, sticky="w", pady=5)
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Vehicle_Number, Model_Name, Daily_Rate, Fuel_Level FROM Vehicles WHERE Status = 'Available';")
        avail_vehicles = cursor.fetchall()
        
        veh_map = {f"{v[0]} - {v[1]} (₹{v[2]}/day, Fuel: {v[3]}%)": v[0] for v in avail_vehicles}
        veh_cb = ttk.Combobox(form, values=list(veh_map.keys()), state="readonly", width=42)
        veh_cb.grid(row=1, column=0, sticky="w", pady=(0, 12))

        if preselect_vehicle:
            for k, val in veh_map.items():
                if val == preselect_vehicle:
                    veh_cb.set(k)
                    break
        elif veh_map:
            veh_cb.current(0)

        # Customer Selection
        tk.Label(form, text="Select Customer (Unique License):", font=('Segoe UI', 10, 'bold'),
                 fg="#f8fafc", bg="#0f172a").grid(row=2, column=0, sticky="w", pady=5)
        cursor.execute("SELECT Customer_ID, Full_Name, Driving_License_Number FROM Customers ORDER BY Full_Name;")
        customers = cursor.fetchall()
        conn.close()

        cust_map = {f"{c[1]} (DL: {c[2]})": c[0] for c in customers}
        cust_cb = ttk.Combobox(form, values=list(cust_map.keys()), state="readonly", width=42)
        cust_cb.grid(row=3, column=0, sticky="w", pady=(0, 15))
        if cust_map:
            cust_cb.current(0)

        def do_checkout():
            if not veh_cb.get():
                messagebox.showerror("Error", "No available vehicle selected!", parent=dialog)
                return
            if not cust_cb.get():
                messagebox.showerror("Error", "No customer selected! Please add a customer first.", parent=dialog)
                return

            v_id = veh_map[veh_cb.get()]
            c_id = cust_map[cust_cb.get()]

            success, msg = database.checkout_vehicle(v_id, c_id)
            if success:
                messagebox.showinfo("Checkout Confirmed", msg, parent=dialog)
                dialog.destroy()
                self.refresh_all_data()
            else:
                messagebox.showerror("Checkout Failed", msg, parent=dialog)

        btn_box = tk.Frame(dialog, bg="#0f172a", pady=12)
        btn_box.pack(fill=tk.X, padx=30)

        btn_confirm = neu.ModernButton(btn_box, text="Confirm Check Out", width=155, height=38, theme="emerald", command=do_checkout)
        btn_confirm.pack(side=tk.RIGHT, padx=5)

        btn_cancel = neu.ModernButton(btn_box, text="Cancel", width=90, height=38, theme="default", command=dialog.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=5)

    def open_return_dialog(self, preselect_vehicle=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Return Vehicle")
        dialog.geometry("520x500")
        dialog.resizable(False, False)
        dialog.configure(bg="#0f172a")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="🔄 Return Vehicle & Audit Fuel", font=('Segoe UI', 15, 'bold'),
                 fg="#38bdf8", bg="#0f172a").pack(pady=(18, 4))
        tk.Label(dialog, text="Executes Stored Procedure ReturnVehicle(vehicle_id, fuel_level).\nIf fuel < 20%, a ₹500 Low Fuel Fee is automatically billed.",
                 font=('Segoe UI', 9), fg=neu.TEXT_SECONDARY, bg="#0f172a", justify="center").pack(pady=(0, 15))

        form = tk.Frame(dialog, bg="#0f172a", padx=35)
        form.pack(fill=tk.BOTH, expand=True)

        # Vehicle Selection
        tk.Label(form, text="Select Rented Vehicle:", font=('Segoe UI', 10, 'bold'),
                 fg="#f8fafc", bg="#0f172a").grid(row=0, column=0, sticky="w", pady=5)

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Vehicle_Number, Model_Name FROM Vehicles WHERE Status = 'Rented';")
        rented_vehicles = cursor.fetchall()
        conn.close()

        rented_map = {f"{v[0]} - {v[1]}": v[0] for v in rented_vehicles}
        veh_cb = ttk.Combobox(form, values=list(rented_map.keys()), state="readonly", width=42)
        veh_cb.grid(row=1, column=0, sticky="w", pady=(0, 12))

        if preselect_vehicle:
            for k, val in rented_map.items():
                if val == preselect_vehicle:
                    veh_cb.set(k)
                    break
        elif rented_map:
            veh_cb.current(0)

        # Return Fuel Slider
        tk.Label(form, text="Return Fuel Level (%):", font=('Segoe UI', 10, 'bold'),
                 fg="#f8fafc", bg="#0f172a").grid(row=2, column=0, sticky="w", pady=5)

        fuel_frame = tk.Frame(form, bg="#0f172a")
        fuel_frame.grid(row=3, column=0, sticky="w", pady=(0, 6))

        fuel_var = tk.DoubleVar(value=80.0)
        fuel_scale = ttk.Scale(fuel_frame, from_=0, to=100, variable=fuel_var, orient="horizontal", length=250)
        fuel_scale.pack(side=tk.LEFT, padx=(0, 10))

        fuel_lbl = tk.Label(fuel_frame, text="80.0%", font=('Segoe UI', 11, 'bold'), width=8,
                            fg="#38bdf8", bg="#0f172a")
        fuel_lbl.pack(side=tk.LEFT)

        penalty_alert = tk.Label(form, text="", font=('Segoe UI', 9, 'bold'), bg="#0f172a")
        penalty_alert.grid(row=4, column=0, sticky="w", pady=(0, 10))

        def update_fuel_display(*args):
            val = fuel_var.get()
            fuel_lbl.config(text=f"{val:.1f}%")
            if val < 20.0:
                fuel_lbl.config(fg="#f43f5e")
                penalty_alert.config(text="⚠️ LOW FUEL ALERT: <20% will incur ₹500 Low Fuel Fee!", fg="#fb7185")
            else:
                fuel_lbl.config(fg="#34d399")
                penalty_alert.config(text="✓ Fuel level normal (No extra penalty fee)", fg="#34d399")

        fuel_var.trace_add("write", update_fuel_display)
        update_fuel_display()

        # Colorful Presets
        preset_frame = tk.Frame(form, bg="#0f172a")
        preset_frame.grid(row=5, column=0, sticky="w", pady=(0, 10))
        tk.Label(preset_frame, text="Presets:", font=('Segoe UI', 9, 'italic'), fg=neu.TEXT_SECONDARY, bg="#0f172a").pack(side=tk.LEFT, padx=(0, 6))
        
        btn_p1 = neu.ModernButton(preset_frame, text="Full (100%)", width=90, height=28, theme="emerald", command=lambda: fuel_var.set(100.0))
        btn_p1.pack(side=tk.LEFT, padx=3)
        btn_p2 = neu.ModernButton(preset_frame, text="Half (50%)", width=90, height=28, theme="blue", command=lambda: fuel_var.set(50.0))
        btn_p2.pack(side=tk.LEFT, padx=3)
        btn_p3 = neu.ModernButton(preset_frame, text="Low (10%)", width=90, height=28, theme="rose", command=lambda: fuel_var.set(10.0))
        btn_p3.pack(side=tk.LEFT, padx=3)

        def do_return():
            if not veh_cb.get():
                messagebox.showerror("Error", "No rented vehicle selected for return!", parent=dialog)
                return

            v_id = rented_map[veh_cb.get()]
            ret_fuel = round(fuel_var.get(), 1)

            success, msg, extra_fee, total = database.ReturnVehicle(v_id, ret_fuel)
            if success:
                messagebox.showinfo("Procedure Executed", msg, parent=dialog)
                dialog.destroy()
                self.refresh_all_data()
            else:
                messagebox.showerror("Return Error", msg, parent=dialog)

        btn_box = tk.Frame(dialog, bg="#0f172a", pady=12)
        btn_box.pack(fill=tk.X, padx=35)

        btn_exec = neu.ModernButton(btn_box, text="Execute Return Procedure", width=195, height=38, theme="blue", command=do_return)
        btn_exec.pack(side=tk.RIGHT, padx=5)

        btn_cancel = neu.ModernButton(btn_box, text="Cancel", width=90, height=38, theme="default", command=dialog.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=5)

    def open_add_vehicle_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Vehicle")
        dialog.geometry("460x390")
        dialog.resizable(False, False)
        dialog.configure(bg="#0f172a")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="➕ Register New Vehicle", font=('Segoe UI', 14, 'bold'),
                 fg="#38bdf8", bg="#0f172a").pack(pady=(16, 10))

        form = tk.Frame(dialog, bg="#0f172a", padx=30)
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Vehicle Number (Primary Key):", font=('Segoe UI', 9, 'bold'), fg="#f8fafc", bg="#0f172a").grid(row=0, column=0, sticky="w", pady=6)
        v_num_entry = ttk.Entry(form, width=30)
        v_num_entry.grid(row=0, column=1, pady=6)

        tk.Label(form, text="Model Name:", font=('Segoe UI', 9, 'bold'), fg="#f8fafc", bg="#0f172a").grid(row=1, column=0, sticky="w", pady=6)
        v_model_entry = ttk.Entry(form, width=30)
        v_model_entry.grid(row=1, column=1, pady=6)

        tk.Label(form, text="Vehicle Type:", font=('Segoe UI', 9, 'bold'), fg="#f8fafc", bg="#0f172a").grid(row=2, column=0, sticky="w", pady=6)
        v_type_cb = ttk.Combobox(form, values=["Car", "Bike"], state="readonly", width=28)
        v_type_cb.current(0)
        v_type_cb.grid(row=2, column=1, pady=6)

        tk.Label(form, text="Daily Rate (₹):", font=('Segoe UI', 9, 'bold'), fg="#f8fafc", bg="#0f172a").grid(row=3, column=0, sticky="w", pady=6)
        v_rate_entry = ttk.Entry(form, width=30)
        v_rate_entry.insert(0, "1500.00")
        v_rate_entry.grid(row=3, column=1, pady=6)

        def save_vehicle():
            v_num = v_num_entry.get().strip()
            v_model = v_model_entry.get().strip()
            v_type = v_type_cb.get()
            try:
                v_rate = float(v_rate_entry.get().strip())
                if v_rate <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "Daily Rate must be a positive number!", parent=dialog)
                return

            if not v_num or not v_model:
                messagebox.showerror("Validation Error", "Vehicle Number and Model are required!", parent=dialog)
                return

            success, msg = database.add_vehicle(v_num, v_model, v_type, v_rate)
            if success:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self.refresh_all_data()
            else:
                messagebox.showerror("Constraint Error", msg, parent=dialog)

        btn_box = tk.Frame(dialog, bg="#0f172a", pady=12)
        btn_box.pack(fill=tk.X, padx=30)

        btn_save = neu.ModernButton(btn_box, text="Save Vehicle", width=125, height=36, theme="indigo", command=save_vehicle)
        btn_save.pack(side=tk.RIGHT, padx=5)

        btn_cancel = neu.ModernButton(btn_box, text="Cancel", width=90, height=36, theme="default", command=dialog.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=5)

    def open_add_customer_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Customer")
        dialog.geometry("460x350")
        dialog.resizable(False, False)
        dialog.configure(bg="#0f172a")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="👤 Register Customer", font=('Segoe UI', 14, 'bold'),
                 fg="#38bdf8", bg="#0f172a").pack(pady=(16, 4))
        tk.Label(dialog, text="Demonstrates UNIQUE key constraint on Driving License",
                 font=('Segoe UI', 9), fg=neu.TEXT_SECONDARY, bg="#0f172a").pack(pady=(0, 10))

        form = tk.Frame(dialog, bg="#0f172a", padx=30)
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Full Name:", font=('Segoe UI', 9, 'bold'), fg="#f8fafc", bg="#0f172a").grid(row=0, column=0, sticky="w", pady=6)
        name_entry = ttk.Entry(form, width=28)
        name_entry.grid(row=0, column=1, pady=6)

        tk.Label(form, text="Driving License (UNIQUE):", font=('Segoe UI', 9, 'bold'), fg="#f8fafc", bg="#0f172a").grid(row=1, column=0, sticky="w", pady=6)
        lic_entry = ttk.Entry(form, width=28)
        lic_entry.grid(row=1, column=1, pady=6)

        tk.Label(form, text="Phone Number:", font=('Segoe UI', 9, 'bold'), fg="#f8fafc", bg="#0f172a").grid(row=2, column=0, sticky="w", pady=6)
        phone_entry = ttk.Entry(form, width=28)
        phone_entry.grid(row=2, column=1, pady=6)

        def save_customer():
            c_name = name_entry.get().strip()
            c_lic = lic_entry.get().strip()
            c_phone = phone_entry.get().strip()

            if not c_name or not c_lic or not c_phone:
                messagebox.showerror("Validation Error", "All fields are required!", parent=dialog)
                return

            success, cust_id, msg = database.add_customer(c_name, c_lic, c_phone)
            if success:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self.refresh_all_data()
            else:
                messagebox.showerror("Constraint Violation", msg, parent=dialog)

        btn_box = tk.Frame(dialog, bg="#0f172a", pady=12)
        btn_box.pack(fill=tk.X, padx=30)

        btn_save = neu.ModernButton(btn_box, text="Save Customer", width=135, height=36, theme="indigo", command=save_customer)
        btn_save.pack(side=tk.RIGHT, padx=5)

        btn_cancel = neu.ModernButton(btn_box, text="Cancel", width=90, height=36, theme="default", command=dialog.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=5)

    def delete_selected_vehicle(self):
        selected = self.veh_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a vehicle from the table to delete.")
            return
        item = self.veh_tree.item(selected[0])
        v_num = item['values'][0]
        model_name = item['values'][1]
        status = item['values'][5]

        if "Rented" in status:
            messagebox.showerror("Operation Blocked", f"Cannot delete vehicle '{v_num}' ({model_name}) because it is currently Rented Out!\n\nPlease process its return before deleting.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete Vehicle",
            f"Are you sure you want to permanently delete vehicle:\n\n"
            f"• Registration No: {v_num}\n"
            f"• Model: {model_name}\n\n"
            f"This will remove the vehicle and its past completed ledger history from the database.",
            icon='warning'
        )
        if not confirm:
            return

        success, msg = database.delete_vehicle(v_num)
        if success:
            messagebox.showinfo("Deleted Successfully", msg)
            self.refresh_all_data()
        else:
            messagebox.showerror("Delete Failed", msg)

    def delete_selected_customer(self):
        selected = self.cust_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a customer from the table to delete.")
            return
        item = self.cust_tree.item(selected[0])
        cust_id = item['values'][0]
        cust_name = item['values'][1]
        license_num = item['values'][2]
        active_rentals = int(item['values'][4])

        if active_rentals > 0:
            messagebox.showerror("Operation Blocked", f"Cannot delete customer '{cust_name}' because they currently have {active_rentals} active rental booking(s)!\n\nPlease return all rented vehicles first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete Customer",
            f"Are you sure you want to permanently delete customer:\n\n"
            f"• Customer ID: {cust_id}\n"
            f"• Name: {cust_name}\n"
            f"• Driving License: {license_num}\n\n"
            f"This will delete the customer and their past completed rental records.",
            icon='warning'
        )
        if not confirm:
            return

        success, msg = database.delete_customer(cust_id)
        if success:
            messagebox.showinfo("Deleted Successfully", msg)
            self.refresh_all_data()
        else:
            messagebox.showerror("Delete Failed", msg)

    def refresh_all_data(self):
        self.load_vehicles()
        self.load_history()
        self.load_customers()

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Vehicles;")
        total_veh = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Vehicles WHERE Status = 'Available';")
        avail_veh = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Vehicles WHERE Status = 'Rented';")
        rented_veh = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(Total_Amount), 0) FROM Rentals;")
        total_rev = cursor.fetchone()[0]
        conn.close()

        self.card_total.update_value(total_veh)
        self.card_avail.update_value(avail_veh)
        self.card_rented.update_value(rented_veh)
        self.card_rev.update_value(f"₹{total_rev:,.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RentalApp(root)
    root.mainloop()
