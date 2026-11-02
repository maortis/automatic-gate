import os
from data import databaseUID, vehicleRate

folder = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(folder, "data.py")

while True:
    print("---TOP UP CARD---")
    
    uid = int(input("Enter Session UID: "))
    
    if uid in databaseUID:
        print("Welcome, " + databaseUID[uid]['name'] + "!")
        print("Current Balance: Rp.", databaseUID[uid]['balance'])
    
        TopUpAmount = int(input("How much would you like to Top-Up?\nRp. "))
    
        if TopUpAmount > 0:
            databaseUID[uid]['balance'] += TopUpAmount
    
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("vehicleRate = " + repr(vehicleRate) + "\n")
                    f.write("databaseUID = " + repr(databaseUID) + "\n")
            except OSError as error:
                print("Warning: could not save data.py (" + str(error) + ")")
    
            print("--- TOP-UP SUCCESFUL ---")
            print("New Balance: Rp.", databaseUID[uid]['balance'])
    
        else:
            print("Invalid Top-Up Amount!")
    
    else:
        print("Session UID not found!")
        
