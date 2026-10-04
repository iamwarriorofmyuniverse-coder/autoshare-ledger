"""
Database management module for Car Rental / Bike-Share Ledger.
Implements Key Constraints, Triggers, and Stored Procedures.
"""

import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "rental_ledger.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. VEHICLES TABLE (Primary Key, CHECK Constraint)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Vehicles (
        Vehicle_Number VARCHAR(50) PRIMARY KEY,
        Model_Name VARCHAR(100) NOT NULL,
        Vehicle_Type VARCHAR(20) NOT NULL CHECK(Vehicle_Type IN ('Car', 'Bike')),
        Daily_Rate DECIMAL(10, 2) NOT NULL CHECK(Daily_Rate > 0),
        Status VARCHAR(20) NOT NULL DEFAULT 'Available' CHECK(Status IN ('Available', 'Rented', 'Maintenance')),
        Fuel_Level DECIMAL(5, 2) NOT NULL DEFAULT 100.0 CHECK(Fuel_Level >= 0 AND Fuel_Level <= 100)
    );
    """)

    # 2. CUSTOMERS TABLE (Primary Key, UNIQUE Driving License constraint)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Customers (
        Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Full_Name VARCHAR(100) NOT NULL,
        Driving_License_Number VARCHAR(50) NOT NULL UNIQUE,
        Phone_Number VARCHAR(20) NOT NULL
    );
    """)

    # 3. RENTALS / BOOKINGS TABLE (Foreign Keys, Transaction Ledger)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Rentals (
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
        Rental_Status VARCHAR(20) NOT NULL DEFAULT 'Active' CHECK(Rental_Status IN ('Active', 'Completed', 'Cancelled')),
        FOREIGN KEY (Vehicle_Number) REFERENCES Vehicles(Vehicle_Number) ON UPDATE CASCADE,
        FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID) ON UPDATE CASCADE
    );
    """)

    # 4. TRIGGER: Automatically switch Vehicle Status to 'Rented' when a rental row is created
    cursor.execute("DROP TRIGGER IF EXISTS trg_after_booking_insert;")
    cursor.execute("""
    CREATE TRIGGER trg_after_booking_insert
    AFTER INSERT ON Rentals
    WHEN NEW.Rental_Status = 'Active'
    BEGIN
        UPDATE Vehicles
        SET Status = 'Rented'
        WHERE Vehicle_Number = NEW.Vehicle_Number;
    END;
    """)

    # Populate default starter data if empty
    cursor.execute("SELECT COUNT(*) FROM Vehicles;")
    if cursor.fetchone()[0] == 0:
        sample_vehicles = [
            ('TN 37 BY 0650', 'Royal Enfield Continental GT 650', 'Bike', 1200.0, 'Available', 100.0),
            ('TN 01 AB 1984', 'HM Contessa Classic 1.8 GLX', 'Car', 2500.0, 'Available', 95.0),
            ('TN 38 CD 4350', 'Royal Enfield Classic 350 Stealth Black', 'Bike', 900.0, 'Available', 100.0),
            ('KL 07 EF 4444', 'Mahindra Thar 4x4 Hard Top Diesel', 'Car', 3200.0, 'Available', 85.0),
            ('KA 05 GH 3900', 'KTM Duke 390 Gen-3', 'Bike', 1500.0, 'Available', 100.0),
            ('TN 66 JK 2800', 'Tata Harrier Dark Edition', 'Car', 2800.0, 'Available', 90.0),
        ]
        cursor.executemany("""
            INSERT INTO Vehicles (Vehicle_Number, Model_Name, Vehicle_Type, Daily_Rate, Status, Fuel_Level)
            VALUES (?, ?, ?, ?, ?, ?);
        """, sample_vehicles)

        sample_customers = [
            ('Rajesh Kumar', 'DL-TN-01-2023-0004123', '+91 9876543210'),
            ('Priya Sundaram', 'DL-TN-37-2022-0008745', '+91 9843212345'),
            ('Vignesh Anand', 'DL-KA-05-2021-0001928', '+91 9789012345'),
        ]
        cursor.executemany("""
            INSERT INTO Customers (Full_Name, Driving_License_Number, Phone_Number)
            VALUES (?, ?, ?);
        """, sample_customers)

    conn.commit()
    conn.close()

# Stored Procedure implementation for Python / SQLite
def ReturnVehicle(vehicle_number: str, return_fuel_level: float, low_fuel_threshold: float = 20.0, low_fuel_penalty: float = 500.0):
    """
    Stored Procedure Routine:
    ReturnVehicle(vehicle_id, fuel_level)
    - Finds the active rental for the vehicle.
    - If return_fuel_level < 20%, assesses extra penalty fee (e.g. ₹500).
    - Updates rental log (return timestamp, fuel, fees, status='Completed').
    - Updates vehicle status back to 'Available' and refreshes its fuel level.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check active rental
        cursor.execute("""
            SELECT Rental_ID, Customer_ID, Rental_Date, Daily_Rate, Start_Fuel_Level
            FROM Rentals
            WHERE Vehicle_Number = ? AND Rental_Status = 'Active'
            ORDER BY Rental_ID DESC LIMIT 1;
        """, (vehicle_number,))
        active_rental = cursor.fetchone()

        if not active_rental:
            conn.close()
            return False, "No active rental booking found for vehicle " + vehicle_number, 0.0, 0.0

        rental_id, customer_id, rental_date_str, daily_rate, start_fuel = active_rental

        # Calculate duration / fee
        rental_time = datetime.fromisoformat(rental_date_str.replace(" ", "T")) if "T" in rental_date_str or " " in rental_date_str else datetime.now()
        now = datetime.now()
        
        # Calculate days (at least 1 day rental charge)
        days = max(1, (now - rental_time).days + (1 if (now - rental_time).seconds > 3600 else 0))
        base_rent = float(daily_rate) * days

        # Evaluate fuel condition: Extra fee if fuel level drops below 20%
        extra_fee = low_fuel_penalty if return_fuel_level < low_fuel_threshold else 0.0
        total_amount = base_rent + extra_fee

        # 1. Update Rental row
        cursor.execute("""
            UPDATE Rentals
            SET Return_Date = CURRENT_TIMESTAMP,
                Return_Fuel_Level = ?,
                Extra_Fee = ?,
                Total_Amount = ?,
                Rental_Status = 'Completed'
            WHERE Rental_ID = ?;
        """, (return_fuel_level, extra_fee, total_amount, rental_id))

        # 2. Update Vehicle back to Available and update its current fuel level
        cursor.execute("""
            UPDATE Vehicles
            SET Status = 'Available',
                Fuel_Level = ?
            WHERE Vehicle_Number = ?;
        """, (return_fuel_level, vehicle_number))

        conn.commit()
        conn.close()

        msg = f"Vehicle {vehicle_number} successfully returned!\n" \
              f"• Base Rental ({days} day(s)): ₹{base_rent:.2f}\n" \
              f"• Return Fuel Level: {return_fuel_level}%\n"
        if extra_fee > 0:
            msg += f"⚠️ LOW FUEL SURCHARGE APPLIED (<20%): +₹{extra_fee:.2f}\n"
        msg += f"• Total Billed Amount: ₹{total_amount:.2f}"

        return True, msg, extra_fee, total_amount

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e), 0.0, 0.0

