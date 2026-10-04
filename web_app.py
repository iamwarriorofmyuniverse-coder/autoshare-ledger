"""
AutoShare Ledger - Web Application
Built with FastAPI (already installed on system) & Modern Responsive Web UI.
Connects directly to database.py (Triggers, Stored Procedures, Constraints & Deletion Guards).
"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import database

# Initialize database
database.init_database()

app = FastAPI(title="AutoShare Ledger Web API")

# -------------------------------------------------------------
# PYDANTIC SCHEMAS
# -------------------------------------------------------------
class CheckoutRequest(BaseModel):
    vehicle_number: str
    customer_id: int

class ReturnRequest(BaseModel):
    vehicle_number: str
    return_fuel_level: float

class AddVehicleRequest(BaseModel):
    vehicle_number: str
    model_name: str
    vehicle_type: str
    daily_rate: float
    fuel_level: float = 100.0

class AddCustomerRequest(BaseModel):
    full_name: str
    driving_license_number: str
    phone_number: str

class DeleteVehicleRequest(BaseModel):
    vehicle_number: str

class DeleteCustomerRequest(BaseModel):
    customer_id: int

class SqlQueryRequest(BaseModel):
    query: str

# -------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------
@app.get("/api/stats")
def get_stats():
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Vehicles;")
    total_veh = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Vehicles WHERE Status = 'Available';")
    avail_veh = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Vehicles WHERE Status = 'Rented';")
    rented_veh = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(Total_Amount), 0) FROM Rentals;")
    total_rev = cur.fetchone()[0]
    conn.close()
    return {
        "total_vehicles": total_veh,
        "available_vehicles": avail_veh,
        "rented_vehicles": rented_veh,
        "total_revenue": total_rev
    }

@app.get("/api/vehicles")
def get_vehicles(filter_type: str = "All"):
    conn = database.get_connection()
    cur = conn.cursor()
    if filter_type == "All":
        cur.execute("SELECT Vehicle_Number, Model_Name, Vehicle_Type, Daily_Rate, Fuel_Level, Status FROM Vehicles ORDER BY Vehicle_Number;")
    elif filter_type in ("Available", "Rented"):
        cur.execute("SELECT Vehicle_Number, Model_Name, Vehicle_Type, Daily_Rate, Fuel_Level, Status FROM Vehicles WHERE Status = ? ORDER BY Vehicle_Number;", (filter_type,))
    elif filter_type in ("Car", "Bike"):
        cur.execute("SELECT Vehicle_Number, Model_Name, Vehicle_Type, Daily_Rate, Fuel_Level, Status FROM Vehicles WHERE Vehicle_Type = ? ORDER BY Vehicle_Number;", (filter_type,))
    else:
        cur.execute("SELECT Vehicle_Number, Model_Name, Vehicle_Type, Daily_Rate, Fuel_Level, Status FROM Vehicles ORDER BY Vehicle_Number;")
    
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "vehicle_number": r[0],
            "model_name": r[1],
            "vehicle_type": r[2],
            "daily_rate": r[3],
            "fuel_level": r[4],
            "status": r[5]
        }
        for r in rows
    ]

@app.get("/api/customers")
def get_customers():
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.Customer_ID, c.Full_Name, c.Driving_License_Number, c.Phone_Number,
               COUNT(CASE WHEN r.Rental_Status = 'Active' THEN 1 END) as active_count
        FROM Customers c
        LEFT JOIN Rentals r ON c.Customer_ID = r.Customer_ID
        GROUP BY c.Customer_ID, c.Full_Name, c.Driving_License_Number, c.Phone_Number
        ORDER BY c.Customer_ID;
    """)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "customer_id": r[0],
            "full_name": r[1],
            "driving_license_number": r[2],
            "phone_number": r[3],
            "active_rentals": r[4]
        }
        for r in rows
    ]

