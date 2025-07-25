import sqlite3

# Connect to the database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    print("Checking current table structure...")
    cursor.execute("PRAGMA table_info(asset_manager_marketplacelisting);")
    columns = cursor.fetchall()
    print("Current columns:")
    for col in columns:
        print(f"  {col[1]} {col[2]}")
    
    # Check if the table has the wrong column names
    column_names = [col[1] for col in columns]
    
    if 'created_at' in column_names and 'listed_at' not in column_names:
        print("\nFixing column names...")
        
        # Drop and recreate the table with correct structure
        cursor.execute("DROP TABLE IF EXISTS asset_manager_marketplacelisting_backup;")
        
        # Backup existing data (if any)
        cursor.execute("""
            CREATE TABLE asset_manager_marketplacelisting_backup AS 
            SELECT * FROM asset_manager_marketplacelisting;
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE asset_manager_marketplacelisting;")
        
        # Create new table with correct structure
        create_table_sql = '''
        CREATE TABLE asset_manager_marketplacelisting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL UNIQUE,
            seller_id INTEGER NOT NULL,
            listing_price DECIMAL(15,2) NOT NULL,
            description TEXT,
            contact_phone VARCHAR(20),
            contact_email VARCHAR(254),
            is_active BOOLEAN NOT NULL DEFAULT 1,
            listed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asset_id) REFERENCES asset_manager_asset (id) DEFERRABLE INITIALLY DEFERRED,
            FOREIGN KEY (seller_id) REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED
        );
        '''
        
        cursor.execute(create_table_sql)
        
        # Create indexes
        cursor.execute('CREATE INDEX asset_manager_marketplacelisting_asset_id ON asset_manager_marketplacelisting (asset_id);')
        cursor.execute('CREATE INDEX asset_manager_marketplacelisting_seller_id ON asset_manager_marketplacelisting (seller_id);')
        cursor.execute('CREATE INDEX asset_manager_marketplacelisting_is_active ON asset_manager_marketplacelisting (is_active);')
        
        # If there was backup data, restore it with correct column mapping
        cursor.execute("SELECT COUNT(*) FROM asset_manager_marketplacelisting_backup;")
        backup_count = cursor.fetchone()[0]
        
        if backup_count > 0:
            cursor.execute("""
                INSERT INTO asset_manager_marketplacelisting 
                (asset_id, seller_id, listing_price, description, contact_phone, contact_email, is_active, listed_at, updated_at)
                SELECT asset_id, seller_id, listing_price, description, contact_phone, contact_email, is_active, created_at, updated_at
                FROM asset_manager_marketplacelisting_backup;
            """)
            print(f"Restored {backup_count} records from backup")
        
        # Drop backup table
        cursor.execute("DROP TABLE asset_manager_marketplacelisting_backup;")
        
        conn.commit()
        print("Table structure fixed successfully!")
        
    else:
        print("Table structure is already correct")
    
    # Show final structure
    print("\nFinal table structure:")
    cursor.execute("PRAGMA table_info(asset_manager_marketplacelisting);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} {col[2]}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()

finally:
    conn.close()
    print("Database connection closed") 