def checkout_vehicle(vehicle_number: str, customer_id: int):
    """
    Creates a new active rental row.
    The Trigger automatically updates the vehicle status to 'Rented'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get vehicle rate and fuel level
        cursor.execute("SELECT Daily_Rate, Fuel_Level, Status FROM Vehicles WHERE Vehicle_Number = ?;", (vehicle_number,))
        veh = cursor.fetchone()
        if not veh:
            conn.close()
            return False, "Vehicle not found."
        
        daily_rate, fuel_level, status = veh
        if status != 'Available':
            conn.close()
            return False, f"Cannot checkout: Vehicle {vehicle_number} is currently '{status}'."

        # Insert booking row -> Trigger fires!
        cursor.execute("""
            INSERT INTO Rentals (Vehicle_Number, Customer_ID, Start_Fuel_Level, Daily_Rate, Rental_Status)
            VALUES (?, ?, ?, ?, 'Active');
        """, (vehicle_number, customer_id, fuel_level, daily_rate))

        conn.commit()
        conn.close()
        return True, f"Checkout successful! Vehicle {vehicle_number} is now marked 'Rented' via Trigger."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def add_customer(full_name: str, driving_license: str, phone: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Customers (Full_Name, Driving_License_Number, Phone_Number)
            VALUES (?, ?, ?);
        """, (full_name.strip(), driving_license.strip().upper(), phone.strip()))
        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()
        return True, customer_id, "Customer added successfully."
    except sqlite3.IntegrityError as e:
        conn.close()
        if "UNIQUE constraint failed: Customers.Driving_License_Number" in str(e):
            return False, None, f"Constraint Violation: Driving License '{driving_license}' already exists! Driving license must be UNIQUE."
        return False, None, str(e)
    except Exception as e:
        conn.close()
        return False, None, str(e)

