
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import os
import math

# ==========================================
# PARKING LOT MANAGEMENT SYSTEM
# ==========================================

FILE_NAME = "parking_lot_dataset.csv"
TOTAL_SLOTS = 10
CAR_RATE = 20
BIKE_RATE = 10


# ==========================================
# LOAD OR CREATE DATASET
# ==========================================

def load_data():
    if os.path.exists(FILE_NAME):
        data = pd.read_csv(FILE_NAME, dtype={"Slot_ID": str})
    else:
        data = pd.DataFrame(columns=[
            "Vehicle_ID",
            "Vehicle_Number",
            "Vehicle_Type",
            "Slot_ID",
            "Entry_Time",
            "Exit_Time",
            "Parking_Fee",
            "Status"
        ])
        data.to_csv(FILE_NAME, index=False)

    required_columns = [
        "Vehicle_ID", "Vehicle_Number", "Vehicle_Type",
        "Slot_ID", "Entry_Time", "Exit_Time",
        "Parking_Fee", "Status"
    ]

    for column in required_columns:
        if column not in data.columns:
            data[column] = ""

    data["Slot_ID"] = data["Slot_ID"].fillna("").astype(str)
    data["Status"] = data["Status"].fillna("")
    data["Vehicle_Number"] = data["Vehicle_Number"].fillna("")
    data["Vehicle_Type"] = data["Vehicle_Type"].fillna("")
    data["Entry_Time"] = data["Entry_Time"].fillna("")
    data["Exit_Time"] = data["Exit_Time"].fillna("")
    data["Parking_Fee"] = pd.to_numeric(
        data["Parking_Fee"], errors="coerce"
    ).fillna(0)

    return data


data = load_data()


def save_data():
    data.to_csv(FILE_NAME, index=False)


# ==========================================
# DISPLAY PARKING STATUS
# ==========================================

def show_status():
    occupied_slots = set(
        data.loc[data["Status"] == "Parked", "Slot_ID"]
    )

    occupied_count = len(occupied_slots)
    available_count = max(0, TOTAL_SLOTS - occupied_count)

    print("\n========== PARKING STATUS ==========")
    print("Total Slots     :", TOTAL_SLOTS)
    print("Occupied Slots  :", occupied_count)
    print("Available Slots :", available_count)

    print("\nSlot Details:")
    for i in range(1, TOTAL_SLOTS + 1):
        slot = f"A{i}"
        if slot in occupied_slots:
            print(f"{slot}: Occupied")
        else:
            print(f"{slot}: Available")


# ==========================================
# VEHICLE ENTRY AND SLOT ALLOCATION
# ==========================================

def vehicle_entry():
    global data

    print("\n========== VEHICLE ENTRY ==========")

    vehicle_number = input(
        "Enter vehicle number: "
    ).strip().upper()

    if not vehicle_number:
        print("Vehicle number cannot be empty.")
        return

    already_parked = data[
        (data["Vehicle_Number"].str.upper() == vehicle_number)
        & (data["Status"] == "Parked")
    ]

    if not already_parked.empty:
        print("This vehicle is already parked.")
        return

    vehicle_type = input(
        "Enter vehicle type (Car/Bike): "
    ).strip().capitalize()

    if vehicle_type not in ["Car", "Bike"]:
        print("Invalid vehicle type. Enter Car or Bike.")
        return

    occupied_slots = set(
        data.loc[data["Status"] == "Parked", "Slot_ID"]
    )

    available_slots = [
        f"A{i}" for i in range(1, TOTAL_SLOTS + 1)
        if f"A{i}" not in occupied_slots
    ]

    if not available_slots:
        print("Parking lot is full!")
        return

    slot = available_slots[0]
    vehicle_id = f"V{len(data) + 1:03d}"
    entry_time = pd.Timestamp.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    new_vehicle = {
        "Vehicle_ID": vehicle_id,
        "Vehicle_Number": vehicle_number,
        "Vehicle_Type": vehicle_type,
        "Slot_ID": slot,
        "Entry_Time": entry_time,
        "Exit_Time": "",
        "Parking_Fee": 0,
        "Status": "Parked"
    }

    data = pd.concat(
        [data, pd.DataFrame([new_vehicle])],
        ignore_index=True
    )

    save_data()

    print("\nVehicle parked successfully!")
    print("Vehicle ID :", vehicle_id)
    print("Vehicle No :", vehicle_number)
    print("Vehicle Type:", vehicle_type)
    print("Allocated Slot:", slot)
    print("Entry Time :", entry_time)


# ==========================================
# VEHICLE EXIT AND BILLING
# ==========================================

