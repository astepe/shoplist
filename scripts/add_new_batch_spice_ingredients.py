#!/usr/bin/env python3
"""
Script to add spice ingredients for new batch recipes:
1. Ground Coriander
2. Cayenne Pepper
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db

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

def create_ingredient_with_conversions(name, type_name, shopping_unit_name, conversion_rules, db=None):
    """Create an ingredient with conversion rules."""
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
                INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                VALUES (?, ?, ?, ?)
            """, (ingredient_id, from_unit_id, shopping_unit_id, rule['factor']))
            print(f"    ✓ Conversion: {rule['from']} → {shopping_unit_name}: {rule['factor']:.6f}")
        
        db.commit()
        return ingredient_id
    
    finally:
        if close_after:
            db.close()

def main():
    """Main function to add all spice ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Spice Ingredients for New Batch Recipes")
        print("=" * 60)
        
        # Step 1: Add Ground Coriander
        print("\n--- Step 1: Adding Ground Coriander ---")
        create_ingredient_with_conversions(
            name='Ground Coriander',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/22.8},  # 1/22.8 = 0.0439 packages/tsp
                {'from': 'gram', 'factor': 1/57},  # 1/57 packages/g
                {'from': 'ounce', 'factor': 1/2},  # 1/2 = 0.5 packages/oz
            ],
            db=db
        )
        
        # Step 2: Add Cayenne Pepper
        print("\n--- Step 2: Adding Cayenne Pepper ---")
        create_ingredient_with_conversions(
            name='Cayenne Pepper',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/22.8},  # 1/22.8 = 0.0439 packages/tsp
                {'from': 'gram', 'factor': 1/57},  # 1/57 packages/g
                {'from': 'ounce', 'factor': 1/2},  # 1/2 = 0.5 packages/oz
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All spice ingredients added successfully!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    main()

