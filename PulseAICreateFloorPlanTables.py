import sqlite3

# Create a SQLite database (or connect to an existing one)
conn = sqlite3.connect('../propertypulseai')
cursor = conn.cursor()

# Create InspectorProperty table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS InspectorProperty (
        Id INTEGER PRIMARY KEY,
        StreetAddress VARCHAR(255),
        City VARCHAR(100),
        State VARCHAR(100),
        PostalCode VARCHAR(20),
        Country VARCHAR(100),
        FloorPlanImageUrl VARCHAR(255)
    )
''')

# Create InspectorPropertyFloorPlanLabels table with a foreign key to InspectorProperty
cursor.execute('''
    CREATE TABLE IF NOT EXISTS InspectorPropertyFloorPlanLabels (
        Id INTEGER PRIMARY KEY,
        FloorPlanLabel TEXT NOT NULL,
        InspectorPropertyId INTEGER,
        FOREIGN KEY (InspectorPropertyId) REFERENCES InspectorProperty(Id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS PropertyWebsite (
        Id INTEGER PRIMARY KEY,
        BaseUrl VARCHAR(255)
    )
''')

cursor.execute('''
    INSERT INTO PropertyWebsite (BaseUrl) VALUES (?)
''', ('https://www.domain.com.au/',))

# Create InspectorPropertyUrl table with a foreign key to InspectorProperty
cursor.execute('''
    CREATE TABLE IF NOT EXISTS InspectorPropertyUrl (
        Id INTEGER PRIMARY KEY,
        InspectorPropertyId INTEGER,
        PropertyWebsiteId INTEGER,
        Url TEXT,
        FOREIGN KEY (InspectorPropertyId) REFERENCES InspectorProperty(Id),
        FOREIGN KEY (PropertyWebsiteId) REFERENCES PropertyWebsite(Id)
    )
''')

# Commit changes and close the connection
conn.commit()
conn.close()