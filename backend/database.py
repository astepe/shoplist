"""
Database initialization and connection management.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database.db"

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create ingredient types table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredient_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Create unit types table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS unit_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            CHECK(category IN ('volume', 'weight', 'count', 'special'))
        )
    """)
    
    # Create ingredients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type_id INTEGER NOT NULL,
            shopping_unit_id INTEGER NOT NULL,
            FOREIGN KEY (type_id) REFERENCES ingredient_types(id),
            FOREIGN KEY (shopping_unit_id) REFERENCES unit_types(id)
        )
    """)
    
    # Create conversion rules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversion_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_id INTEGER NOT NULL,
            from_unit_id INTEGER NOT NULL,
            to_unit_id INTEGER NOT NULL,
            conversion_factor REAL NOT NULL,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
            FOREIGN KEY (from_unit_id) REFERENCES unit_types(id),
            FOREIGN KEY (to_unit_id) REFERENCES unit_types(id),
            UNIQUE(ingredient_id, from_unit_id)
        )
    """)
    
    # Create size estimation rules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS size_estimation_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_id INTEGER NOT NULL,
            size_qualifier TEXT NOT NULL,
            reference_unit_id INTEGER NOT NULL,
            reference_value REAL NOT NULL,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
            FOREIGN KEY (reference_unit_id) REFERENCES unit_types(id),
            CHECK(size_qualifier IN ('small', 'medium', 'large')),
            UNIQUE(ingredient_id, size_qualifier)
        )
    """)
    
    # Create recipes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            is_sub_recipe INTEGER NOT NULL DEFAULT 0,
            yield_quantity REAL NOT NULL,
            yield_unit_id INTEGER NOT NULL,
            FOREIGN KEY (yield_unit_id) REFERENCES unit_types(id),
            CHECK(is_sub_recipe IN (0, 1))
        )
    """)
    
    # Add page_number column to recipes if missing
    try:
        cursor.execute("PRAGMA table_info(recipes)")
        cols = [row[1] for row in cursor.fetchall()]
        if 'page_number' not in cols:
            cursor.execute("ALTER TABLE recipes ADD COLUMN page_number INTEGER")
    except Exception:
        # Safe to ignore; column may already exist or ALTER may fail on some SQLite versions
        pass
    
    # Create recipe items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,
            ingredient_id INTEGER,
            sub_recipe_id INTEGER,
            quantity REAL NOT NULL,
            unit_id INTEGER NOT NULL,
            size_qualifier TEXT,
            preparation_notes TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
            FOREIGN KEY (sub_recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (unit_id) REFERENCES unit_types(id),
            CHECK(item_type IN ('ingredient', 'sub_recipe')),
            CHECK((item_type = 'ingredient' AND ingredient_id IS NOT NULL AND sub_recipe_id IS NULL) OR
                  (item_type = 'sub_recipe' AND sub_recipe_id IS NOT NULL AND ingredient_id IS NULL)),
            CHECK(size_qualifier IS NULL OR size_qualifier IN ('small', 'medium', 'large'))
        )
    """)
    
    # Create shopping lists table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopping_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            recipe_selections TEXT NOT NULL,
            shopping_list_data TEXT NOT NULL
        )
    """)
    
    conn.commit()
    
    # Insert default unit types
    default_units = [
        # Volume
        ('cup', 'volume'), ('tablespoon', 'volume'), ('teaspoon', 'volume'),
        ('milliliter', 'volume'), ('liter', 'volume'), ('fluid_ounce', 'volume'),
        # Weight
        ('gram', 'weight'), ('kilogram', 'weight'), ('ounce', 'weight'), ('pound', 'weight'),
        # Count
        ('whole', 'count'), ('piece', 'count'), ('head', 'count'), ('bunch', 'count'),
        ('clove', 'count'), ('package', 'count'),
        # Special
        ('serving', 'special'), ('to_taste', 'special'), ('as_needed', 'special')
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO unit_types (name, category) VALUES (?, ?)
    """, default_units)
    
    # Insert default ingredient types
    default_types = [
        'Vegetables', 'Fruits', 'Grains', 'Plant Proteins', 
        'Nuts & Seeds', 'Spices', 'Herbs', 'Liquids', 'Pantry Items'
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO ingredient_types (name) VALUES (?)
    """, [(t,) for t in default_types])
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()