def vehicle_exit():
    global data

    print("\n========== VEHICLE EXIT ==========")

    vehicle_number = input(
        "Enter vehicle number: "
    ).strip().upper()

    matches = data[
        (data["Vehicle_Number"].str.upper() == vehicle_number)
        & (data["Status"] == "Parked")
    ]

    if matches.empty:
        print("No parked vehicle found with this number.")
        return

    index = matches.index[-1]

    entry_time = pd.to_datetime(
        data.at[index, "Entry_Time"], errors="coerce"
    )

    if pd.isna(entry_time):
        print("Invalid entry time in the dataset.")
        return

    exit_time = pd.Timestamp.now()
    duration_seconds = max(
        0, (exit_time - entry_time).total_seconds()
    )

    # Charge at least one hour, rounding partial hours up.
    hours = max(1, math.ceil(duration_seconds / 3600))

    vehicle_type = str(
        data.at[index, "Vehicle_Type"]
    ).capitalize()

    if vehicle_type == "Car":
        rate = CAR_RATE
    else:
        rate = BIKE_RATE

    fee = hours * rate

    data.at[index, "Exit_Time"] = exit_time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    data.at[index, "Parking_Fee"] = fee
    data.at[index, "Status"] = "Exited"

    save_data()

    print("\n========== PARKING BILL ==========")
    print("Vehicle Number :", vehicle_number)
    print("Vehicle Type   :", vehicle_type)
    print("Parking Slot   :", data.at[index, "Slot_ID"])
    print("Entry Time     :", entry_time)
    print("Exit Time      :", exit_time.strftime(
        "%Y-%m-%d %H:%M:%S"
    ))
    print("Hours Charged  :", hours)
    print("Rate per Hour  : Rs.", rate)
    print("Total Fee      : Rs.", fee)
    print("Vehicle exit completed successfully!")


# ==========================================
# DISPLAY ALL VEHICLES
# ==========================================

def show_all_vehicles():
    print("\n========== VEHICLE RECORDS ==========")

    if data.empty:
        print("No vehicle records available.")
    else:
        print(data.to_string(index=False))


# ==========================================
# SEARCH VEHICLE
# ==========================================

def search_vehicle():
    vehicle_number = input(
        "Enter vehicle number to search: "
    ).strip().upper()

    result = data[
        data["Vehicle_Number"].str.upper() == vehicle_number
    ]

    if result.empty:
        print("Vehicle not found.")
    else:
        print(result.to_string(index=False))


# ==========================================
# GRAPH 1: OCCUPIED VS AVAILABLE SLOTS
# ==========================================

def plot_slot_status():
    occupied_slots = set(
        data.loc[data["Status"] == "Parked", "Slot_ID"]
    )

    occupied = len(occupied_slots)
    available = max(0, TOTAL_SLOTS - occupied)

    plt.figure(figsize=(7, 5))
    plt.bar(
        ["Occupied", "Available"],
        [occupied, available]
    )
    plt.title("Parking Slot Status")
    plt.ylabel("Number of Slots")
    plt.tight_layout()
    plt.show()


# ==========================================
# GRAPH 2: VEHICLE TYPES
# ==========================================

def plot_vehicle_types():
    if data.empty:
        print("No vehicle data available for the graph.")
        return

    counts = data["Vehicle_Type"].value_counts()

    counts.plot(
        kind="bar",
        figsize=(7, 5),
        title="Vehicles by Type"
    )
    plt.xlabel("Vehicle Type")
    plt.ylabel("Number of Records")
    plt.tight_layout()
    plt.show()


# ==========================================
# GRAPH 3: PARKING SLOT NETWORK
# ==========================================

def plot_network():
    graph = nx.Graph()

    slots = [
        f"A{i}" for i in range(1, TOTAL_SLOTS + 1)
    ]
    graph.add_nodes_from(slots)

    for i in range(1, TOTAL_SLOTS):
        graph.add_edge(f"A{i}", f"A{i + 1}")

    parked_slots = set(
        data.loc[data["Status"] == "Parked", "Slot_ID"]
    )

    colors = [
        "tomato" if slot in parked_slots else "lightgreen"
        for slot in graph.nodes()
    ]

    positions = {
        slot: (i, 0)
        for i, slot in enumerate(slots)
    }

    plt.figure(figsize=(12, 4))
    nx.draw(
        graph,
        positions,
        with_labels=True,
        node_color=colors,
        node_size=1000,
        font_weight="bold"
    )

    plt.title(
        "Parking Slot Network Graph\n"
        "Red = Occupied, Green = Available"
    )
    plt.tight_layout()
    plt.show()


# ==========================================
# MAIN MENU
# ==========================================

def main():
    while True:
        print("\n")
        print("=" * 40)
        print(" PARKING LOT MANAGEMENT SYSTEM")
        print("=" * 40)
        print("1. Vehicle Entry")
        print("2. Vehicle Exit and Billing")
        print("3. View Parking Status")
        print("4. View All Vehicle Records")
        print("5. Search Vehicle")
        print("6. Show Parking Slot Graph")
        print("7. Show Vehicle Type Graph")
        print("8. Show Parking Network Graph")
        print("9. Exit")
        print("=" * 40)

        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            vehicle_entry()
        elif choice == "2":
            vehicle_exit()
        elif choice == "3":
            show_status()
        elif choice == "4":
            show_all_vehicles()
        elif choice == "5":
            search_vehicle()
        elif choice == "6":
            plot_slot_status()
        elif choice == "7":
            plot_vehicle_types()
        elif choice == "8":
            plot_network()
        elif choice == "9":
            print("Thank you for using the Parking Lot Management System!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 9.")


if __name__ == "__main__":
    main()