@app.get("/api/rentals")
def get_rentals():
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.Rental_ID, r.Vehicle_Number, c.Full_Name, c.Driving_License_Number,
               r.Rental_Date, r.Return_Date, r.Start_Fuel_Level, r.Return_Fuel_Level,
               r.Extra_Fee, r.Total_Amount, r.Rental_Status
        FROM Rentals r
        JOIN Customers c ON r.Customer_ID = c.Customer_ID
        ORDER BY r.Rental_ID DESC;
    """)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "rental_id": r[0],
            "vehicle_number": r[1],
            "customer_name": r[2],
            "driving_license": r[3],
            "rental_date": r[4],
            "return_date": r[5] if r[5] else "Active",
            "start_fuel": r[6],
            "return_fuel": r[7] if r[7] is not None else "-",
            "extra_fee": r[8],
            "total_amount": r[9],
            "status": r[10]
        }
        for r in rows
    ]

@app.post("/api/checkout")
def checkout(req: CheckoutRequest):
    ok, msg = database.checkout_vehicle(req.vehicle_number, req.customer_id)
    return {"success": ok, "message": msg}

@app.post("/api/return")
def return_veh(req: ReturnRequest):
    ok, msg, extra_fee, total = database.ReturnVehicle(req.vehicle_number, req.return_fuel_level)
    return {
        "success": ok,
        "message": msg,
        "extra_fee": extra_fee,
        "total_amount": total
    }

@app.post("/api/add-vehicle")
def add_veh(req: AddVehicleRequest):
    ok, msg = database.add_vehicle(req.vehicle_number, req.model_name, req.vehicle_type, req.daily_rate, req.fuel_level)
    return {"success": ok, "message": msg}

@app.post("/api/add-customer")
def add_cust(req: AddCustomerRequest):
    ok, cust_id, msg = database.add_customer(req.full_name, req.driving_license_number, req.phone_number)
    return {"success": ok, "customer_id": cust_id, "message": msg}

@app.post("/api/delete-vehicle")
def del_veh(req: DeleteVehicleRequest):
    ok, msg = database.delete_vehicle(req.vehicle_number)
    return {"success": ok, "message": msg}

@app.post("/api/delete-customer")
def del_cust(req: DeleteCustomerRequest):
    ok, msg = database.delete_customer(req.customer_id)
    return {"success": ok, "message": msg}

@app.post("/api/execute-sql")
def execute_sql(req: SqlQueryRequest):
    q = req.query.strip()
    if not q:
        return {"success": False, "message": "Query cannot be empty."}
    
    conn = database.get_connection()
    cur = conn.cursor()
    try:
        cur.execute(q)
        if q.upper().startswith(("SELECT", "PRAGMA", "EXPLAIN")):
            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            conn.close()
            return {"success": True, "columns": columns, "rows": rows, "count": len(rows)}
        else:
            conn.commit()
            affected = cur.rowcount
            conn.close()
            return {"success": True, "message": f"Query executed successfully. Rows affected: {affected}"}
    except Exception as e:
        conn.close()
        return {"success": False, "message": str(e)}

# -------------------------------------------------------------
# FRONTEND HTML INTERFACE
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoShare Ledger - Web Database Application</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0b0f19; color: #f8fafc; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .card-surface { background: #141c2e; border: 1px solid #1e293b; }
        .card-glow-blue:hover { border-color: #38bdf8; box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); }
        .card-glow-emerald:hover { border-color: #10b981; box-shadow: 0 0 15px rgba(16, 185, 129, 0.2); }
        .card-glow-rose:hover { border-color: #f43f5e; box-shadow: 0 0 15px rgba(244, 63, 94, 0.2); }
        .card-glow-amber:hover { border-color: #fbbf24; box-shadow: 0 0 15px rgba(251, 191, 36, 0.2); }
        .tab-active { background: #1e293b; color: #38bdf8; border-bottom: 2px solid #38bdf8; }
        .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #0b0f19; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
    </style>
</head>
<body class="min-h-screen flex flex-col p-4 md:p-8">

    <!-- Top Header -->
    <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
            <div class="flex items-center gap-2">
                <span class="text-2xl">⚡</span>
                <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight text-sky-400">AutoShare Ledger</h1>
                <span class="text-xs bg-sky-950 text-sky-400 border border-sky-800 px-2.5 py-0.5 rounded-full font-semibold">Web Live</span>
            </div>
            <p class="text-sm text-slate-400 mt-1">Car Rental & Bike-Share Database Ledger • DBMS Laboratory</p>
        </div>
        <div class="flex items-center gap-3">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Database Active & Connected
            </span>
            <button onclick="refreshAll()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition flex items-center gap-1.5">
                ⟳ Refresh
            </button>
        </div>
    </header>

    <!-- KPI Metric Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 my-6">
        <div class="card-surface card-glow-blue rounded-xl p-4 transition">
            <div class="flex items-center justify-between text-slate-400 text-xs font-semibold">
                <span>TOTAL FLEET</span>
                <span class="text-lg">🚘</span>
            </div>
            <div id="stat-total" class="text-2xl md:text-3xl font-bold text-sky-400 mt-2">0</div>
            <div class="text-[11px] text-slate-500 mt-1">Cars & Bikes Registered</div>
        </div>
        <div class="card-surface card-glow-emerald rounded-xl p-4 transition">
            <div class="flex items-center justify-between text-slate-400 text-xs font-semibold">
                <span>AVAILABLE</span>
                <span class="text-lg">🟢</span>
            </div>
            <div id="stat-avail" class="text-2xl md:text-3xl font-bold text-emerald-400 mt-2">0</div>
            <div class="text-[11px] text-slate-500 mt-1">Ready for Checkout</div>
        </div>
        <div class="card-surface card-glow-rose rounded-xl p-4 transition">
            <div class="flex items-center justify-between text-slate-400 text-xs font-semibold">
                <span>RENTED OUT</span>
                <span class="text-lg">🔴</span>
            </div>
            <div id="stat-rented" class="text-2xl md:text-3xl font-bold text-rose-400 mt-2">0</div>
            <div class="text-[11px] text-slate-500 mt-1">Flipped via Trigger</div>
        </div>
        <div class="card-surface card-glow-amber rounded-xl p-4 transition">
            <div class="flex items-center justify-between text-slate-400 text-xs font-semibold">
                <span>TOTAL REVENUE</span>
                <span class="text-lg">💰</span>
            </div>
            <div id="stat-rev" class="text-2xl md:text-3xl font-bold text-amber-400 mt-2">₹0.00</div>
            <div class="text-[11px] text-slate-500 mt-1">Rentals + Low Fuel Fees</div>
        </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex items-center gap-2 border-b border-slate-800 mb-6 overflow-x-auto custom-scrollbar">
        <button onclick="switchTab('fleet')" id="tab-fleet" class="tab-active px-4 py-2.5 text-sm font-semibold transition rounded-t-lg flex items-center gap-2 whitespace-nowrap">
            🚗 Fleet Status
        </button>
        <button onclick="switchTab('customers')" id="tab-customers" class="text-slate-400 hover:text-slate-200 px-4 py-2.5 text-sm font-semibold transition rounded-t-lg flex items-center gap-2 whitespace-nowrap">
            👤 Customer Registry
        </button>
        <button onclick="switchTab('history')" id="tab-history" class="text-slate-400 hover:text-slate-200 px-4 py-2.5 text-sm font-semibold transition rounded-t-lg flex items-center gap-2 whitespace-nowrap">
            📜 Rental Audit Ledger
        </button>
        <button onclick="switchTab('sql')" id="tab-sql" class="text-slate-400 hover:text-slate-200 px-4 py-2.5 text-sm font-semibold transition rounded-t-lg flex items-center gap-2 whitespace-nowrap">
            🎓 SQL Query Inspector
        </button>
    </div>

    <!-- TAB 1: FLEET STATUS -->
    <div id="view-fleet" class="space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <div class="flex items-center gap-2">
                <span class="text-xs font-semibold text-slate-400">Filter:</span>
                <select id="fleet-filter" onchange="loadVehicles()" class="bg-slate-800 text-slate-200 text-xs font-medium border border-slate-700 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500">
                    <option value="All">All Vehicles</option>
                    <option value="Available">Available</option>
                    <option value="Rented">Rented Out</option>
                    <option value="Car">Cars</option>
                    <option value="Bike">Bikes</option>
                </select>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
                <button onclick="openModal('modal-checkout')" class="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow-lg shadow-emerald-900/30 transition flex items-center gap-1">
                    🚀 Rent Vehicle (Trigger)
                </button>
                <button onclick="openModal('modal-return')" class="px-3.5 py-1.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg shadow-lg shadow-sky-900/30 transition flex items-center gap-1">
                    🔄 Return (Procedure)
                </button>
                <button onclick="openModal('modal-add-vehicle')" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-lg shadow-indigo-900/30 transition flex items-center gap-1">
                    ➕ Add Vehicle
                </button>
            </div>
        </div>

        <div class="card-surface rounded-xl overflow-hidden shadow-xl border border-slate-800">
            <div class="overflow-x-auto custom-scrollbar">
                <table class="w-full text-left border-collapse text-sm">
                    <thead>
                        <tr class="bg-slate-900/90 text-sky-400 text-xs font-bold border-b border-slate-800">
                            <th class="p-3.5">Registration No (PK)</th>
                            <th class="p-3.5">Model Name</th>
                            <th class="p-3.5 text-center">Type</th>
                            <th class="p-3.5 text-right">Daily Rate</th>
                            <th class="p-3.5 text-center">Fuel %</th>
                            <th class="p-3.5 text-center">Status</th>
                            <th class="p-3.5 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="fleet-table-body" class="divide-y divide-slate-800/60 font-normal">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 2: CUSTOMERS REGISTRY -->
    <div id="view-customers" class="hidden space-y-4">
        <div class="flex items-center justify-between bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <div class="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <span>👤 Customer Registry</span>
                <span class="text-slate-500">• Driving License is Enforced UNIQUE</span>
            </div>
            <button onclick="openModal('modal-add-customer')" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-lg shadow-indigo-900/30 transition flex items-center gap-1">
                ➕ Add Customer
            </button>
        </div>

        <div class="card-surface rounded-xl overflow-hidden shadow-xl border border-slate-800">
            <div class="overflow-x-auto custom-scrollbar">
                <table class="w-full text-left border-collapse text-sm">
                    <thead>
                        <tr class="bg-slate-900/90 text-sky-400 text-xs font-bold border-b border-slate-800">
                            <th class="p-3.5 text-center">ID (PK)</th>
                            <th class="p-3.5">Full Name</th>
                            <th class="p-3.5">Driving License (UNIQUE)</th>
                            <th class="p-3.5 text-center">Phone Number</th>
                            <th class="p-3.5 text-center">Active Bookings</th>
                            <th class="p-3.5 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="cust-table-body" class="divide-y divide-slate-800/60">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 3: RENTAL AUDIT LEDGER -->
    <div id="view-history" class="hidden space-y-4">
        <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-800 text-xs font-medium text-slate-400">
            📜 Complete Rental Audit Ledger • Tracks Fuel %, Penalties, and Procedure Status
        </div>
        <div class="card-surface rounded-xl overflow-hidden shadow-xl border border-slate-800">
            <div class="overflow-x-auto custom-scrollbar">
                <table class="w-full text-left border-collapse text-xs md:text-sm">
                    <thead>
                        <tr class="bg-slate-900/90 text-sky-400 text-xs font-bold border-b border-slate-800">
                            <th class="p-3 text-center">ID</th>
                            <th class="p-3">Vehicle No</th>
                            <th class="p-3">Customer</th>
                            <th class="p-3">Rental Date</th>
                            <th class="p-3">Return Date</th>
                            <th class="p-3 text-center">Start Fuel</th>
                            <th class="p-3 text-center">Return Fuel</th>
                            <th class="p-3 text-right">Low Fuel Fee</th>
                            <th class="p-3 text-right">Total Amount</th>
                            <th class="p-3 text-center">Status</th>
                        </tr>
                    </thead>
                    <tbody id="history-table-body" class="divide-y divide-slate-800/60">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 4: SQL QUERY INSPECTOR -->
    <div id="view-sql" class="hidden space-y-4">
        <div class="card-surface rounded-xl p-4 border border-slate-800 space-y-3">
            <div class="flex items-center justify-between">
                <label class="text-xs font-bold text-sky-400 uppercase tracking-wider">Execute Custom SQL Query</label>
                <span class="text-[11px] text-slate-500">Supports SELECT, INSERT, UPDATE, DELETE & Procedures</span>
            </div>
            <textarea id="sql-query-input" rows="3" class="w-full bg-slate-950 text-emerald-400 border border-slate-800 rounded-lg p-3 text-xs md:text-sm mono focus:outline-none focus:border-sky-500" placeholder="SELECT * FROM Vehicles WHERE Status = 'Available';"></textarea>
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <button onclick="setQuery('SELECT * FROM Vehicles;')" class="text-[11px] bg-slate-800 text-slate-300 px-2.5 py-1 rounded hover:bg-slate-700">Vehicles</button>
                    <button onclick="setQuery('SELECT * FROM Customers;')" class="text-[11px] bg-slate-800 text-slate-300 px-2.5 py-1 rounded hover:bg-slate-700">Customers</button>
                    <button onclick="setQuery('SELECT * FROM Rentals ORDER BY Rental_ID DESC;')" class="text-[11px] bg-slate-800 text-slate-300 px-2.5 py-1 rounded hover:bg-slate-700">Rentals</button>
                </div>
                <button onclick="runSqlQuery()" class="px-4 py-1.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold rounded-lg transition shadow-lg shadow-sky-900/30">
                    ▶ Execute Query
                </button>
            </div>
        </div>

        <div id="sql-result-container" class="card-surface rounded-xl overflow-hidden border border-slate-800 hidden">
            <div class="p-3 bg-slate-900 text-xs font-bold text-slate-400 border-b border-slate-800 flex items-center justify-between">
                <span>Query Result Output</span>
                <span id="sql-row-count" class="text-sky-400">0 rows</span>
            </div>
            <div class="overflow-x-auto custom-scrollbar p-2">
                <div id="sql-result-table"></div>
            </div>
        </div>
    </div>

    <!-- ==================== MODALS ==================== -->

    <!-- Modal 1: Check Out (Rent) -->
    <div id="modal-checkout" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="card-surface border border-slate-700 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 class="text-lg font-bold text-sky-400">🚀 Check Out Vehicle (Trigger)</h3>
                <button onclick="closeModal('modal-checkout')" class="text-slate-400 hover:text-white">&times;</button>
            </div>
            <p class="text-xs text-slate-400">Creates booking in <span class="mono text-sky-300">Rentals</span>. Trigger automatically updates status to <span class="text-rose-400 font-semibold">'Rented'</span>.</p>
            <div class="space-y-3">
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Select Available Vehicle:</label>
                    <select id="checkout-veh-select" class="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-lg p-2.5 text-xs focus:outline-none focus:border-sky-500"></select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Select Customer (Unique License):</label>
                    <select id="checkout-cust-select" class="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-lg p-2.5 text-xs focus:outline-none focus:border-sky-500"></select>
                </div>
            </div>
            <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                <button onclick="closeModal('modal-checkout')" class="px-3 py-1.5 bg-slate-800 text-slate-300 rounded-lg text-xs hover:bg-slate-700">Cancel</button>
                <button onclick="doCheckout()" class="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs shadow-lg shadow-emerald-900/30">Confirm Rent</button>
            </div>
        </div>
    </div>

    <!-- Modal 2: Return Vehicle (Stored Procedure) -->
    <div id="modal-return" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="card-surface border border-slate-700 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 class="text-lg font-bold text-sky-400">🔄 Return Vehicle (Stored Procedure)</h3>
                <button onclick="closeModal('modal-return')" class="text-slate-400 hover:text-white">&times;</button>
            </div>
            <p class="text-xs text-slate-400">Executes <span class="mono text-sky-300">ReturnVehicle(vehicle, fuel)</span>. If fuel &lt; 20%, an automatic <span class="text-amber-400 font-bold">₹500 Surcharge</span> is added.</p>
            <div class="space-y-3">
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Select Rented Vehicle:</label>
                    <select id="return-veh-select" class="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-lg p-2.5 text-xs focus:outline-none focus:border-sky-500"></select>
                </div>
                <div>
                    <div class="flex justify-between items-center mb-1">
                        <label class="text-xs font-semibold text-slate-300">Return Fuel Level (%):</label>
                        <span id="fuel-slider-val" class="text-xs font-bold text-sky-400">80.0%</span>
                    </div>
                    <input type="range" id="return-fuel-slider" min="0" max="100" value="80" step="1" oninput="updateFuelVal(this.value)" class="w-full accent-sky-400">
                    <div id="fuel-warning" class="text-[11px] font-semibold text-amber-400 mt-1 hidden">
                        ⚠️ Fuel is below 20%! A ₹500 Low Fuel Fee will be applied.
                    </div>
                </div>
            </div>
            <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                <button onclick="closeModal('modal-return')" class="px-3 py-1.5 bg-slate-800 text-slate-300 rounded-lg text-xs hover:bg-slate-700">Cancel</button>
                <button onclick="doReturn()" class="px-4 py-1.5 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-lg text-xs shadow-lg shadow-sky-900/30">Process Return</button>
            </div>
        </div>
    </div>

    <!-- Modal 3: Add Vehicle -->
    <div id="modal-add-vehicle" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="card-surface border border-slate-700 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 class="text-lg font-bold text-sky-400">➕ Register New Vehicle</h3>
                <button onclick="closeModal('modal-add-vehicle')" class="text-slate-400 hover:text-white">&times;</button>
            </div>
            <div class="space-y-3">
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Vehicle Plate No (Primary Key):</label>
                    <input type="text" id="add-v-num" placeholder="e.g. TN 45 AZ 1234" class="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-lg p-2.5 text-xs uppercase focus:outline-none focus:border-sky-500">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Model Name:</label>
                    <input type="text" id="add-v-model" placeholder="e.g. Hyundai Creta SX" class="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-lg p-2.5 text-xs focus:outline-none focus:border-sky-500">
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 mb-1">Type:</label>
                        <select id="add-v-type" class="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-lg p-2.5 text-xs focus:outline-none focus:border-sky-500">
                            <option value="Car">Car</option>
                            <option value="Bike">Bike</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 mb-1">Daily Rate (₹):</label>
                        <input type="number" id="add-v-rate" value="1500" class="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-lg p-2.5 text-xs focus:outline-none focus:border-sky-500">
                    </div>
                </div>
            </div>
            <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                <button onclick="closeModal('modal-add-vehicle')" class="px-3 py-1.5 bg-slate-800 text-slate-300 rounded-lg text-xs hover:bg-slate-700">Cancel</button>
                <button onclick="doAddVehicle()" class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg text-xs">Save Vehicle</button>
            </div>
        </div>
    </div>

    <!-- Modal 4: Add Customer -->
    <div id="modal-add-customer" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center hidden p-4">
        <div class="card-surface border border-slate-700 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 class="text-lg font-bold text-sky-400">👤 Register Customer</h3>
                <button onclick="closeModal('modal-add-customer')" class="text-slate-400 hover:text-white">&times;</button>
            </div>
            <div class="space-y-3">
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Full Name:</label>
                    <input type="text" id="add-c-name" placeholder="e.g. Ramesh Krishnan" class="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-lg p-2.5 text-xs focus:outline-none focus:border-sky-500">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Driving License (UNIQUE):</label>
                    <input type="text" id="add-c-dl" placeholder="e.g. DL-TN-02-2023-0005544" class="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-lg p-2.5 text-xs uppercase focus:outline-none focus:border-sky-500">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Phone Number:</label>
                    <input type="text" id="add-c-phone" placeholder="e.g. +91 9876543210" class="w-full bg-slate-950 text-slate-200 border border-slate-800 rounded-lg p-2.5 text-xs focus:outline-none focus:border-sky-500">
                </div>
            </div>
            <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                <button onclick="closeModal('modal-add-customer')" class="px-3 py-1.5 bg-slate-800 text-slate-300 rounded-lg text-xs hover:bg-slate-700">Cancel</button>
                <button onclick="doAddCustomer()" class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg text-xs">Save Customer</button>
            </div>
        </div>
    </div>

    <!-- JavaScript Application Logic -->
    <script>
        function switchTab(tabId) {
            ['fleet', 'customers', 'history', 'sql'].forEach(t => {
                document.getElementById('view-' + t).classList.add('hidden');
                document.getElementById('tab-' + t).className = 'text-slate-400 hover:text-slate-200 px-4 py-2.5 text-sm font-semibold transition rounded-t-lg flex items-center gap-2 whitespace-nowrap';
            });
            document.getElementById('view-' + tabId).classList.remove('hidden');
            document.getElementById('tab-' + tabId).className = 'tab-active px-4 py-2.5 text-sm font-semibold transition rounded-t-lg flex items-center gap-2 whitespace-nowrap';
            
            if (tabId === 'fleet') loadVehicles();
            if (tabId === 'customers') loadCustomers();
            if (tabId === 'history') loadHistory();
        }

        function openModal(id) {
            document.getElementById(id).classList.remove('hidden');
            if (id === 'modal-checkout') loadCheckoutDropdowns();
            if (id === 'modal-return') loadReturnDropdowns();
        }

        function closeModal(id) {
            document.getElementById(id).classList.add('hidden');
        }

        function updateFuelVal(val) {
            document.getElementById('fuel-slider-val').innerText = parseFloat(val).toFixed(1) + '%';
            if (parseFloat(val) < 20.0) {
                document.getElementById('fuel-warning').classList.remove('hidden');
            } else {
                document.getElementById('fuel-warning').classList.add('hidden');
            }
        }

        async function loadStats() {
            const res = await fetch('/api/stats');
            const data = await res.json();
            document.getElementById('stat-total').innerText = data.total_vehicles;
            document.getElementById('stat-avail').innerText = data.available_vehicles;
            document.getElementById('stat-rented').innerText = data.rented_vehicles;
            document.getElementById('stat-rev').innerText = '₹' + data.total_revenue.toLocaleString('en-IN', {minimumFractionDigits: 2});
        }

        async function loadVehicles() {
            const filter = document.getElementById('fleet-filter').value;
            const res = await fetch('/api/vehicles?filter_type=' + filter);
            const data = await res.json();
            const tbody = document.getElementById('fleet-table-body');
            tbody.innerHTML = '';
            
            data.forEach(v => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/40 transition';
                const isAvail = v.status === 'Available';
                const badge = isAvail 
                    ? '<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">🟢 Available</span>'
                    : '<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-950 text-rose-400 border border-rose-800">🔴 Rented</span>';
                
                tr.innerHTML = `
                    <td class="p-3.5 font-bold text-slate-100 mono">${v.vehicle_number}</td>
                    <td class="p-3.5 text-slate-300">${v.model_name}</td>
                    <td class="p-3.5 text-center text-slate-400 text-xs">${v.vehicle_type}</td>
                    <td class="p-3.5 text-right font-semibold text-slate-200">₹${v.daily_rate.toFixed(2)}</td>
                    <td class="p-3.5 text-center text-xs text-slate-300 mono">${v.fuel_level.toFixed(1)}%</td>
                    <td class="p-3.5 text-center">${badge}</td>
                    <td class="p-3.5 text-center">
                        <button onclick="deleteVehicle('${v.vehicle_number}', '${v.status}')" class="px-2.5 py-1 text-xs text-rose-400 hover:text-white hover:bg-rose-600/30 border border-rose-900 rounded transition">
                            🗑️ Delete
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            loadStats();
        }

        async function loadCustomers() {
            const res = await fetch('/api/customers');
            const data = await res.json();
            const tbody = document.getElementById('cust-table-body');
            tbody.innerHTML = '';
            data.forEach(c => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/40 transition';
                tr.innerHTML = `
                    <td class="p-3.5 text-center mono text-sky-400 font-bold">${c.customer_id}</td>
                    <td class="p-3.5 font-semibold text-slate-200">${c.full_name}</td>
                    <td class="p-3.5 mono text-xs text-slate-300">${c.driving_license_number}</td>
                    <td class="p-3.5 text-center text-xs text-slate-400">${c.phone_number}</td>
                    <td class="p-3.5 text-center font-bold ${c.active_rentals > 0 ? 'text-amber-400' : 'text-slate-400'}">${c.active_rentals}</td>
                    <td class="p-3.5 text-center">
                        <button onclick="deleteCustomer(${c.customer_id}, '${c.full_name}', ${c.active_rentals})" class="px-2.5 py-1 text-xs text-rose-400 hover:text-white hover:bg-rose-600/30 border border-rose-900 rounded transition">
                            🗑️ Delete
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function loadHistory() {
            const res = await fetch('/api/rentals');
            const data = await res.json();
            const tbody = document.getElementById('history-table-body');
            tbody.innerHTML = '';
            data.forEach(r => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/40 transition';
                const feeBadge = r.extra_fee > 0 
                    ? `<span class="text-rose-400 font-bold">₹${r.extra_fee.toFixed(2)}</span>`
                    : '<span class="text-slate-500">₹0.00</span>';
                
                tr.innerHTML = `
                    <td class="p-3 text-center mono text-slate-400">${r.rental_id}</td>
                    <td class="p-3 mono font-bold text-slate-200">${r.vehicle_number}</td>
                    <td class="p-3 text-slate-300">${r.customer_name}</td>
                    <td class="p-3 text-xs text-slate-400">${r.rental_date}</td>
                    <td class="p-3 text-xs text-slate-400">${r.return_date}</td>
                    <td class="p-3 text-center text-xs text-slate-300 mono">${r.start_fuel.toFixed(1)}%</td>
                    <td class="p-3 text-center text-xs text-slate-300 mono">${r.return_fuel !== '-' ? parseFloat(r.return_fuel).toFixed(1) + '%' : '-'}</td>
                    <td class="p-3 text-right text-xs">${feeBadge}</td>
                    <td class="p-3 text-right font-bold text-emerald-400">₹${r.total_amount.toFixed(2)}</td>
                    <td class="p-3 text-center">
                        <span class="px-2 py-0.5 text-[11px] rounded ${r.status === 'Active' ? 'bg-sky-950 text-sky-400 border border-sky-800' : 'bg-slate-800 text-slate-300'}">${r.status}</span>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function loadCheckoutDropdowns() {
            const resV = await fetch('/api/vehicles?filter_type=Available');
            const dataV = await resV.json();
            const selV = document.getElementById('checkout-veh-select');
            selV.innerHTML = '';
            dataV.forEach(v => {
                const opt = document.createElement('option');
                opt.value = v.vehicle_number;
                opt.innerText = `${v.vehicle_number} - ${v.model_name} (₹${v.daily_rate}/day)`;
                selV.appendChild(opt);
            });

            const resC = await fetch('/api/customers');
            const dataC = await resC.json();
            const selC = document.getElementById('checkout-cust-select');
            selC.innerHTML = '';
            dataC.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.customer_id;
                opt.innerText = `${c.full_name} (DL: ${c.driving_license_number})`;
                selC.appendChild(opt);
            });
        }

        async function loadReturnDropdowns() {
            const resV = await fetch('/api/vehicles?filter_type=Rented');
            const dataV = await resV.json();
            const selV = document.getElementById('return-veh-select');
            selV.innerHTML = '';
            dataV.forEach(v => {
                const opt = document.createElement('option');
                opt.value = v.vehicle_number;
                opt.innerText = `${v.vehicle_number} - ${v.model_name}`;
                selV.appendChild(opt);
            });
        }

        async function doCheckout() {
            const v = document.getElementById('checkout-veh-select').value;
            const c = parseInt(document.getElementById('checkout-cust-select').value);
            if (!v || !c) return alert('Please select vehicle and customer.');

            const res = await fetch('/api/checkout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({vehicle_number: v, customer_id: c})
            });
            const data = await res.json();
            alert(data.message);
            if (data.success) {
                closeModal('modal-checkout');
                refreshAll();
            }
        }

        async function doReturn() {
            const v = document.getElementById('return-veh-select').value;
            const f = parseFloat(document.getElementById('return-fuel-slider').value);
            if (!v) return alert('No rented vehicle selected.');

            const res = await fetch('/api/return', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({vehicle_number: v, return_fuel_level: f})
            });
            const data = await res.json();
            alert(data.message);
            if (data.success) {
                closeModal('modal-return');
                refreshAll();
            }
        }

        async function doAddVehicle() {
            const num = document.getElementById('add-v-num').value.trim();
            const model = document.getElementById('add-v-model').value.trim();
            const type = document.getElementById('add-v-type').value;
            const rate = parseFloat(document.getElementById('add-v-rate').value);

            if (!num || !model || isNaN(rate) || rate <= 0) return alert('Invalid inputs.');
            const res = await fetch('/api/add-vehicle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({vehicle_number: num, model_name: model, vehicle_type: type, daily_rate: rate})
            });
            const data = await res.json();
            alert(data.message);
            if (data.success) {
                closeModal('modal-add-vehicle');
                refreshAll();
            }
        }

        async function doAddCustomer() {
            const name = document.getElementById('add-c-name').value.trim();
            const dl = document.getElementById('add-c-dl').value.trim();
            const phone = document.getElementById('add-c-phone').value.trim();

            if (!name || !dl || !phone) return alert('All customer fields required.');
            const res = await fetch('/api/add-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({full_name: name, driving_license_number: dl, phone_number: phone})
            });
            const data = await res.json();
            alert(data.message);
            if (data.success) {
                closeModal('modal-add-customer');
                loadCustomers();
            }
        }

        async function deleteVehicle(vNum, status) {
            if (status === 'Rented') {
                return alert("Cannot delete vehicle '" + vNum + "' because it is currently Rented Out! Please process return first.");
            }
            if (!confirm("Permanently delete vehicle " + vNum + " and past records?")) return;
            const res = await fetch('/api/delete-vehicle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({vehicle_number: vNum})
            });
            const data = await res.json();
            alert(data.message);
            refreshAll();
        }

        async function deleteCustomer(cId, name, activeCount) {
            if (activeCount > 0) {
                return alert("Cannot delete customer '" + name + "' because they have active rental bookings!");
            }
            if (!confirm("Permanently delete customer " + name + " (ID: " + cId + ")?")) return;
            const res = await fetch('/api/delete-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({customer_id: cId})
            });
            const data = await res.json();
            alert(data.message);
            loadCustomers();
        }

        function setQuery(q) {
            document.getElementById('sql-query-input').value = q;
        }

        async function runSqlQuery() {
            const q = document.getElementById('sql-query-input').value;
            const res = await fetch('/api/execute-sql', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: q})
            });
            const data = await res.json();
            const outBox = document.getElementById('sql-result-container');
            const outTable = document.getElementById('sql-result-table');
            outBox.classList.remove('hidden');

            if (!data.success) {
                outTable.innerHTML = `<div class="p-4 text-rose-400 font-bold">Error: ${data.message}</div>`;
                document.getElementById('sql-row-count').innerText = '0 rows';
                return;
            }

            if (data.columns && data.rows) {
                document.getElementById('sql-row-count').innerText = data.count + ' rows';
                let html = '<table class="w-full text-left text-xs border-collapse"><thead><tr class="bg-slate-800 text-sky-400">';
                data.columns.forEach(col => html += `<th class="p-2.5 border border-slate-700">${col}</th>`);
                html += '</tr></thead><tbody>';
                data.rows.forEach(r => {
                    html += '<tr class="hover:bg-slate-800/50 border-b border-slate-800/80">';
                    r.forEach(val => html += `<td class="p-2.5 text-slate-300 mono">${val !== null ? val : 'NULL'}</td>`);
                    html += '</tr>';
                });
                html += '</tbody></table>';
                outTable.innerHTML = html;
            } else {
                document.getElementById('sql-row-count').innerText = '1 execution';
                outTable.innerHTML = `<div class="p-4 text-emerald-400 font-bold">${data.message}</div>`;
            }
        }

        function refreshAll() {
            loadStats();
            loadVehicles();
            loadCustomers();
            loadHistory();
        }

        // Initial Load
        refreshAll();
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("[+] Starting AutoShare Ledger Web Server...")
    print("[+] Access Local URL: http://127.0.0.1:8000")
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=False)
