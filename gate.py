
import math
import os
import random
import time
from datetime import datetime, timedelta


# CONSTANTS #
WHEEL_CATEGORIES = [
    ("two_wheel", "Two-Wheel Vehicles"),
    ("three_wheel", "Three-Wheel Vehicles"),
    ("four_wheel", "Four-Wheel Vehicles"),
    ("five_wheel", "Five-Or-More-Wheel Vehicles"),
]

VEHICLE_GROUPS = {
    2: ["Motorcycle", "Bicycle", "Scooter", "Motor"],
    3: ["Bajaj", "Becak", "Bentor"],
    4: ["Car", "Angkot", "Taxi"],
    5: ["Bus", "Truck"],
}

RATE_KEYS = {2: "two_wheel", 3: "three_wheel", 4: "four_wheel", 5: "five_wheel"}

CARD_NAMES = {1: "E-Money", 2: "Brizzi", 3: "Flazz", 4: "TapCash"}

TRACK_WIDTH = 35
GATE_POS = 18



# INPUT FAILSAFES #

def askYesNo(prompt):
    #Keeps asking until the answer is y or n.#
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "n"):
            return answer
        print("Invalid input. Please answer with y or n.")


def askInt(prompt, minValue=None, maxValue=None):
    #Keeps asking until a whole number (inside the range) is entered.#
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Invalid input. Please enter a whole number.")
            continue
        if minValue is not None and value < minValue:
            print("Value must be at least " + str(minValue) + ".")
            continue
        if maxValue is not None and value > maxValue:
            print("Value must be at most " + str(maxValue) + ".")
            continue
        return value


def askName(prompt):
    #Keeps asking until a non-empty name made of letters/spaces is entered.#
    while True:
        name = " ".join(input(prompt).split())
        if name and all(c.isalpha() or c in " .'-" for c in name):
            return name.title()
        print("Invalid name. Use letters only and do not leave it empty.")


def askTime(prompt):
    #Keeps asking until a valid HH:MM (24-hour) time is entered.#
    while True:
        raw = input(prompt).strip()
        try:
            parsed = datetime.strptime(raw, "%H:%M")
        except ValueError:
            print("Invalid time. Use HH:MM in 24-hour format (e.g. 08:30, 17:45).")
            continue
        return parsed.strftime("%H:%M")


# ----------------------------------------------------------------------
# SETUP MENU
# ----------------------------------------------------------------------
def configureRates():
    rates = {}
    print("===START MENU===")
    print("================")
    for key, label in WHEEL_CATEGORIES:
        print("")
        print("---Configuration for " + label + "---")
        hourly = askInt("Hourly Rates (Rp): ", 0)
        first = askInt("Cost of First Hour (Rp): ", 0)
        maxHour = askInt("Maximum Hours Cap (Hours): ", 1)
        rates[key] = {
            "hourly_rate": hourly,
            "first_hour": first,
            "max_hour": maxHour,
        }
    print("")
    print("===CONFIG COMPLETE===")
    return rates


# ----------------------------------------------------------------------
# GATE VISUALIZATION
# ----------------------------------------------------------------------
def clearScreen():
    os.system("cls" if os.name == "nt" else "clear")


def drawTrack(pos, length, gateChar, status):
    clearScreen()
    track = [" "] * TRACK_WIDTH
    track[GATE_POS] = gateChar
    for i in range(length):
        if 0 <= pos + i < TRACK_WIDTH:
            track[pos + i] = "■"
    print("Current Track View:")
    print("".join(track))
    print(status)


def animateGate(wheelCount):
    #Vehicle drives up, gate opens, vehicle passes, gate closes.#
    length = max(2, min(wheelCount, 5))

    # 1. Approach (gate closed)
    for pos in range(0, GATE_POS - length + 1):
        drawTrack(pos, length, "|",
                  "Status: Vehicle approaching gate... [Gate: CLOSED]")
        time.sleep(0.25)

    # 2. Gate opens
    print("\n[Sensor detected vehicle] -> [Card OK] -> [GATE OPENS]")
    time.sleep(1)

    # 3. Vehicle passes (gate open)
    for pos in range(GATE_POS - length + 1, GATE_POS + 2):
        drawTrack(pos, length, " ",
                  "Status: Vehicle passing through... [Gate: OPEN]")
        time.sleep(0.25)

    # 4. Clearance check, then close
    print("\n[Checking every 1 second: has the rear of the vehicle left the gate?]")
    time.sleep(1)
    drawTrack(GATE_POS + 1, length, "|",
              "Status: Rear of vehicle cleared the gate. [Gate: CLOSED]")
    time.sleep(1)


# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------
def findWheelCount(vehicle):
    #Returns wheel count for a known vehicle name, or None if unknown.#
    for wheels, names in VEHICLE_GROUPS.items():
        if vehicle in names:
            return wheels
    return None


def newUid(database):
    #Random 7-digit UID that is guaranteed not to exist yet.#
    while True:
        uid = random.randint(1000000, 9999999)
        if uid not in database:
            return uid


def calculateParking(entryTime, exitTime, rateInfo):
    #Returns (hoursParked, hoursCharged, totalFee).#
    entry = datetime.strptime(entryTime, "%H:%M")
    exitDt = datetime.strptime(exitTime, "%H:%M")

    # Exit earlier than entry on the clock = parked past midnight
    if exitDt < entry:
        exitDt += timedelta(days=1)

    seconds = (exitDt - entry).total_seconds()
    hoursParked = max(1, math.ceil(seconds / 3600))  # round up, minimum 1 hour

    hoursCharged = min(hoursParked, rateInfo["max_hour"])
    totalFee = rateInfo["first_hour"] + (hoursCharged - 1) * rateInfo["hourly_rate"]
    return hoursParked, hoursCharged, totalFee


