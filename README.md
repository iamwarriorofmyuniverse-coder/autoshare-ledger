# 🚗 AutoShare Ledger - Vehicle Rental & Bike-Share Database System
### DBMS Laboratory - GUI Database Application

---

## 📌 System Specifications & Features

| Component | Requirement | Implementation Detail |
| :--- | :--- | :--- |
| **Key Constraints** | Entity Integrity & Validation | `Vehicle_Number` as **PRIMARY KEY**, `Driving_License_Number` as **UNIQUE**, `CHECK` constraints on Fuel (0-100) and Rates. |
| **Data Manipulation** | Relational Schemas & Integrity | Tables for `Vehicles`, `Customers`, and `Rentals` with foreign key relations and transactional integrity. |
| **Database Triggers** | Automated State Transitions | **AFTER INSERT Trigger** (`trg_after_booking_insert`) to auto-switch vehicle status to `'Rented'` upon booking. |
| **Stored Procedures** | Routine Business Computation | **Stored Procedure** (`ReturnVehicle`) to process return, audit fuel, assess `< 20%` penalty fee, and restore `'Available'` status. |

---

## 🛠️ Project Structure

- `app.py`: Desktop GUI application with interactive status tables, live metric cards, checkout/return modals, and SQL Inspector.
- `neu_theme.py`: Custom UI components rendering styled cards, status indicators, and buttons.
- `database.py`: Database connection, table initialization, trigger definitions, and stored procedure logic.
- `schema_mysql.sql`: MySQL script with complete DDL, `TRIGGER`, and `STORED PROCEDURE` definitions.
- `test_db.py`: Automated validation script verifying constraint enforcement, trigger execution, and procedure logic.

---

## 🚀 How to Run the Application

### Option A: Web Browser Link (Local / Network)
```bash
# 1-Click Launch (starts server & opens browser)
run_web_link.bat

# OR run manually:
python web_app.py
```
Open **`http://127.0.0.1:8000`** in any web browser (Chrome, Edge, Firefox) or on any device on the same local Wi-Fi.

### Option B: Desktop GUI (Tkinter)
```bash
python app.py
```

---

## 💡 Key Features & Workflow

1. **Visual Table & Live Status Flags**:
   - Lists vehicles with official registration numbers (`TN 37 BY 0650`, `TN 01 AB 1984`, `TN 38 CD 4350`, `KL 07 EF 4444`, `KA 05 GH 3900`) and distinct Model Names with color-coded status badges (🟢 Available vs 🔴 Rented).
   - Double-clicking any vehicle row automatically opens the appropriate action (Check Out or Return).
2. **Check Out (Trigger Demonstration)**:
   - Selecting a vehicle and customer creates a booking row in `Rentals`.
   - The database trigger immediately switches the vehicle's status to `'Rented'`.
3. **Return Vehicle (Stored Procedure Demonstration)**:
   - Interactive slider / preset buttons to input returned fuel level (0–100%).
   - If fuel `< 20%`, Stored Procedure applies a ₹500 Low Fuel Surcharge and updates total billing.
   - Restores vehicle status to `'Available'` and logs the return in the audit ledger.
4. **Deletion & Active Rental Safety Guards**:
   - **Delete Vehicle**: Select any vehicle in the Fleet tab and click `🗑️ Delete Vehicle`. If the vehicle is actively rented out, deletion is safely blocked until returned.
   - **Delete Customer**: Select any customer in the Customers tab and click `🗑️ Delete Customer`. If the customer has ongoing active rentals, deletion is safely prevented.
5. **Constraint Violation Handling**:
   - Entering duplicate Vehicle Numbers or Driving Licenses triggers clean constraint violation alerts.
