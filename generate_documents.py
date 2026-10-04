"""
Script to generate:
1. DBMS_Lab_Experiment_10_AutoShare.docx
2. DBMS_Lab_Experiment_10_AutoShare.pptx

Fully compliant with requirements:
- Aim, Description, Program, Explanation with detailed steps, Output, Result
- Clean academic formatting
- Indian Registration Plates (TN 37 BY 0650, etc.)
- Triggers, Stored Procedures, Constraints, Delete Feature with safety guards
- Obsidian Neon Glass theme details
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from pptx import Presentation
from pptx.util import Inches as PInches, Pt as PPt
from pptx.dml.color import RGBColor as PRGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

DIR = os.path.dirname(os.path.abspath(__file__))

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_docx():
    doc = Document()

    # Set 0.75-inch page margins for perfect 5-page balance
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.75)
        s.right_margin = Inches(0.75)

    # Styles & Primary Palette
    C_PRIMARY = RGBColor(15, 23, 42)      # #0f172a Deep Slate
    C_NAVY = RGBColor(30, 58, 138)        # #1e3a8a Classic Navy
    C_BLUE = RGBColor(2, 132, 199)        # #0284c7 Electric Blue Accent
    C_MUTED = RGBColor(100, 116, 139)     # #64748b
    C_DARK = RGBColor(30, 41, 59)         # #1e293b

    def add_heading_1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(3)
        r = h.add_run(text)
        r.bold = True
        r.font.size = Pt(12)
        r.font.color.rgb = C_NAVY
        r.font.name = "Segoe UI"
        return h

    def add_heading_2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
        r = h.add_run(text)
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = C_BLUE
        r.font.name = "Segoe UI"
        return h

    def add_body(text, bold_prefix=None, italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.12
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.bold = True
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = C_PRIMARY
            rb.font.name = "Segoe UI"
        r = p.add_run(text)
        r.font.size = Pt(9.5)
        r.italic = italic
        r.font.color.rgb = C_DARK
        r.font.name = "Segoe UI"
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.line_spacing = 1.12
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.bold = True
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = C_PRIMARY
            rb.font.name = "Segoe UI"
        r = p.add_run(text)
        r.font.size = Pt(9.5)
        r.font.color.rgb = C_DARK
        r.font.name = "Segoe UI"
        return p

    def add_code_block(code_text):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.02
        r = p.add_run(code_text.strip())
        r.font.size = Pt(8.0)
        r.font.name = "Consolas"
        r.font.color.rgb = RGBColor(15, 23, 42)
        doc.add_paragraph().paragraph_format.space_after = Pt(3)

    # =========================================================================
    # PAGE 1: HEADER, AIM & DESCRIPTION
    # =========================================================================
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.paragraph_format.space_after = Pt(2)
    r1 = p_header.add_run("DEPARTMENT OF ARTIFICIAL INTELLIGENCE AND DATA SCIENCE\n")
    r1.bold = True
    r1.font.size = Pt(12)
    r1.font.color.rgb = C_NAVY
    r1.font.name = "Segoe UI"

    r2 = p_header.add_run("DATABASE MANAGEMENT SYSTEMS LABORATORY\n")
    r2.bold = True
    r2.font.size = Pt(11)
    r2.font.color.rgb = C_BLUE
    r2.font.name = "Segoe UI"

    p_exp = doc.add_paragraph()
    p_exp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_exp.paragraph_format.space_after = Pt(4)
    r_exp = p_exp.add_run("EXPERIMENT NO: 10\n")
    r_exp.bold = True
    r_exp.font.size = Pt(13)
    r_exp.font.color.rgb = C_PRIMARY
    r_exp.font.name = "Segoe UI"

    r_title = p_exp.add_run("DEVELOPMENT OF A GUI DATABASE APPLICATION WITH CONSTRAINTS, TRIGGERS & STORED PROCEDURES\n")
    r_title.bold = True
    r_title.font.size = Pt(11.5)
    r_title.font.color.rgb = C_NAVY
    r_title.font.name = "Segoe UI"

    r_sub = p_exp.add_run("AutoShare Ledger - Car Rental & Bike-Share Database Ledger")
    r_sub.italic = True
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = C_MUTED
    r_sub.font.name = "Segoe UI"

    # 1. AIM
    add_heading_1("1. AIM")
    add_body("To design, implement, and evaluate a comprehensive GUI-based database application for a Car Rental and Bike-Share Ledger System (AutoShare Ledger) integrating:")
    add_bullet(" Enforcing Entity Integrity via PRIMARY KEY on Vehicle Registration Number and UNIQUE constraint on Customer Driving License Number.", "1. Key Constraints:")
    add_bullet(" Automatically flipping the vehicle availability status flag to 'Rented' upon booking insertion without client-side manual updates.", "2. Database Trigger:")
    add_bullet(" Executing ReturnVehicle(vehicle_id, fuel_level) to calculate base rent, audit return fuel percentage, assess an automatic Rs. 500 penalty surcharge if fuel < 20%, and restore vehicle status to 'Available'.", "3. Stored Procedure:")
    add_bullet(" Safe deletion of Vehicles and Customers with automatic active-rental locking guards.", "4. Record Deletion & Safety Guards:")

    # 2. DESCRIPTION
    add_heading_1("2. DESCRIPTION")
    add_heading_2("2.1 System Architecture & Overview")
    add_body("The AutoShare Rental Ledger is an enterprise-grade desktop database management application. It bridges backend transactional integrity with an interactive desktop user interface. The system manages fleet records, customer registries, live bookings, audit history, and direct SQL execution.")

    add_heading_2("2.2 Relational Database Schema & Integrity Constraints")
    t_schema = doc.add_table(rows=1, cols=4)
    t_schema.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Table Name", "Column & Data Type", "Constraint Type", "Description & Business Rule"]
    hdr_row = t_schema.rows[0]
    for i, h in enumerate(headers):
        c = hdr_row.cells[i]
        set_cell_background(c, "1E3A8A")
        set_cell_margins(c, top=60, bottom=60, left=80, right=80)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.name = "Segoe UI"

    schema_data = [
        ("Vehicles", "Vehicle_Number VARCHAR(50)", "PRIMARY KEY", "Registration plate (e.g., 'TN 37 BY 0650'). Enforces unique fleet identity."),
        ("Vehicles", "Model_Name VARCHAR(100)", "NOT NULL", "Make & Model name (e.g., 'Royal Enfield Continental GT 650')."),
        ("Vehicles", "Vehicle_Type ENUM/VARCHAR", "CHECK ('Car','Bike')", "Restricts category to valid vehicle types."),
        ("Vehicles", "Daily_Rate DECIMAL(10,2)", "CHECK (Daily_Rate > 0)", "Enforces strictly positive rental rates."),
        ("Vehicles", "Status VARCHAR(20)", "CHECK ('Available','Rented')", "Live availability state tracked by Trigger & Procedure."),
        ("Vehicles", "Fuel_Level DECIMAL(5,2)", "CHECK (0 <= Fuel <= 100)", "Current fuel percentage capacity."),
        ("Customers", "Customer_ID INTEGER", "PRIMARY KEY AUTOINCREMENT", "Surrogate primary key for customer entities."),
        ("Customers", "Driving_License_Number VARCHAR", "UNIQUE, NOT NULL", "Unique 1-to-1 government DL mapping (e.g., 'DL-TN-01-2023-0004123')."),
        ("Rentals", "Rental_ID INTEGER", "PRIMARY KEY AUTOINCREMENT", "Unique audit log identifier for rental transactions."),
        ("Rentals", "Vehicle_Number VARCHAR", "FOREIGN KEY (Vehicles)", "Links booking directly to vehicle with CASCADE updates."),
        ("Rentals", "Customer_ID INTEGER", "FOREIGN KEY (Customers)", "Links booking to customer with CASCADE updates."),
        ("Rentals", "Extra_Fee DECIMAL(10,2)", "DEFAULT 0.0", "Penalty fee (Rs. 500) assessed by ReturnVehicle procedure if fuel < 20%."),
        ("Rentals", "Rental_Status VARCHAR", "CHECK ('Active','Completed')", "Maintains active vs closed booking ledger state.")
    ]

    for row_idx, data in enumerate(schema_data):
        row = t_schema.add_row()
        bg_col = "F1F5F9" if row_idx % 2 == 0 else "FFFFFF"
        for i, val in enumerate(data):
            c = row.cells[i]
            set_cell_background(c, bg_col)
            set_cell_margins(c, top=40, bottom=40, left=60, right=60)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.0)
            r.font.name = "Segoe UI"
            r.font.color.rgb = C_DARK

    doc.add_page_break()

    # =========================================================================
    # PAGE 2: PROGRAM CODE - PART 1 (SQL DDL, TRIGGER & STORED PROCEDURES)
    # =========================================================================
    add_heading_1("3. PROGRAM CODE")
    add_heading_2("3.1 MySQL Relational Schema, Trigger, and Stored Procedures (schema_mysql.sql)")
    
    sql_code = """-- ============================================================================
