import sys
import database

def run_tests():
    database.init_database()
    print("[+] Database initialized successfully.")

    # 1. Test Checkout (Trigger test) with Registration Plate TN 37 BY 0650
    res, msg = database.checkout_vehicle('TN 37 BY 0650', 1)
    print(f"[+] Checkout response: {res} | {msg}")
    assert res is True

    # Verify Trigger changed status to 'Rented'
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT Status FROM Vehicles WHERE Vehicle_Number = 'TN 37 BY 0650';")
    status = cur.fetchone()[0]
    print(f"[+] Vehicle 'TN 37 BY 0650' status after checkout (Trigger): {status}")
    assert status == 'Rented', "Trigger failed to update status to Rented"

    # 2. Test Stored Procedure ReturnVehicle with low fuel (<20%)
    res, msg, extra_fee, total = database.ReturnVehicle('TN 37 BY 0650', 15.0)
    print(f"[+] ReturnVehicle (15% fuel): extra_fee={extra_fee}, total={total}")
    assert extra_fee == 500.0, f"Expected penalty 500.0, got {extra_fee}"

    cur.execute("SELECT Status, Fuel_Level FROM Vehicles WHERE Vehicle_Number = 'TN 37 BY 0650';")
    row = cur.fetchone()
    print(f"[+] Vehicle status & fuel after return: {row}")
    assert row[0] == 'Available'
    assert row[1] == 15.0

    # 3. Test UNIQUE Constraint on Driving License
    res, cid, msg = database.add_customer('Duplicate Person', 'DL-TN-01-2023-0004123', '9999999999')
    print(f"[+] Duplicate DL test: {res} | {msg}")
    assert res is False
    assert "UNIQUE constraint" in msg or "already exists" in msg

    # 4. Test PRIMARY KEY Constraint on Vehicle_Number
    res, msg = database.add_vehicle('TN 37 BY 0650', 'Royal Enfield Continental GT 650', 'Bike', 1200.0)
    print(f"[+] Duplicate PK test: {res} | {msg}")
    assert res is False
    assert "PRIMARY KEY" in msg or "already registered" in msg

    # 5. Test Delete Vehicle & Customer with Safety Checks
    print("\n[+] Testing Deletion & Safety Constraints...")
    # Register temporary vehicle & customer
    res, msg = database.add_vehicle('TN 99 ZZ 9999', 'Test Deletion Bike', 'Bike', 500.0)
    assert res is True
    res, temp_cid, msg = database.add_customer('Temp User For Delete', 'DL-TEMP-99-9999-9999', '9888877777')
    assert res is True

    # Checkout temp vehicle
    res, msg = database.checkout_vehicle('TN 99 ZZ 9999', temp_cid)
    assert res is True

    # Attempt to delete while Rented (Must Fail)
    res, msg = database.delete_vehicle('TN 99 ZZ 9999')
    print(f"[+] Delete actively rented vehicle test: {res} | {msg}")
    assert res is False, "Should not allow deleting actively rented vehicle"

    # Attempt to delete customer with active rental (Must Fail)
    res, msg = database.delete_customer(temp_cid)
    print(f"[+] Delete customer with active rental test: {res} | {msg}")
    assert res is False, "Should not allow deleting customer with active rental"

    # Return the vehicle
    res, msg, extra_fee, total = database.ReturnVehicle('TN 99 ZZ 9999', 50.0)
    assert res is True

    # Now delete vehicle (Must Succeed)
    res, msg = database.delete_vehicle('TN 99 ZZ 9999')
    print(f"[+] Delete available vehicle test: {res} | {msg}")
    assert res is True

    # Now delete customer (Must Succeed)
    res, msg = database.delete_customer(temp_cid)
    print(f"[+] Delete inactive customer test: {res} | {msg}")
    assert res is True

    conn.close()
    print("\n[SUCCESS] ALL LAB TESTS (TRIGGERS, PROCEDURES, CONSTRAINTS, DELETIONS) PASSED PERFECTLY!")

if __name__ == "__main__":
    run_tests()
