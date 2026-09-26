import datetime
import math
import heapq

class Vehicle:
    def __init__(self, plate_number, slot_id):
        self.plate_number = plate_number.upper()
        self.slot_id = slot_id
        self.entry_time = datetime.datetime.now()

    def __str__(self):
        return f"Vehicle [{self.plate_number}] at Slot {self.slot_id}"

class TransactionRecord:
    def __init__(self, plate_number, entry_time, exit_time, fee):
        self.plate_number = plate_number
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.fee = fee

    def print_receipt(self):
        duration = self.exit_time - self.entry_time
        minutes = duration.total_seconds() / 60
        print("\n" + "="*40)
        print("            PARKING RECEIPT")
        print("="*40)
        print(f" Plate Number : {self.plate_number}")
        print(f" Entry Time   : {self.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Exit Time    : {self.exit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Duration     : {minutes:.2f} mins")
        print(f" Total Paid   : ${self.fee:.2f}")
        print("="*40 + "\n")

class FeeCalculator:
    def __init__(self, hourly_rate=5.0):
        self.hourly_rate = hourly_rate

    def calculate(self, entry_time, exit_time):
        duration = exit_time - entry_time
        seconds = duration.total_seconds()
        # 1 second acts as 1 hour for testing
        hours = seconds 
        if hours <= 0:
            return 0.0
        return math.ceil(hours) * self.hourly_rate

class SlotManager:
    def __init__(self, capacity):
        self.capacity = capacity
        self.available_slots = list(range(1, capacity + 1))
        heapq.heapify(self.available_slots)

    def has_space(self):
        return len(self.available_slots) > 0

    def assign_slot(self):
        if not self.has_space():
            return None
        return heapq.heappop(self.available_slots)

    def free_slot(self, slot_id):
        if slot_id not in self.available_slots:
            heapq.heappush(self.available_slots, slot_id)

class ParkingDatabase:
    def __init__(self):
        self.active_cars = {}
        self.history = []

    def park_car(self, vehicle):
        self.active_cars[vehicle.plate_number] = vehicle

    def find_car(self, plate_number):
        return self.active_cars.get(plate_number.upper())

    def remove_car(self, plate_number):
        pn = plate_number.upper()
        if pn in self.active_cars:
            del self.active_cars[pn]

    def log_transaction(self, record):
        self.history.append(record)

class SystemController:
    def __init__(self, capacity, hourly_rate):
        self.slots = SlotManager(capacity)
        self.billing = FeeCalculator(hourly_rate)
        self.db = ParkingDatabase()
        self.capacity = capacity

    def get_free_count(self):
        return len(self.slots.available_slots)

    def car_entry(self, plate_number):
        plate = plate_number.strip().upper()
        if not plate:
            print("Error: Plate number cannot be empty.")
            return False
        if self.db.find_car(plate):
            print("Error: Vehicle is already inside.")
            return False
        if not self.slots.has_space():
            print("Sorry, the parking lot is full.")
            return False

        slot = self.slots.assign_slot()
        car = Vehicle(plate, slot)
        self.db.park_car(car)
        print(f"Success: Vehicle {plate} parked at slot {slot}.")
        return True

    def car_exit(self, plate_number):
        plate = plate_number.strip().upper()
        car = self.db.find_car(plate)
        if not car:
            print("Error: Vehicle registration not found.")
            return False

        exit_time = datetime.datetime.now()
        fee = self.billing.calculate(car.entry_time, exit_time)
        
        self.slots.free_slot(car.slot_id)
        self.db.remove_car(plate)

        receipt = TransactionRecord(car.plate_number, car.entry_time, exit_time, fee)
        self.db.log_transaction(receipt)
        receipt.print_receipt()
        return True

class ReportGenerator:
    @staticmethod
    def show_status(system):
        print("\n" + "-"*30)
        print("        SYSTEM STATUS")
        print("-"*30)
        print(f" Active Vehicles : {len(system.db.active_cars)}")
        print(f" Available Slots : {system.get_free_count()}")
        total_revenue = sum(r.fee for r in system.db.history)
        print(f" Total Earnings  : ${total_revenue:.2f}")
        print("-"*30)

def main():
    parking_lot = SystemController(capacity=10, hourly_rate=3.50)
    
    while True:
        print("\n=== PARKING SYSTEM MENU ===")
        print("1. View Available Slots")
        print("2. Vehicle Entry")
        print("3. Vehicle Exit")
        print("4. Management Report")
        print("5. Exit Program")
        
        choice = input("Enter option (1-5): ").strip()
        
        if choice == '1':
            print(f"\nAvailable slots: {parking_lot.get_free_count()}")
        elif choice == '2':
            plate = input("Enter plate number: ")
            parking_lot.car_entry(plate)
        elif choice == '3':
            plate = input("Enter plate number: ")
            parking_lot.car_exit(plate)
        elif choice == '4':
            ReportGenerator.show_status(parking_lot)
        elif choice == '5':
            print("Exiting application...")
            break
        else:
            print("Invalid choice, please select 1-5.")

if __name__ == "__main__":
    main()