def add_vehicle(vehicle_number: str, model_name: str, vehicle_type: str, daily_rate: float, fuel_level: float = 100.0):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Vehicles (Vehicle_Number, Model_Name, Vehicle_Type, Daily_Rate, Status, Fuel_Level)
            VALUES (?, ?, ?, ?, 'Available', ?);
        """, (vehicle_number.strip().upper(), model_name.strip(), vehicle_type, daily_rate, fuel_level))
        conn.commit()
        conn.close()
        return True, f"Vehicle {vehicle_number} added successfully."
    except sqlite3.IntegrityError as e:
        conn.close()
        if "UNIQUE constraint failed: Vehicles.Vehicle_Number" in str(e) or "PRIMARY KEY" in str(e):
            return False, f"Constraint Violation: Vehicle Number '{vehicle_number}' is already registered as PRIMARY KEY."
        return False, str(e)
    except Exception as e:
        conn.close()
        return False, str(e)

def delete_vehicle(vehicle_number: str):
    """
    Deletes a vehicle from the database.
    Prevents deletion if the vehicle is currently in 'Rented' status.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Status, Model_Name FROM Vehicles WHERE Vehicle_Number = ?;", (vehicle_number,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False, f"Vehicle '{vehicle_number}' not found in database."

        status, model_name = row
        if status == 'Rented':
            conn.close()
            return False, f"Cannot delete vehicle '{vehicle_number}' ({model_name}) because it is currently Rented Out!\nPlease process its return before deleting."

        # Delete any associated past completed rental history, then the vehicle
        cursor.execute("DELETE FROM Rentals WHERE Vehicle_Number = ?;", (vehicle_number,))
        cursor.execute("DELETE FROM Vehicles WHERE Vehicle_Number = ?;", (vehicle_number,))
        conn.commit()
        conn.close()
        return True, f"Vehicle '{vehicle_number}' ({model_name}) deleted successfully."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Error deleting vehicle: {str(e)}"

def delete_customer(customer_id: int):
    """
    Deletes a customer from the database.
    Prevents deletion if the customer has an ongoing active rental booking.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Full_Name, Driving_License_Number FROM Customers WHERE Customer_ID = ?;", (customer_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False, f"Customer with ID {customer_id} not found."

        full_name, license_num = row
        cursor.execute("SELECT COUNT(*) FROM Rentals WHERE Customer_ID = ? AND Rental_Status = 'Active';", (customer_id,))
        active_count = cursor.fetchone()[0]
        if active_count > 0:
            conn.close()
            return False, f"Cannot delete customer '{full_name}' because they have an ongoing active rental booking!\nPlease complete the rental return first."

        # Delete associated past completed rentals, then customer
        cursor.execute("DELETE FROM Rentals WHERE Customer_ID = ?;", (customer_id,))
        cursor.execute("DELETE FROM Customers WHERE Customer_ID = ?;", (customer_id,))
        conn.commit()
        conn.close()
        return True, f"Customer '{full_name}' (DL: {license_num}) deleted successfully."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Error deleting customer: {str(e)}"

