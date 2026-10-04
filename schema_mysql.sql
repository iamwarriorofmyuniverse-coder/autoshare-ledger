-- ==========================================================
-- DBMS LABORATORY
-- Project: Car Rental / Bike-Share Ledger Database
-- Key Constraints, Integrity, Triggers, and Stored Procedures
-- ==========================================================

CREATE DATABASE IF NOT EXISTS vehicle_rental_db;
USE vehicle_rental_db;

-- ----------------------------------------------------------
-- 1. VEHICLES TABLE (Primary Key & Check Constraints)
-- ----------------------------------------------------------
DROP TABLE IF EXISTS Rentals;
DROP TABLE IF EXISTS Customers;
DROP TABLE IF EXISTS Vehicles;

CREATE TABLE Vehicles (
    Vehicle_Number VARCHAR(50) NOT NULL,
    Model_Name VARCHAR(100) NOT NULL,
    Vehicle_Type ENUM('Car', 'Bike') NOT NULL,
    Daily_Rate DECIMAL(10, 2) NOT NULL CHECK (Daily_Rate > 0),
    Status ENUM('Available', 'Rented', 'Maintenance') NOT NULL DEFAULT 'Available',
    Fuel_Level DECIMAL(5, 2) NOT NULL DEFAULT 100.0 CHECK (Fuel_Level >= 0 AND Fuel_Level <= 100),
    CONSTRAINT pk_vehicles PRIMARY KEY (Vehicle_Number)
);

-- ----------------------------------------------------------
-- 2. CUSTOMERS TABLE (Primary Key & Unique License)
-- ----------------------------------------------------------
CREATE TABLE Customers (
    Customer_ID INT AUTO_INCREMENT,
    Full_Name VARCHAR(100) NOT NULL,
    Driving_License_Number VARCHAR(50) NOT NULL,
    Phone_Number VARCHAR(20) NOT NULL,
    CONSTRAINT pk_customers PRIMARY KEY (Customer_ID),
    CONSTRAINT uq_driving_license UNIQUE (Driving_License_Number)
);

-- ----------------------------------------------------------
-- 3. RENTALS LEDGER TABLE (Foreign Keys & Default Values)
-- ----------------------------------------------------------
CREATE TABLE Rentals (
    Rental_ID INT AUTO_INCREMENT,
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
    CONSTRAINT pk_rentals PRIMARY KEY (Rental_ID),
    CONSTRAINT fk_rentals_vehicle FOREIGN KEY (Vehicle_Number) REFERENCES Vehicles(Vehicle_Number) ON UPDATE CASCADE,
    CONSTRAINT fk_rentals_customer FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID) ON UPDATE CASCADE
);

-- ----------------------------------------------------------
-- 4. THE TRIGGER (AFTER INSERT Trigger on Bookings)
-- Automatically switches Vehicle availability flag to 'Rented'
-- the second a booking row is created.
-- ----------------------------------------------------------
DELIMITER $$

CREATE TRIGGER trg_after_booking_insert
AFTER INSERT ON Rentals
FOR EACH ROW
BEGIN
    IF NEW.Rental_Status = 'Active' THEN
        UPDATE Vehicles
        SET Status = 'Rented'
        WHERE Vehicle_Number = NEW.Vehicle_Number;
    END IF;
END$$

DELIMITER ;

-- ----------------------------------------------------------
-- 5. THE STORED PROCEDURE (ReturnVehicle Routine)
-- ReturnVehicle(vehicle_id, fuel_level)
-- Updates rental log, flags vehicle as 'Available', and logs
-- an extra fee if fuel level drops below 20%.
-- ----------------------------------------------------------
DELIMITER $$