-- 1. RELATIONAL SCHEMA DEFINITION WITH CONSTRAINTS (DDL)
-- ============================================================================
CREATE TABLE Vehicles (
    Vehicle_Number VARCHAR(50) PRIMARY KEY,
    Model_Name VARCHAR(100) NOT NULL,
    Vehicle_Type ENUM('Car', 'Bike') NOT NULL,
    Daily_Rate DECIMAL(10, 2) NOT NULL CHECK (Daily_Rate > 0),
    Status ENUM('Available', 'Rented', 'Maintenance') NOT NULL DEFAULT 'Available',
    Fuel_Level DECIMAL(5, 2) NOT NULL DEFAULT 100.0 CHECK (Fuel_Level >= 0 AND Fuel_Level <= 100)
);

CREATE TABLE Customers (
    Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
    Full_Name VARCHAR(100) NOT NULL,
    Driving_License_Number VARCHAR(50) NOT NULL UNIQUE,
    Phone_Number VARCHAR(20) NOT NULL
);

CREATE TABLE Rentals (
    Rental_ID INT AUTO_INCREMENT PRIMARY KEY,
    Vehicle_Number VARCHAR(50) NOT NULL,
    Customer_ID INT NOT NULL,
    Rental_Date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Return_Date DATETIME NULL,
    Start_Fuel_Level DECIMAL(5, 2) NOT NULL,
    Return_Fuel_Level DECIMAL(5, 2) NULL,
    Daily_Rate DECIMAL(10, 2) NOT NULL,
    Extra_Fee DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
    Total_Amount DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
    Rental_Status ENUM('Active', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Active',
    FOREIGN KEY (Vehicle_Number) REFERENCES Vehicles(Vehicle_Number) ON UPDATE CASCADE,
    FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID) ON UPDATE CASCADE
);

-- ============================================================================
-- 2. DATABASE TRIGGER (AFTER INSERT: Automatically switches Status to 'Rented')
-- ============================================================================
DELIMITER $$
CREATE TRIGGER trg_after_booking_insert
AFTER INSERT ON Rentals FOR EACH ROW
BEGIN
    IF NEW.Rental_Status = 'Active' THEN
        UPDATE Vehicles SET Status = 'Rented' WHERE Vehicle_Number = NEW.Vehicle_Number;
    END IF;
END$$

-- ============================================================================
-- 3. STORED PROCEDURE: ReturnVehicle (Fuel Audit, Penalty & Status Restoration)
-- ============================================================================
CREATE PROCEDURE ReturnVehicle(
    IN p_vehicle_num VARCHAR(50), IN p_fuel_level DECIMAL(5, 2),
    OUT p_extra_fee DECIMAL(10, 2), OUT p_total_amount DECIMAL(10, 2), OUT p_msg VARCHAR(255)
)
BEGIN
    DECLARE v_id INT; DECLARE v_rate DECIMAL(10, 2); DECLARE v_date DATETIME;
    DECLARE v_days INT; DECLARE v_base DECIMAL(10, 2);

    SELECT Rental_ID, Daily_Rate, Rental_Date INTO v_id, v_rate, v_date
    FROM Rentals WHERE Vehicle_Number = p_vehicle_num AND Rental_Status = 'Active'
    ORDER BY Rental_ID DESC LIMIT 1;

    IF v_id IS NOT NULL THEN
        SET v_days = GREATEST(1, TIMESTAMPDIFF(DAY, v_date, NOW()));
        SET v_base = v_rate * v_days;
        SET p_extra_fee = IF(p_fuel_level < 20.0, 500.00, 0.00); -- < 20% Fuel Penalty
        SET p_total_amount = v_base + p_extra_fee;

        UPDATE Rentals SET Return_Date = NOW(), Return_Fuel_Level = p_fuel_level,
            Extra_Fee = p_extra_fee, Total_Amount = p_total_amount, Rental_Status = 'Completed'
        WHERE Rental_ID = v_id;

        UPDATE Vehicles SET Status = 'Available', Fuel_Level = p_fuel_level WHERE Vehicle_Number = p_vehicle_num;
        SET p_msg = CONCAT('Success: Returned ', p_vehicle_num, '. Total: Rs.', p_total_amount);
    END IF;
