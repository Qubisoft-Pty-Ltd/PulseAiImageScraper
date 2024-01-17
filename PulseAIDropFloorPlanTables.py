import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('../propertypulseai')
cursor = conn.cursor()

# Drop the InspectorPropertyUrl table
cursor.execute('DROP TABLE IF EXISTS InspectorPropertyUrl')

# Drop the PropertyWebsite table
cursor.execute('DROP TABLE IF EXISTS PropertyWebsite')

# Drop the InspectorPropertyFloorPlanLabels table
cursor.execute('DROP TABLE IF EXISTS InspectorPropertyFloorPlanLabels')

# Drop the InspectorProperty table
cursor.execute('DROP TABLE IF EXISTS InspectorProperty')

# Commit changes and close the connection
conn.commit()
conn.close()