#!/usr/bin/env python3
"""
Script to add ingredients for Nutty Parm 2.0 recipe.
This script adds:
1. Raw Cashews
2. Brazil Nuts
3. Raw Walnuts
4. Raw Pecans
5. Raw Sesame Seeds
"""

import os
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
    """Main function to add all Nutty Parm ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Ingredients for Nutty Parm 2.0")
        print("=" * 60)
        
        # Step 1: Add Raw Cashews
        print("\n--- Step 1: Adding Raw Cashews ---")
        create_ingredient_with_conversions(
            name='Raw Cashews',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 140/454},  # 140/454 = 0.3084 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
                {'from': 'pound', 'factor': 1},  # 1 lb = 1 package
            ],
            db=db
        )
        
        # Step 2: Add Brazil Nuts
        print("\n--- Step 2: Adding Brazil Nuts ---")
        create_ingredient_with_conversions(
            name='Brazil Nuts',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 140/454},  # 140/454 = 0.3084 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
                {'from': 'pound', 'factor': 1},  # 1 lb = 1 package
            ],
            db=db
        )
        
        # Step 3: Add Raw Walnuts
        print("\n--- Step 3: Adding Raw Walnuts ---")
        create_ingredient_with_conversions(
            name='Raw Walnuts',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 140/454},  # 140/454 = 0.3084 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
                {'from': 'pound', 'factor': 1},  # 1 lb = 1 package
            ],
            db=db
        )
        
        # Step 4: Add Raw Pecans
        print("\n--- Step 4: Adding Raw Pecans ---")
        create_ingredient_with_conversions(
            name='Raw Pecans',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 140/454},  # 140/454 = 0.3084 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
                {'from': 'pound', 'factor': 1},  # 1 lb = 1 package
            ],
            db=db
        )
        
        # Step 5: Add Raw Sesame Seeds
        print("\n--- Step 5: Adding Raw Sesame Seeds ---")
        create_ingredient_with_conversions(
            name='Raw Sesame Seeds',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 120/227},  # 120/227 = 0.5291 packages/cup
                {'from': 'gram', 'factor': 1/227},  # 1/227 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 1/8 = 0.125 packages/oz
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All Nutty Parm ingredients added successfully!")
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

