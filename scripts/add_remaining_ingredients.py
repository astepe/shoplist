#!/usr/bin/env python3
"""
Script to add remaining ingredients for Balsamic Syrup, Date Syrup 2.0, and other recipes.
This script adds:
1. Balsamic Vinegar
2. Pitted Dates
3. Water
4. Pippali (Long Pepper)
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
    """Main function to add all remaining ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Remaining Ingredients")
        print("=" * 60)
        
        # Step 1: Add Balsamic Vinegar
        print("\n--- Step 1: Adding Balsamic Vinegar ---")
        create_ingredient_with_conversions(
            name='Balsamic Vinegar',
            type_name='Pantry Items',
            shopping_unit_name='bottle',
            conversion_rules=[
                {'from': 'cup', 'factor': 235/500},  # 235/500 = 0.47 bottles/cup
                {'from': 'tablespoon', 'factor': 1/42.55},  # 1/42.55 = 0.0235 bottles/tbsp
                {'from': 'milliliter', 'factor': 1/500},  # 1/500 bottles/ml
                {'from': 'fluid_ounce', 'factor': 1/16.9},  # 1/16.9 = 0.0592 bottles/fl oz
            ],
            db=db
        )
        
        # Step 2: Add Pitted Dates
        print("\n--- Step 2: Adding Pitted Dates ---")
        create_ingredient_with_conversions(
            name='Pitted Dates',
            type_name='Fruits',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 135/454},  # 135/454 = 0.2974 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
                {'from': 'pound', 'factor': 1},  # 1 lb = 1 package
            ],
            db=db
        )
        
        # Step 3: Add Water
        print("\n--- Step 3: Adding Water ---")
        create_ingredient_with_conversions(
            name='Water',
            type_name='Liquids',
            shopping_unit_name='cup',
            conversion_rules=[
                {'from': 'cup', 'factor': 1.0},  # 1 cup = 1 cup
                {'from': 'milliliter', 'factor': 0.00423},  # 1 ml = 0.00423 cups
                {'from': 'liter', 'factor': 4.2268},  # 1 L = 4.2268 cups
                {'from': 'fluid_ounce', 'factor': 0.125},  # 1 fl oz = 0.125 cups
                {'from': 'tablespoon', 'factor': 1/16},  # 1 tbsp = 0.0625 cups
                {'from': 'teaspoon', 'factor': 1/48},  # 1 tsp = 0.02083 cups
            ],
            db=db
        )
        
        # Step 4: Add Pippali (Long Pepper)
        print("\n--- Step 4: Adding Pippali (Long Pepper) ---")
        create_ingredient_with_conversions(
            name='Pippali (Long Pepper)',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/14},  # 1/14 = 0.07143 packages/tsp
                {'from': 'gram', 'factor': 1/28},  # 1/28 packages/g
                {'from': 'ounce', 'factor': 1/1},  # 1 oz = 1 package
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All remaining ingredients added successfully!")
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

