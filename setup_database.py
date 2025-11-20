#!/usr/bin/env python3
"""
Setup script to initialize the database with default ingredients and conversion formulas.
This script loads all ingredients from default_conversions.py with their conversion rules.

Run this script after initializing the database schema to populate it with default data.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db, get_db
from backend.default_conversions import DEFAULT_CONVERSIONS, get_default_conversions

def get_unit_id(name, cursor):
    """Get unit type ID by name."""
    cursor.execute("SELECT id FROM unit_types WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Unit '{name}' not found")
    return result['id']

def get_type_id(name, cursor):
    """Get ingredient type ID by name."""
    cursor.execute("SELECT id FROM ingredient_types WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Ingredient type '{name}' not found")
    return result['id']

def create_ingredient_with_conversions(name, type_name, shopping_unit_name, conversion_rules, size_rules=None, db=None):
    """Create an ingredient with conversion and size estimation rules."""
    if db is None:
        db = get_db()
        close_after = True
    else:
        close_after = False
    
    try:
        cursor = db.cursor()
        
        # Get IDs
        type_id = get_type_id(type_name, cursor)
        shopping_unit_id = get_unit_id(shopping_unit_name, cursor)
        
        # Check if ingredient already exists
        cursor.execute("SELECT id FROM ingredients WHERE name = ?", (name,))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ {name} already exists (ID: {existing['id']}) - skipping")
            return existing['id']
        
        # Create ingredient
        cursor.execute("""
            INSERT INTO ingredients (name, type_id, shopping_unit_id)
            VALUES (?, ?, ?)
        """, (name, type_id, shopping_unit_id))
        
        ingredient_id = cursor.lastrowid
        print(f"  ✓ Created {name} (ID: {ingredient_id})")
        
        # Add conversion rules
        for rule in conversion_rules:
            from_unit_id = get_unit_id(rule['from'], cursor)
            cursor.execute("""
                INSERT OR IGNORE INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                VALUES (?, ?, ?, ?)
            """, (ingredient_id, from_unit_id, shopping_unit_id, rule['factor']))
            print(f"    ✓ Conversion: {rule['from']} → {shopping_unit_name}: {rule['factor']:.6f}")
        
        # Add size estimation rules
        if size_rules:
            for size_rule in size_rules:
                ref_unit_id = get_unit_id(size_rule['reference_unit'], cursor)
                cursor.execute("""
                    INSERT OR IGNORE INTO size_estimation_rules (ingredient_id, size_qualifier, reference_unit_id, reference_value)
                    VALUES (?, ?, ?, ?)
                """, (ingredient_id, size_rule['size'], ref_unit_id, size_rule['value']))
                print(f"    ✓ Size rule: {size_rule['size']} = {size_rule['value']} {size_rule['reference_unit']}")
        
        db.commit()
        return ingredient_id
    
    finally:
        if close_after:
            db.close()

def determine_ingredient_type(ingredient_name):
    """Determine ingredient type based on name."""
    name_lower = ingredient_name.lower()
    
    # Vegetables
    vegetables = ['celery', 'onion', 'tomato', 'carrot', 'bell pepper', 'garlic', 'potato', 
                  'sweet potato', 'broccoli', 'cauliflower', 'cabbage', 'spinach', 'lettuce']
    
    # Fruits
    fruits = ['avocado', 'lemon', 'lime']
    
    # Grains & Legumes
    grains = ['rice', 'lentils', 'quinoa']
    
    # Herbs
    herbs = ['parsley', 'cilantro', 'basil']
    
    # Nuts & Seeds
    nuts = ['almonds', 'cashews']
    
    if any(v in name_lower for v in vegetables):
        return 'Vegetables'
    elif any(f in name_lower for f in fruits):
        return 'Fruits'
    elif any(g in name_lower for g in grains):
        return 'Grains'
    elif any(h in name_lower for h in herbs):
        return 'Herbs'
    elif any(n in name_lower for n in nuts):
        return 'Nuts & Seeds'
    else:
        return 'Pantry Items'  # Default fallback

def main():
    """Main function to load all default ingredients."""
    print("=" * 60)
    print("Setting up ShopList Database")
    print("=" * 60)
    
    # Step 1: Initialize database schema
    print("\n--- Step 1: Initializing database schema ---")
    init_db()
    print("✓ Database schema initialized")
    
    # Step 2: Load default ingredients
    print("\n--- Step 2: Loading default ingredients and conversions ---")
    db = get_db()
    
    try:
        cursor = db.cursor()
        
        # Count existing ingredients
        cursor.execute("SELECT COUNT(*) as count FROM ingredients")
        existing_count = cursor.fetchone()['count']
        
        if existing_count > 0:
            print(f"⚠ Found {existing_count} existing ingredients in database.")
            response = input("Do you want to add default ingredients anyway? (y/n): ")
            if response.lower() != 'y':
                print("Skipping ingredient loading.")
                return
        
        # Load each ingredient from DEFAULT_CONVERSIONS
        ingredients_loaded = 0
        for ingredient_name, config in DEFAULT_CONVERSIONS.items():
            print(f"\n--- Loading {ingredient_name} ---")
            
            # Determine ingredient type
            type_name = determine_ingredient_type(ingredient_name)
            
            # Get shopping unit
            shopping_unit = config['shopping_unit']
            
            # Convert conversion rules to the format expected by create_ingredient_with_conversions
            conversion_rules = []
            for conv in config.get('conversions', []):
                conversion_rules.append({
                    'from': conv['from'],
                    'factor': conv['factor']
                })
            
            # Convert size estimation rules
            size_rules = []
            for size_rule in config.get('size_estimation', []):
                size_rules.append({
                    'size': size_rule['size'],
                    'reference_unit': size_rule['reference_unit'],
                    'value': size_rule['value']
                })
            
            try:
                create_ingredient_with_conversions(
                    ingredient_name,
                    type_name,
                    shopping_unit,
                    conversion_rules,
                    size_rules if size_rules else None,
                    db
                )
                ingredients_loaded += 1
            except Exception as e:
                print(f"  ✗ Error loading {ingredient_name}: {e}")
        
        print("\n" + "=" * 60)
        print(f"✓ Setup complete! Loaded {ingredients_loaded} ingredients with conversion formulas.")
        print("=" * 60)
        print("\nNote: The recipes table is empty. You can add your own recipes through the web interface.")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()

