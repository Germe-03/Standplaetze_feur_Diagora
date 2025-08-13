import sqlite3

# Verbindung zur Datenbank herstellen
conn = sqlite3.connect('../Databank/StandplaetzeDatabank.db')
cursor = conn.cursor()

# Alle bestehenden Daten löschen
print("Lösche alle bestehenden Daten...")

# Reihenfolge beachten wegen Foreign Key Constraints
cursor.execute("DELETE FROM Bookings")
cursor.execute("DELETE FROM LocationLimits")
cursor.execute("DELETE FROM CityLimit")
cursor.execute("DELETE FROM Locations")
cursor.execute("DELETE FROM Cities")
cursor.execute("DELETE FROM Campaign")
cursor.execute("DELETE FROM LocationType")
cursor.execute("DELETE FROM ContactInformation")
cursor.execute("DELETE FROM Address")
cursor.execute("DELETE FROM Users")

print("Alle Daten gelöscht. Füge Testdaten ein...")

# 1. LocationType einfügen (3x)
cursor.execute("""
INSERT INTO LocationType (LocationTypeID, LocationType, UserID) VALUES 
(1, 'Altstadt', 1),
(2, 'Innenstadt', 1),
(3, 'Bahnhof', 1)
""")

# 2. Users einfügen (2x)
cursor.execute("""
INSERT INTO Users (UserID, LastName, FirstName, Password, Role) VALUES 
(1, 'Germann', 'David', 'password123', 'admin'),
(2, 'Duss', 'David', 'password456', 'user')
""")

# 3. Cities einfügen (2x)
cursor.execute("""
INSERT INTO Cities (CityID, Name, State) VALUES 
(1, 'Aarau', 'Aargau'),
(2, 'Luzern', 'Luzern')
""")

# 4. Locations einfügen (5x - 2 für Berlin, 3 für München)
cursor.execute("""
INSERT INTO Locations (LocationID, Name, IsSBB, MaxDialog, good, Notes, CityID, UserID) VALUES 
(1, 'Igelweid', 0, 4, 1, NULL, 1, 1),
(2, 'Bahnhofplatz', 0, 5, 1, 'Überdachte Garage', 1, 2),
(3, 'Pilatusstrasse', 0, 4, 1, NULL, 2, 1),
(4, 'Postplatz', 0, 3, 1, NULL, 2, 1),
(5, 'Torbogen', 0, 4, 0, NULL, 2, 1)
""")

# 5. LocationLimits einfügen (2x für Standplätze)
cursor.execute("""
INSERT INTO LocationLimits (LocationLimitID, LocationLimitYearly, LocationLimitMonthly, LocationLimitCampaign, LocationID, ValidFrom, UserID) VALUES 
(1, 4, NULL, NULL, 2, '2024-01-01', 1)
""")

# 6. Campaign einfügen (1x)
cursor.execute("""
INSERT INTO Campaign (CampaignID, Name, Year, Budget, UserID) VALUES 
(1, 'Pro Natura', 2026, 20000.0, 1)
""")

# 7. CityLimit einfügen (2x für Städte)
cursor.execute("""
INSERT INTO CityLimit (CityLimitID, CityLimitYearly, CityLimitMonthly, CityLimitCampaign, CityLimitYearlyPerL, CityLimitMonthlyPerL, CityLimitCampaignPerL, ValidFrom, CityID) VALUES 
(1, 8, NULL, NULL, NULL, NULL, NULL, '2024-01-01', 1),
(2, 12, 2, NULL, 3, NULL, NULL, '2024-01-01', 2)
""")

# 8. ContactInformation einfügen (2x)
cursor.execute("""
INSERT INTO ContactInformation (ContactInformationID, EMail, Phone, UserID) VALUES 
(1, 'mdavidgerm3@gmail.com', 0767476030, 1),
(2, 'david.duss@gmx.ch', 0765608598, 2)
""")

# 9. Address einfügen (2x)
cursor.execute("""
INSERT INTO Address (AddressID, Street, Number, Zip, City, State, UserID) VALUES 
(1, 'Quellenweg', '3', '5614', 'Sarmenstorf', 'Aargau', 1),
(2, 'Jurastrasse', '8a', '5610', 'Wohlen', 'Aargau', 2)
""")

# 10. Bookings einfügen (6x)
cursor.execute("""
INSERT INTO Bookings (BookingID, DateOfBooking, DateOfEvent, DateOfLastUpdate, Price, Confirmed, LocationID, Cancelled, CampaignID, UserID) VALUES 
(1, '2026-01-01', '2026-01-04', '2026-01-01', 40.00, 1, 1, 0, 1, 1),
(2, '2026-01-01', '2026-01-20', '2026-01-01', 40.00, 1, 2, 0, 1, 2),
(3, '2026-01-03', '2026-01-07', '2026-01-03', 100.00, 1, 3, 0, 1, 1),
(4, '2026-01-03', '2026-01-15', '2026-01-03', 100.00, 1, 4, 0, 1, 2),
(5, '2026-01-03', '2026-01-23', '2026-01-03', 100.00, 1, 2, 0, 1, 1),
(6, '2026-01-03', '2026-01-30', '2026-01-07', 100.00, 0, 2, 0, 1, 2)
""")

# Änderungen speichern
conn.commit()
print("Testdaten erfolgreich eingefügt!")

# Verbindung schließen
conn.close()