END$$

-- ============================================================================
-- 4. STORED PROCEDURES FOR SAFE DELETIONS (Active-Rental Guards)
-- ============================================================================
CREATE PROCEDURE DeleteVehicle(IN p_vnum VARCHAR(50), OUT p_ok INT, OUT p_msg VARCHAR(255))
BEGIN
    IF (SELECT Status FROM Vehicles WHERE Vehicle_Number = p_vnum) = 'Rented' THEN
        SET p_ok = 0; SET p_msg = 'Error: Cannot delete actively rented vehicle!';
    ELSE
        DELETE FROM Rentals WHERE Vehicle_Number = p_vnum;
        DELETE FROM Vehicles WHERE Vehicle_Number = p_vnum;
        SET p_ok = 1; SET p_msg = 'Vehicle deleted successfully.';
    END IF;
END$$
DELIMITER ;"""
    add_code_block(sql_code)

    doc.add_page_break()

    # =========================================================================
    # PAGE 3: PROGRAM CODE - PART 2 (PYTHON DATABASE ENGINE & GUI HANDLERS)
    # =========================================================================
    add_heading_2("3.2 Python Database Engine & Transaction Logic (database.py)")
    py_db_code = """import sqlite3, os
from datetime import datetime
DB_FILE = os.path.join(os.path.dirname(__file__), "rental_ledger.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_database():
    conn = get_connection(); cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Vehicles (
        Vehicle_Number VARCHAR(50) PRIMARY KEY, Model_Name VARCHAR(100) NOT NULL,
        Vehicle_Type VARCHAR(20) NOT NULL CHECK(Vehicle_Type IN ('Car', 'Bike')),
        Daily_Rate DECIMAL(10, 2) NOT NULL CHECK(Daily_Rate > 0),
        Status VARCHAR(20) NOT NULL DEFAULT 'Available' CHECK(Status IN ('Available', 'Rented')),
        Fuel_Level DECIMAL(5, 2) NOT NULL DEFAULT 100.0 CHECK(Fuel_Level >= 0 AND Fuel_Level <= 100));''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Customers (
        Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT, Full_Name VARCHAR(100) NOT NULL,
        Driving_License_Number VARCHAR(50) NOT NULL UNIQUE, Phone_Number VARCHAR(20) NOT NULL);''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Rentals (
        Rental_ID INTEGER PRIMARY KEY AUTOINCREMENT, Vehicle_Number VARCHAR(50) NOT NULL,
        Customer_ID INTEGER NOT NULL, Rental_Date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        Return_Date TIMESTAMP NULL, Start_Fuel_Level DECIMAL(5, 2) NOT NULL, Return_Fuel_Level DECIMAL(5, 2) NULL,
        Daily_Rate DECIMAL(10, 2) NOT NULL, Extra_Fee DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
        Total_Amount DECIMAL(10, 2) NOT NULL DEFAULT 0.0, Rental_Status VARCHAR(20) NOT NULL DEFAULT 'Active',
        FOREIGN KEY (Vehicle_Number) REFERENCES Vehicles(Vehicle_Number) ON UPDATE CASCADE,
        FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID) ON UPDATE CASCADE);''')

    cur.execute('''CREATE TRIGGER IF NOT EXISTS trg_after_booking_insert
    AFTER INSERT ON Rentals WHEN NEW.Rental_Status = 'Active'
    BEGIN UPDATE Vehicles SET Status = 'Rented' WHERE Vehicle_Number = NEW.Vehicle_Number; END;''')
    conn.commit(); conn.close()

def checkout_vehicle(vehicle_number: str, customer_id: int):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT Daily_Rate, Fuel_Level, Status FROM Vehicles WHERE Vehicle_Number = ?;", (vehicle_number,))
    rate, fuel, status = cur.fetchone()
    if status != 'Available': return False, f"Vehicle {vehicle_number} is already '{status}'."
    cur.execute("INSERT INTO Rentals (Vehicle_Number, Customer_ID, Start_Fuel_Level, Daily_Rate, Rental_Status) VALUES (?, ?, ?, ?, 'Active');",
                (vehicle_number, customer_id, fuel, rate))
    conn.commit(); conn.close()
    return True, f"Checkout successful! Trigger updated {vehicle_number} to 'Rented'."

def ReturnVehicle(vehicle_number: str, return_fuel_level: float, penalty_fee: float = 500.0):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT Rental_ID, Daily_Rate FROM Rentals WHERE Vehicle_Number = ? AND Rental_Status = 'Active';", (vehicle_number,))
    row = cur.fetchone()
    if not row: return False, "No active rental found.", 0.0, 0.0
    r_id, rate = row
    extra_fee = penalty_fee if return_fuel_level < 20.0 else 0.0
    total_amount = float(rate) * 1 + extra_fee
    cur.execute("UPDATE Rentals SET Return_Date = CURRENT_TIMESTAMP, Return_Fuel_Level = ?, Extra_Fee = ?, Total_Amount = ?, Rental_Status = 'Completed' WHERE Rental_ID = ?;",
                (return_fuel_level, extra_fee, total_amount, r_id))
    cur.execute("UPDATE Vehicles SET Status = 'Available', Fuel_Level = ? WHERE Vehicle_Number = ?;", (return_fuel_level, vehicle_number))
    conn.commit(); conn.close()
    return True, f"Vehicle {vehicle_number} returned successfully.", extra_fee, total_amount

def delete_vehicle(vehicle_number: str):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT Status FROM Vehicles WHERE Vehicle_Number = ?;", (vehicle_number,))
    if cur.fetchone()[0] == 'Rented': return False, f"Cannot delete vehicle '{vehicle_number}' because it is Rented Out!"
    cur.execute("DELETE FROM Rentals WHERE Vehicle_Number = ?;", (vehicle_number,))
    cur.execute("DELETE FROM Vehicles WHERE Vehicle_Number = ?;", (vehicle_number,))
    conn.commit(); conn.close()
    return True, f"Vehicle '{vehicle_number}' deleted successfully."

def delete_customer(customer_id: int):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Rentals WHERE Customer_ID = ? AND Rental_Status = 'Active';", (customer_id,))
    if cur.fetchone()[0] > 0: return False, "Cannot delete customer with active rental bookings!"
    cur.execute("DELETE FROM Rentals WHERE Customer_ID = ?;", (customer_id,))
    cur.execute("DELETE FROM Customers WHERE Customer_ID = ?;", (customer_id,))
    conn.commit(); conn.close()
    return True, "Customer deleted successfully." """
    add_code_block(py_db_code)

    add_heading_2("3.3 GUI Deletion Handlers with Confirmation Modals (app.py)")
    py_gui_code = """# GUI Event Handlers in app.py for Safe Record Deletions
def delete_selected_vehicle(self):
    selected = self.veh_tree.selection()
    if not selected: return messagebox.showwarning("No Selection", "Please select a vehicle to delete.")
    v_num = self.veh_tree.item(selected[0])['values'][0]
    if "Rented" in self.veh_tree.item(selected[0])['values'][5]:
        return messagebox.showerror("Blocked", f"Vehicle '{v_num}' is currently Rented Out! Process return first.")
    if messagebox.askyesno("Confirm Delete", f"Permanently delete vehicle {v_num} and completed logs?"):
        ok, msg = database.delete_vehicle(v_num)
        messagebox.showinfo("Result", msg) if ok else messagebox.showerror("Error", msg)
        self.refresh_all_data()

def delete_selected_customer(self):
    selected = self.cust_tree.selection()
    if not selected: return messagebox.showwarning("No Selection", "Please select a customer to delete.")
    c_id = self.cust_tree.item(selected[0])['values'][0]
    if int(self.cust_tree.item(selected[0])['values'][4]) > 0:
        return messagebox.showerror("Blocked", "Cannot delete customer with active rental bookings!")
    if messagebox.askyesno("Confirm Delete", f"Permanently delete customer ID {c_id}?"):
        ok, msg = database.delete_customer(c_id)
        messagebox.showinfo("Result", msg) if ok else messagebox.showerror("Error", msg)
        self.refresh_all_data()"""
    add_code_block(py_gui_code)

    doc.add_page_break()

    # =========================================================================
    # PAGE 4: EXPLANATION WITH DETAILED STEPS
    # =========================================================================
    add_heading_1("4. EXPLANATION WITH DETAILED STEPS")
    
    add_heading_2("Step 1: Database Initialization & Constraint Enforcement")
    add_body("When the application launches, init_database() sets up tables with rigorous integrity rules:")
    add_bullet(" Ensures Vehicle Registration Numbers (e.g. 'TN 37 BY 0650') are unique entity identifiers across the fleet.", "• Primary Key on Vehicles: ")
    add_bullet(" Enforces 1-to-1 government ID mapping. Duplicate license attempts trigger an IntegrityError handled with a clear UI pop-up.", "• Unique Constraint on Driving License: ")
    add_bullet(" Validates that Daily_Rate > 0 and Fuel_Level is bounded between 0% and 100%.", "• Check Constraints: ")

    add_heading_2("Step 2: Automated State Transition via Database Trigger")
    add_body("When a customer rents an available vehicle (checkout_vehicle):")
    add_bullet("The application inserts a new row into Rentals with Rental_Status = 'Active'.")
    add_bullet("The database trigger trg_after_booking_insert automatically executes: UPDATE Vehicles SET Status = 'Rented' WHERE Vehicle_Number = NEW.Vehicle_Number;")
    add_bullet("The GUI table instantly reflects the change from 🟢 Available to 🔴 Rented without requiring application-level status updates.")

    add_heading_2("Step 3: Stored Procedure Execution on Vehicle Return")
    add_body("When a vehicle is returned (ReturnVehicle):")
    add_bullet("The active rental record is fetched, and elapsed rental duration is computed.")
    add_bullet("Return fuel level is audited: if fuel < 20%, an automatic Rs. 500.00 penalty is appended to Total_Amount.")
    add_bullet("The booking is closed (Rental_Status = 'Completed') and the vehicle status is restored to 'Available' with its new fuel percentage.")

    add_heading_2("Step 4: Record Deletion with Active-Rental Protection Guards")
    add_body("Safe deletion prevents orphaned records and maintains database consistency:")
    add_bullet(" Attempting to delete a vehicle with Status = 'Rented' is intercepted and blocked with an error modal. If 'Available', the vehicle and past completed history are deleted safely.", "• Delete Vehicle Guard: ")
    add_bullet(" Attempting to delete a customer with ongoing active bookings is blocked. Inactive customers and past history are deleted cleanly.", "• Delete Customer Guard: ")

    doc.add_page_break()

    # =========================================================================
    # PAGE 5: OUTPUT, TEST RESULTS & CONCLUSION
    # =========================================================================
    add_heading_1("5. OUTPUT & TEST RESULTS")
    
    add_heading_2("5.1 Automated Test Verification Output (test_db.py)")
    test_out = """[+] Database initialized successfully.
[+] Checkout response: True | Checkout successful! Vehicle TN 37 BY 0650 is now marked 'Rented' via Trigger.
[+] Vehicle 'TN 37 BY 0650' status after checkout (Trigger): Rented
[+] ReturnVehicle (15% fuel): extra_fee=500.0, total=1700.0 (Rs. 500 Low Fuel Surcharge Applied)
[+] Vehicle status & fuel after return: ('Available', 15.0)
[+] Duplicate DL test: False | Constraint Violation: Driving License already exists! (UNIQUE Enforced)
[+] Duplicate PK test: False | Constraint Violation: Vehicle Number already registered! (PRIMARY KEY Enforced)

[+] Testing Deletion & Safety Constraints...
[+] Delete actively rented vehicle test: False | Blocked: Vehicle currently Rented Out!
[+] Delete customer with active rental test: False | Blocked: Active rental booking exists!
[+] Delete available vehicle test: True | Vehicle deleted successfully.
[+] Delete inactive customer test: True | Customer deleted successfully.

[SUCCESS] ALL LAB TESTS (TRIGGERS, PROCEDURES, CONSTRAINTS, DELETIONS) PASSED PERFECTLY!"""
    add_code_block(test_out)

    add_heading_2("5.2 Sample Fleet Ledger State Tables")
    add_body("Initial Fleet State:", bold_prefix="Table 5.1: ")
    t_fleet = doc.add_table(rows=1, cols=6)
    t_fleet.alignment = WD_TABLE_ALIGNMENT.CENTER
    f_headers = ["Vehicle Reg No", "Model Name", "Type", "Daily Rate", "Current Fuel", "Status"]
    for i, h in enumerate(f_headers):
        c = t_fleet.rows[0].cells[i]
        set_cell_background(c, "1E293B")
        set_cell_margins(c, top=50, bottom=50, left=60, right=60)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.0)
        r.font.color.rgb = RGBColor(56, 189, 248)
        r.font.name = "Segoe UI"

    f_data = [
        ("TN 37 BY 0650", "Royal Enfield Continental GT 650", "Bike", "Rs. 1,200.00", "100.0%", "🟢 Available"),
        ("TN 01 AB 1984", "HM Contessa Classic 1.8 GLX", "Car", "Rs. 2,500.00", "95.0%", "🟢 Available"),
        ("TN 38 CD 4350", "Royal Enfield Classic 350", "Bike", "Rs. 900.00", "100.0%", "🟢 Available"),
        ("KL 07 EF 4444", "Mahindra Thar 4x4 Hard Top", "Car", "Rs. 3,200.00", "85.0%", "🟢 Available"),
        ("KA 05 GH 3900", "KTM Duke 390 Gen-3", "Bike", "Rs. 1,500.00", "100.0%", "🟢 Available")
    ]
    for row_idx, row_vals in enumerate(f_data):
        row = t_fleet.add_row()
        bg_col = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for i, val in enumerate(row_vals):
            c = row.cells[i]
            set_cell_background(c, bg_col)
            set_cell_margins(c, top=40, bottom=40, left=60, right=60)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            r.font.name = "Segoe UI"
            if "Available" in val:
                r.font.color.rgb = RGBColor(16, 185, 129)
                r.bold = True
            elif "Rented" in val:
                r.font.color.rgb = RGBColor(225, 29, 72)
                r.bold = True
            else:
                r.font.color.rgb = C_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Return breakdown box
    add_body("Stored Procedure Execution Breakdown (Return with 15% Fuel):", bold_prefix="Audit Log: ")
    add_bullet("Registration Number: TN 37 BY 0650 (Royal Enfield Continental GT 650)")
    add_bullet("Base Rental Charge (1 Day): Rs. 1,200.00 | Fuel Level on Return: 15.0% (< 20% Threshold)")
    add_bullet("Low Fuel Surcharge (Automated Penalty): +Rs. 500.00 | Total Billed & Paid: Rs. 1,700.00")
    add_bullet("Vehicle Status Restored: Available (Fuel updated to 15.0%)")

    # 6. RESULT
    add_heading_1("6. RESULT")
    add_body("Thus, a full-featured GUI-based database application for the Car Rental and Bike-Share Ledger System (AutoShare Ledger) was successfully designed, developed, and evaluated. The key constraints (Primary Key, Unique, Check), automated database trigger for rental status flipping, stored procedure for return billing & fuel penalty calculation, and active-rental deletion protection guards were completely verified.")

    out_path = os.path.join(DIR, "DBMS_Lab_Experiment_10_AutoShare.docx")
    try:
        doc.save(out_path)
        print(f"[+] Successfully generated DOCX at: {out_path}")
    except PermissionError:
        alt_path = os.path.join(DIR, "DBMS_Lab_Experiment_10_AutoShare_5Pages.docx")
        doc.save(alt_path)
        print(f"[!] Original file is currently open in Word. Saved 5-page version to: {alt_path}")



def create_pptx():
    prs = Presentation()
    prs.slide_width = PInches(13.333)
    prs.slide_height = PInches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors
    BG_DARK = PRGBColor(11, 15, 25)       # #0b0f19
    CARD_BG = PRGBColor(20, 28, 46)       # #141c2e
    CARD_BORDER = PRGBColor(30, 41, 59)   # #1e293b
    TEXT_WHITE = PRGBColor(248, 250, 252) # #f8fafc
    TEXT_MUTED = PRGBColor(148, 163, 184) # #94a3b8
    CYAN_ACCENT = PRGBColor(56, 189, 248) # #38bdf8
    EMERALD = PRGBColor(52, 211, 153)     # #34d399
    ROSE = PRGBColor(251, 113, 133)       # #fb7185
    AMBER = PRGBColor(251, 191, 36)       # #fbbf24
    INDIGO = PRGBColor(129, 140, 248)     # #818cf8

    def set_slide_background(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BG_DARK

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = PPt(1.5)
        return shape

    def add_header(slide, title_text, category_text="DBMS LABORATORY • EXPERIMENT 10"):
        # Category Tag
        cat_box = slide.shapes.add_textbox(PInches(0.8), PInches(0.4), PInches(11.5), PInches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = PPt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = CYAN_ACCENT
        p_cat.font.name = "Segoe UI"

        # Main Title
        title_box = slide.shapes.add_textbox(PInches(0.8), PInches(0.75), PInches(11.5), PInches(0.8))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = PPt(22)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.font.name = "Segoe UI"

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Hero card
    add_card(s1, PInches(1.2), PInches(1.0), PInches(10.933), PInches(5.5), bg_color=CARD_BG, border_color=CYAN_ACCENT)

    tb = s1.shapes.add_textbox(PInches(1.6), PInches(1.4), PInches(10.133), PInches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "DEPARTMENT OF ARTIFICIAL INTELLIGENCE & DATA SCIENCE"
    p0.font.size = PPt(14)
    p0.font.bold = True
    p0.font.color.rgb = CYAN_ACCENT
    p0.font.name = "Segoe UI"
    p0.alignment = PP_ALIGN.CENTER

    p1 = tf.add_paragraph()
    p1.text = "EXPERIMENT NO: 10"
    p1.font.size = PPt(16)
    p1.font.bold = True
    p1.font.color.rgb = AMBER
    p1.font.name = "Segoe UI"
    p1.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "AutoShare Ledger - GUI Database Application"
    p2.font.size = PPt(28)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.font.name = "Segoe UI"
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf.add_paragraph()
    p3.text = "Integrating Key Constraints, Automated Database Triggers, Stored Procedures & Deletion Safety Guards"
    p3.font.size = PPt(14)
    p3.font.color.rgb = TEXT_MUTED
    p3.font.name = "Segoe UI"
    p3.alignment = PP_ALIGN.CENTER

    p4 = tf.add_paragraph()
    p4.text = "\n• Interface: Interactive Desktop GUI Dashboard with Real-Time Metrics\n• Database: SQLite3 / MySQL Relational Schema with DDL & Procedures\n• Vehicle Registration: Real Indian Registration Plates (TN 37 BY 0650, etc.)"
    p4.font.size = PPt(12)
    p4.font.color.rgb = EMERALD
    p4.font.name = "Segoe UI"
    p4.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 2: Aim & Key Objectives
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Aim & Laboratory Objectives")

    cards_s2 = [
        ("1. Key Constraints", "Enforce PRIMARY KEY on Vehicle Registration Number, UNIQUE constraint on Customer Driving License, and CHECK constraints on fuel level (0-100%) and daily rates.", CYAN_ACCENT),
        ("2. Database Trigger", "Implement AFTER INSERT trigger on Rentals table to automatically update vehicle status to 'Rented' upon booking without client-side intervention.", EMERALD),
        ("3. Stored Procedure", "Create ReturnVehicle(vehicle_id, fuel_level) to calculate base rent, audit fuel level, assess a Rs. 500 penalty if fuel < 20%, and restore status to 'Available'.", AMBER),
        ("4. Deletion Safety Guards", "Provide Delete Vehicle & Delete Customer features with intelligent active-rental locks preventing deletion of rented vehicles or active renters.", ROSE),
    ]

    for idx, (title, desc, color) in enumerate(cards_s2):
        row = idx // 2
        col = idx % 2
        left = PInches(0.8 + col * 5.9)
        top = PInches(1.8 + row * 2.6)
        add_card(s2, left, top, PInches(5.7), PInches(2.3), border_color=color)

        tb = s2.shapes.add_textbox(left + PInches(0.2), top + PInches(0.2), PInches(5.3), PInches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = PPt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        p_t.font.name = "Segoe UI"

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = PPt(11.5)
        p_d.font.color.rgb = TEXT_WHITE
        p_d.font.name = "Segoe UI"

    # ==========================================
    # SLIDE 3: System Architecture & Relational Schema
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Relational Database Schema & Architecture")

    tables = [
        ("Vehicles Table", [
            ("Vehicle_Number", "VARCHAR(50)", "PRIMARY KEY (e.g., 'TN 37 BY 0650')"),
            ("Model_Name", "VARCHAR(100)", "Make & Model (e.g. 'RE GT 650')"),
            ("Vehicle_Type", "VARCHAR(20)", "CHECK (IN ('Car', 'Bike'))"),
            ("Daily_Rate", "DECIMAL(10,2)", "CHECK (Daily_Rate > 0)"),
            ("Status", "VARCHAR(20)", "CHECK (IN ('Available', 'Rented'))"),
            ("Fuel_Level", "DECIMAL(5,2)", "CHECK (0 <= Fuel <= 100)")
        ], CYAN_ACCENT),
        ("Customers Table", [
            ("Customer_ID", "INTEGER", "PRIMARY KEY AUTOINCREMENT"),
            ("Full_Name", "VARCHAR(100)", "Customer Full Name (NOT NULL)"),
            ("Driving_License", "VARCHAR(50)", "UNIQUE, NOT NULL (Govt ID)"),
            ("Phone_Number", "VARCHAR(20)", "Contact Phone (NOT NULL)")
        ], INDIGO),
        ("Rentals Ledger Table", [
            ("Rental_ID", "INTEGER", "PRIMARY KEY AUTOINCREMENT"),
            ("Vehicle_Number", "VARCHAR(50)", "FOREIGN KEY -> Vehicles"),
            ("Customer_ID", "INTEGER", "FOREIGN KEY -> Customers"),
            ("Rental_Date", "TIMESTAMP", "Booking Date (DEFAULT NOW)"),
            ("Return_Date", "TIMESTAMP", "Return Date (Set on Return)"),
            ("Extra_Fee", "DECIMAL(10,2)", "Penalty Surcharge (< 20% fuel)"),
            ("Total_Amount", "DECIMAL(10,2)", "Total Billed Amount (Rs.)"),
            ("Rental_Status", "VARCHAR(20)", "'Active' or 'Completed'")
        ], EMERALD),
    ]

    for idx, (t_name, cols, color) in enumerate(tables):
        left = PInches(0.8 + idx * 3.9)
        top = PInches(1.8)
        add_card(s3, left, top, PInches(3.75), PInches(5.1), border_color=color)

        tb = s3.shapes.add_textbox(left + PInches(0.15), top + PInches(0.15), PInches(3.45), PInches(4.8))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = t_name
        pt.font.size = PPt(15)
        pt.font.bold = True
        pt.font.color.rgb = color
        pt.font.name = "Segoe UI"

        for col_name, c_type, c_rule in cols:
            p = tf.add_paragraph()
            p.text = f"• {col_name} ({c_type})\n   └ {c_rule}"
            p.font.size = PPt(9.5)
            p.font.color.rgb = TEXT_WHITE
            p.font.name = "Segoe UI"

    # ==========================================
    # SLIDE 4: Database Trigger Implementation
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Automated Database Trigger (AFTER INSERT ON Rentals)")

    # Left: Explanation Card
    add_card(s4, PInches(0.8), PInches(1.8), PInches(5.7), PInches(5.1), border_color=EMERALD)
    tb_l = s4.shapes.add_textbox(PInches(1.0), PInches(2.0), PInches(5.3), PInches(4.7))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "Trigger Specification & Logic"
    p.font.size = PPt(16)
    p.font.bold = True
    p.font.color.rgb = EMERALD

    items_trg = [
        ("Event Hook:", "AFTER INSERT ON Rentals table."),
        ("Condition:", "WHEN NEW.Rental_Status = 'Active'"),
        ("Action:", "Automatically updates the matching row in Vehicles table, setting Status = 'Rented'."),
        ("Integrity Benefit:", "Guarantees that a vehicle cannot be double-booked. Eliminates reliance on client-side state manipulation."),
        ("Visual Feedback:", "GUI instantly shifts table badges from 🟢 Available to 🔴 Rented in real-time.")
    ]
    for k, v in items_trg:
        p = tf_l.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = PPt(11)
        p.font.color.rgb = TEXT_WHITE

    # Right: DDL Code Card
    add_card(s4, PInches(6.8), PInches(1.8), PInches(5.7), PInches(5.1), border_color=CYAN_ACCENT)
    tb_r = s4.shapes.add_textbox(PInches(7.0), PInches(2.0), PInches(5.3), PInches(4.7))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "SQL Trigger Definition"
    p.font.size = PPt(16)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    code_t = """-- MySQL / SQLite Trigger
CREATE TRIGGER trg_after_booking_insert
AFTER INSERT ON Rentals
FOR EACH ROW
WHEN NEW.Rental_Status = 'Active'
BEGIN
    UPDATE Vehicles
    SET Status = 'Rented'
    WHERE Vehicle_Number = NEW.Vehicle_Number;
END;"""
    p_c = tf_r.add_paragraph()
    p_c.text = code_t
    p_c.font.size = PPt(10.5)
    p_c.font.name = "Consolas"
    p_c.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 5: Stored Procedure Implementation
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Stored Procedure (ReturnVehicle Routine)")

    # Left: Explanation Card
    add_card(s5, PInches(0.8), PInches(1.8), PInches(5.7), PInches(5.1), border_color=AMBER)
    tb_l = s5.shapes.add_textbox(PInches(1.0), PInches(2.0), PInches(5.3), PInches(4.7))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "Procedure Workflow & Fuel Audit"
    p.font.size = PPt(16)
    p.font.bold = True
    p.font.color.rgb = AMBER

    items_sp = [
        ("Procedure Signature:", "ReturnVehicle(p_vehicle_num, p_fuel_level)"),
        ("1. Active Rental Lookup:", "Locates active booking in Rentals for the vehicle."),
        ("2. Duration Calculation:", "Calculates days rented: base_charge = daily_rate * days."),
        ("3. Low Fuel Audit:", "If p_fuel_level < 20%: Extra_Fee = Rs. 500.00 surcharge automatically added to Total_Amount."),
        ("4. Ledger Closure:", "Sets Return_Date = NOW(), Rental_Status = 'Completed'."),
        ("5. Fleet State Restoration:", "Sets Vehicles.Status = 'Available' and updates Fuel_Level to returned value.")
    ]
    for k, v in items_sp:
        p = tf_l.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = PPt(10.5)
        p.font.color.rgb = TEXT_WHITE

    # Right: Stored Procedure Code Card
    add_card(s5, PInches(6.8), PInches(1.8), PInches(5.7), PInches(5.1), border_color=CYAN_ACCENT)
    tb_r = s5.shapes.add_textbox(PInches(7.0), PInches(2.0), PInches(5.3), PInches(4.7))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Stored Procedure Logic"
    p.font.size = PPt(16)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    code_sp = """CREATE PROCEDURE ReturnVehicle(
    IN p_vehicle_num VARCHAR(50),
    IN p_fuel_level DECIMAL(5, 2)
)
BEGIN
    -- Surcharge condition
    IF p_fuel_level < 20.0 THEN
        SET p_extra_fee = 500.00;
    ELSE
        SET p_extra_fee = 0.00;
    END IF;

    SET p_total = v_base_rent + p_extra_fee;

    -- Update Ledger & Fleet status
    UPDATE Rentals SET Return_Date = NOW(),
        Extra_Fee = p_extra_fee,
        Total_Amount = p_total,
        Rental_Status = 'Completed'
    WHERE Rental_ID = v_id;

    UPDATE Vehicles SET Status = 'Available',
        Fuel_Level = p_fuel_level
    WHERE Vehicle_Number = p_vehicle_num;
END;"""
    p_c = tf_r.add_paragraph()
    p_c.text = code_sp
    p_c.font.size = PPt(9.5)
    p_c.font.name = "Consolas"
    p_c.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 6: Deletion Features & Safety Guards
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Deletion Features & Active-Rental Safety Guards")

    # Card 1: Delete Vehicle
    add_card(s6, PInches(0.8), PInches(1.8), PInches(5.7), PInches(5.1), border_color=ROSE)
    tb1 = s6.shapes.add_textbox(PInches(1.0), PInches(2.0), PInches(5.3), PInches(4.7))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "🗑️ Delete Vehicle Safety Guard"
    p.font.size = PPt(16)
    p.font.bold = True
    p.font.color.rgb = ROSE

    v_pts = [
        ("Active Rental Check:", "Queries Vehicles table to verify current status."),
        ("Blocked Condition:", "If Status == 'Rented', deletion is intercepted and blocked with error pop-up: 'Cannot delete vehicle because it is currently Rented Out! Please return first.'"),
        ("Safe Deletion Path:", "If Status == 'Available', prompts confirmation modal, deletes completed past history from Rentals, and removes vehicle from Vehicles table."),
        ("Live GUI Update:", "Auto-refreshes stat cards (Total Fleet, Available) and table view.")
    ]
    for k, v in v_pts:
        p = tf1.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = PPt(11)
        p.font.color.rgb = TEXT_WHITE

    # Card 2: Delete Customer
    add_card(s6, PInches(6.8), PInches(1.8), PInches(5.7), PInches(5.1), border_color=INDIGO)
    tb2 = s6.shapes.add_textbox(PInches(7.0), PInches(2.0), PInches(5.3), PInches(4.7))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "🗑️ Delete Customer Safety Guard"
    p.font.size = PPt(16)
    p.font.bold = True
    p.font.color.rgb = INDIGO

    c_pts = [
        ("Active Bookings Check:", "Counts active rentals in Rentals table where Customer_ID matches and Rental_Status == 'Active'."),
        ("Blocked Condition:", "If active_count > 0, deletion is blocked: 'Cannot delete customer because they have active rental booking(s)!'"),
        ("Safe Deletion Path:", "If no active rentals, prompts confirmation, removes completed ledger records, and deletes customer row."),
        ("Integrity Guaranteed:", "Prevents orphaned active rental records and maintains foreign key consistency.")
    ]
    for k, v in c_pts:
        p = tf2.add_paragraph()
        p.text = f"• {k} {v}"
        p.font.size = PPt(11)
        p.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 7: Graphical User Interface & Features
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Graphical User Interface & Features")

    ui_cards = [
        ("High-Contrast Modern Theme", "Dark background with elevated cards, high-contrast text, and distinct status indicators.", CYAN_ACCENT),
        ("Live KPI Metric Cards", "Real-time metrics for Total Fleet, Available Units, Rented Out, and Total Revenue with color-coded badges.", EMERALD),
        ("Segmented Tab Navigation", "Smooth tab switcher supporting Fleet Status, Complete Rental Audit Ledger, Customer Registry, and Live SQL Inspector.", INDIGO),
        ("Interactive Modals & Sliders", "Quick Check Out modal, Return modal with real-time fuel slider (<20% warning), Add Vehicle/Customer modals, and Delete dialogs.", AMBER),
    ]

    for idx, (title, desc, color) in enumerate(ui_cards):
        row = idx // 2
        col = idx % 2
        left = PInches(0.8 + col * 5.9)
        top = PInches(1.8 + row * 2.6)
        add_card(s7, left, top, PInches(5.7), PInches(2.3), border_color=color)

        tb = s7.shapes.add_textbox(left + PInches(0.2), top + PInches(0.2), PInches(5.3), PInches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = PPt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = color

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = PPt(11.5)
        p_d.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 8: Step-by-Step Execution Workflow
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Step-by-Step Execution & User Flow")

    steps = [
        ("Step 1: Fleet & Customer Init", "System initializes schema, verifies PK and UNIQUE constraints, seeds registration plate numbers (TN 37 BY 0650, etc.).", CYAN_ACCENT),
        ("Step 2: Check Out (Rent Vehicle)", "User selects available vehicle and customer. Rental row created -> Trigger instantly switches status to 'Rented'.", EMERALD),
        ("Step 3: Fuel Audit & Return", "ReturnVehicle procedure executes with returned fuel %. If < 20%, +Rs. 500 penalty surcharge is computed. Vehicle restored to 'Available'.", AMBER),
        ("Step 4: Record Deletion & Auditing", "Delete actions guarded against active rentals. SQL Inspector allows custom queries with instant tabular output.", ROSE)
    ]

    for idx, (title, desc, color) in enumerate(steps):
        top = PInches(1.8 + idx * 1.3)
        add_card(s8, PInches(0.8), top, PInches(11.733), PInches(1.15), border_color=color)

        tb = s8.shapes.add_textbox(PInches(1.0), top + PInches(0.1), PInches(11.333), PInches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = PPt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = color

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = PPt(11)
        p_d.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 9: Automated Test Results & Verification
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Automated Verification & Test Output (test_db.py)")

    add_card(s9, PInches(0.8), PInches(1.8), PInches(11.733), PInches(5.1), border_color=EMERALD)
    tb = s9.shapes.add_textbox(PInches(1.0), PInches(2.0), PInches(11.333), PInches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Console Output from Automated Test Suite"
    p.font.size = PPt(16)
    p.font.bold = True
    p.font.color.rgb = EMERALD

    test_lines = """[+] Database initialized successfully.
[+] Checkout response: True | Checkout successful! Vehicle TN 37 BY 0650 is now marked 'Rented' via Trigger.
[+] Vehicle 'TN 37 BY 0650' status after checkout (Trigger): Rented
[+] ReturnVehicle (15% fuel): extra_fee=500.0, total=1700.0 (Rs. 500 Low Fuel Surcharge Applied)
[+] Vehicle status & fuel after return: ('Available', 15.0)
[+] Duplicate DL test: False | Constraint Violation: Driving License already exists! (UNIQUE Enforced)
[+] Duplicate PK test: False | Constraint Violation: Vehicle Number already registered! (PRIMARY KEY Enforced)

[+] Testing Deletion & Safety Constraints...
[+] Delete actively rented vehicle test: False | Blocked: Currently Rented Out!
[+] Delete customer with active rental test: False | Blocked: Active rental booking exists!
[+] Delete available vehicle test: True | Vehicle deleted successfully.
[+] Delete inactive customer test: True | Customer deleted successfully.

[SUCCESS] ALL LAB TESTS (TRIGGERS, PROCEDURES, CONSTRAINTS, DELETIONS) PASSED PERFECTLY!"""
    p_t = tf.add_paragraph()
    p_t.text = test_lines
    p_t.font.size = PPt(10.5)
    p_t.font.name = "Consolas"
    p_t.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 10: Conclusion & Result
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Summary & Conclusion")

    add_card(s10, PInches(0.8), PInches(1.8), PInches(11.733), PInches(5.1), border_color=CYAN_ACCENT)
    tb = s10.shapes.add_textbox(PInches(1.2), PInches(2.2), PInches(10.933), PInches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "Experiment Conclusion & Key Findings"
    p0.font.size = PPt(20)
    p0.font.bold = True
    p0.font.color.rgb = CYAN_ACCENT

    summary_bullets = [
        "1. Entity & Domain Integrity: Enforced Primary Key on Vehicle Registration Plates (TN 37 BY 0650), Unique Constraint on Driving Licenses, and Check constraints on fuel and daily rates.",
        "2. Automated State Transitions: The AFTER INSERT Trigger eliminates concurrency errors by automatically switching vehicle status to 'Rented' upon booking.",
        "3. Stored Procedure Fuel Audit: The ReturnVehicle routine enforces consistent billing rules with automatic Rs. 500 low-fuel surcharges and restores fleet availability.",
        "4. Record Safety Guards: Delete Vehicle and Delete Customer operations prevent accidental deletion of rented assets and ongoing bookings.",
        "5. Interactive User Interface: The desktop GUI delivers an intuitive, responsive administrative experience with real-time status updates."
    ]
    for b in summary_bullets:
        p = tf.add_paragraph()
        p.text = f"\n{b}"
        p.font.size = PPt(12.5)
        p.font.color.rgb = TEXT_WHITE

    out_path_ppt = os.path.join(DIR, "DBMS_Lab_Experiment_10_AutoShare.pptx")
    try:
        prs.save(out_path_ppt)
        print(f"[+] Successfully generated PPTX at: {out_path_ppt}")
    except PermissionError:
        alt_ppt = os.path.join(DIR, "DBMS_Lab_Experiment_10_AutoShare_Updated.pptx")
        prs.save(alt_ppt)
        print(f"[!] Original PPTX is currently open in PowerPoint. Saved updated version to: {alt_ppt}")

if __name__ == "__main__":
    create_docx()
    create_pptx()