def saveData(vehicleRates, databaseUID):
    #Saves a snapshot to data.py (same format as the original files).#
    folder = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(folder, "data.py")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("vehicleRate = " + repr(vehicleRates) + "\n")
            f.write("databaseUID = " + repr(databaseUID) + "\n")
    except OSError as error:
        print("Warning: could not save data.py (" + str(error) + ")")


def loadData():
    #Loads previously saved data from data.py
    folder = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(folder, "data.py")

    if os.path.exists(path):
        try:
            import runpy
            savedData = runpy.run_path(path)

            vehicleRates = savedData["vehicleRate"]
            databaseUID = savedData["databaseUID"]

            print("Previous data loaded!")
            return vehicleRates, databaseUID

        except (KeyError, OSError, SyntaxError) as error:
            print("Could not load previous data: ", error)

        print("No previous data found. Starting new configuration.")
        return{}, {}


# ----------------------------------------------------------------------
# ENTRY BRANCH
# ----------------------------------------------------------------------
def handleEntry(vehicleRates, databaseUID):
    print("")
    print("---ENTRY GATE---")
    if askYesNo("Is there a vehicle? (y/n): ") == "n":
        return

    print("Please tap your E-Money / Brizzi / Flazz / TapCash")

    card = askInt("Card (1=E-Money, 2=Brizzi, 3=Flazz, 4=TapCash): ")
    if card not in CARD_NAMES:
        print("Unknown Card")
        print("Gate remains closed.")
        return

    fullName = askName("Please input your Full Name: ")
    balance = askInt("Please input your card's balance (Rp): ", 0)

    vehicle = ""
    while not vehicle:
        vehicle = " ".join(input("What is your vehicle?: ").split()).title()
        if not vehicle:
            print("Vehicle cannot be empty.")

    wheels = findWheelCount(vehicle)
    if wheels is None:
        wheels = askInt("Vehicle not found. Please input the number of wheels (2 or more): ", 2)

    entryTime = askTime("Please input the time of entry (HH:MM, 24-hour): ")

    rateTicket = RATE_KEYS[min(wheels, 5)]
    uid = newUid(databaseUID)

    databaseUID[uid] = {
        "name": fullName,
        "card": card,
        "balance": balance,
        "vehicle": vehicle,
        "wheels": wheels,
        "rateTicket": rateTicket,
        "entryTime": entryTime,
        "status": "OPEN",
    }

    print("PROCESSING...")
    time.sleep(1)
    print("YOUR DATA HAS BEEN RECORDED")
    print("GATE OPENS")
    time.sleep(1)

    animateGate(wheels)

    print("")
    print("GATE CLOSES")
    print("Welcome, " + fullName + "!")
    print("YOUR SESSION ID IS = " + str(uid) + "   (keep it, you need it to exit)")


# ----------------------------------------------------------------------
# EXIT BRANCH
# ----------------------------------------------------------------------
def handleExit(vehicleRates, databaseUID):
    print("")
    print("---EXIT GATE---")
    if askYesNo("Is there a vehicle? (y/n): ") == "n":
        return

    print("Please tap your card to exit")
    uid = askInt("Enter your Session ID: ")

    if uid not in databaseUID:
        print("Unknown Card")
        return

    record = databaseUID[uid]
    if record["status"] == "CLOSED":
        print("Session already closed")
        return

    exitTime = askTime("Please input the time of exit (HH:MM, 24-hour): ")

    rateInfo = vehicleRates[record["rateTicket"]]
    hoursParked, hoursCharged, totalFee = calculateParking(
        record["entryTime"], exitTime, rateInfo
    )

    print("Parking Duration:", hoursParked, "hour(s)")
    if hoursCharged < hoursParked:
        print("Maximum hours cap reached: charged for", hoursCharged, "hour(s)")
    print("Total Parking Fee: Rp", totalFee)

    if record["balance"] < totalFee:
        print("Insufficient Balance")
        print("Short by: Rp", totalFee - record["balance"])
        print("Please top up your card. Gate remains closed.")
        return

    record["balance"] -= totalFee
    print("Payment Successful!")
    print("Remaining Balance: Rp", record["balance"])

    record["exitTime"] = exitTime
    record["parkingHours"] = hoursParked
    record["parkingFee"] = totalFee
    record["status"] = "CLOSED"

    time.sleep(1)
    animateGate(record["wheels"])

    print("")
    print("GATE CLOSES")
    print("Thank you, " + record["name"] + "!")
    print("Parked: " + record["entryTime"] + " -> " + exitTime +
          " | Fee: Rp " + str(totalFee) +
          " | Remaining balance: Rp " + str(record["balance"]))


# ----------------------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------------------
def main():
    vehicleRates = {}
    databaseUID = {}
    try:
        vehicleRates, databaseUID = loadData()

        if not vehicleRates:
            vehicleRates = configureRates()
        saveData(vehicleRates, databaseUID)

        # Runs until the program is stopped (Ctrl+C)
        while True:
            print("")
            if askYesNo("New Vehicle? (y/n): ") == "y":
                handleEntry(vehicleRates, databaseUID)
            else:
                handleExit(vehicleRates, databaseUID)
            saveData(vehicleRates, databaseUID)
    except (KeyboardInterrupt, EOFError):
        print("\nSystem stopped. Data saved to data.py.")
        saveData(vehicleRates, databaseUID)


if __name__ == "__main__":
    main()