CREATE PROCEDURE ReturnVehicle(
    IN p_vehicle_num VARCHAR(50),
    IN p_fuel_level DECIMAL(5, 2),
    OUT p_extra_fee DECIMAL(10, 2),
    OUT p_total_amount DECIMAL(10, 2),
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_rental_id INT;
    DECLARE v_daily_rate DECIMAL(10, 2);
    DECLARE v_rental_date DATETIME;
    DECLARE v_days_rented INT;
    DECLARE v_base_charge DECIMAL(10, 2);

    -- Find active rental for this vehicle
    SELECT Rental_ID, Daily_Rate, Rental_Date
    INTO v_rental_id, v_daily_rate, v_rental_date
    FROM Rentals
    WHERE Vehicle_Number = p_vehicle_num AND Rental_Status = 'Active'
    ORDER BY Rental_ID DESC LIMIT 1;

    IF v_rental_id IS NULL THEN
        SET p_extra_fee = 0.0;
        SET p_total_amount = 0.0;
        SET p_message = CONCAT('Error: No active rental found for ', p_vehicle_num);
    ELSE
        -- Calculate rented duration in days (minimum 1 day)
        SET v_days_rented = GREATEST(1, TIMESTAMPDIFF(DAY, v_rental_date, NOW()));
        SET v_base_charge = v_daily_rate * v_days_rented;

        -- Fuel below 20% incurs low fuel penalty fee (500)
        IF p_fuel_level < 20.0 THEN
            SET p_extra_fee = 500.00;
        ELSE
            SET p_extra_fee = 0.00;
        END IF;

        SET p_total_amount = v_base_charge + p_extra_fee;

        -- 1. Update Rental row
        UPDATE Rentals
        SET Return_Date = NOW(),
            Return_Fuel_Level = p_fuel_level,
            Extra_Fee = p_extra_fee,
            Total_Amount = p_total_amount,
            Rental_Status = 'Completed'
        WHERE Rental_ID = v_rental_id;

        -- 2. Switch vehicle status back to 'Available' and record current fuel
        UPDATE Vehicles
        SET Status = 'Available',
            Fuel_Level = p_fuel_level
        WHERE Vehicle_Number = p_vehicle_num;

        SET p_message = CONCAT('Success: Vehicle ', p_vehicle_num, ' returned. Total: ₹', p_total_amount);
    END IF;
END$$

DELIMITER ;

-- ----------------------------------------------------------
-- 6. STORED PROCEDURES FOR SAFE DELETION (Active-Rental Guards)
-- ----------------------------------------------------------
DELIMITER $$

CREATE PROCEDURE DeleteVehicle(
    IN p_vehicle_num VARCHAR(50),
    OUT p_success INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_status VARCHAR(20);
    
    SELECT Status INTO v_status FROM Vehicles WHERE Vehicle_Number = p_vehicle_num;
    
    IF v_status IS NULL THEN
        SET p_success = 0;
        SET p_message = CONCAT('Error: Vehicle ', p_vehicle_num, ' does not exist.');
    ELSEIF v_status = 'Rented' THEN
        SET p_success = 0;
        SET p_message = CONCAT('Error: Cannot delete vehicle ', p_vehicle_num, ' because it is currently Rented Out!');
    ELSE
        DELETE FROM Rentals WHERE Vehicle_Number = p_vehicle_num;
        DELETE FROM Vehicles WHERE Vehicle_Number = p_vehicle_num;
        SET p_success = 1;
        SET p_message = CONCAT('Success: Vehicle ', p_vehicle_num, ' and historical records deleted.');
    END IF;
END$$

CREATE PROCEDURE DeleteCustomer(
    IN p_customer_id INT,
    OUT p_success INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_active_count INT;
    DECLARE v_name VARCHAR(100);
    
    SELECT Full_Name INTO v_name FROM Customers WHERE Customer_ID = p_customer_id;
    
    IF v_name IS NULL THEN
        SET p_success = 0;
        SET p_message = CONCAT('Error: Customer ID ', p_customer_id, ' does not exist.');
    ELSE
        SELECT COUNT(*) INTO v_active_count FROM Rentals 
        WHERE Customer_ID = p_customer_id AND Rental_Status = 'Active';
        
        IF v_active_count > 0 THEN
            SET p_success = 0;
            SET p_message = CONCAT('Error: Cannot delete customer ', v_name, ' due to active rental bookings!');
        ELSE
            DELETE FROM Rentals WHERE Customer_ID = p_customer_id;
            DELETE FROM Customers WHERE Customer_ID = p_customer_id;
            SET p_success = 1;
            SET p_message = CONCAT('Success: Customer ', v_name, ' deleted.');
        END IF;
    END IF;
END$$

DELIMITER ;

-- ----------------------------------------------------------
-- 7. SAMPLE SEED DATA
-- ----------------------------------------------------------
INSERT INTO Vehicles (Vehicle_Number, Model_Name, Vehicle_Type, Daily_Rate, Status, Fuel_Level) VALUES
('TN 37 BY 0650', 'Royal Enfield Continental GT 650', 'Bike', 1200.00, 'Available', 100.00),
('TN 01 AB 1984', 'HM Contessa Classic 1.8 GLX', 'Car', 2500.00, 'Available', 95.00),
('TN 38 CD 4350', 'Royal Enfield Classic 350 Stealth Black', 'Bike', 900.00, 'Available', 100.00),
('KL 07 EF 4444', 'Mahindra Thar 4x4 Hard Top Diesel', 'Car', 3200.00, 'Available', 85.00),
('KA 05 GH 3900', 'KTM Duke 390 Gen-3', 'Bike', 1500.00, 'Available', 100.00);

INSERT INTO Customers (Full_Name, Driving_License_Number, Phone_Number) VALUES
('Rajesh Kumar', 'DL-TN-01-2023-0004123', '+91 9876543210'),
('Priya Sundaram', 'DL-TN-37-2022-0008745', '+91 9843212345'),
('Vignesh Anand', 'DL-KA-05-2021-0001928', '+91 9789012345');
