import sqlite3

class PulseAiSqlite:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)

    # Method to add data to the InspectorProperty table
    def add_inspector_property(self, street_address, city, state, postal_code, country):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO InspectorProperty (StreetAddress, City, State, PostalCode, Country)
                VALUES (?, ?, ?, ?, ?)
            ''', (street_address, city, state, postal_code, country))
            return cursor.lastrowid
    

    def search_inspector_property(self, street_address, city, state, postal_code, country):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM InspectorProperty
                WHERE StreetAddress = ? AND City = ? AND State = ? AND PostalCode = ? AND Country = ?
            ''', (street_address, city, state, postal_code, country))
            result = cursor.fetchone()
            return result

    # Method to add a floor plan image URL to an existing inspector property
    def add_floor_plan_image_url(self, property_id, floor_plan_image_url):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE InspectorProperty
                SET FloorPlanImageUrl = ?
                WHERE Id = ?
            ''', (floor_plan_image_url, property_id))
            return cursor.rowcount

    # Method to add data to the InspectorPropertyFloorPlanLabels table
    def add_floor_plan_label(self, floor_plan_label, inspector_property_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO InspectorPropertyFloorPlanLabels (FloorPlanLabel, InspectorPropertyId)
                VALUES (?, ?)
            ''', (floor_plan_label, inspector_property_id))
            return cursor.lastrowid

    # Method to add data to the PropertyWebsite table
    def add_property_website(self, base_url):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO PropertyWebsite (BaseUrl) VALUES (?)', (base_url,))
            return cursor.lastrowid

    # Method to add data to the InspectorPropertyUrl table
    def add_inspector_property_url(self, inspector_property_id, property_website_id, url):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO InspectorPropertyUrl (InspectorPropertyId, PropertyWebsiteId, Url)
                VALUES (?, ?, ?)
            ''', (inspector_property_id, property_website_id, url))
            return cursor.lastrowid