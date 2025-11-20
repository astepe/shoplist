#!/usr/bin/env python3
"""
Script to add ingredients for batch 4 recipes:
1. Savoy Cabbage
2. Fresh Sage
3. Buckwheat Noodles
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
                INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                VALUES (?, ?, ?, ?)
            """, (ingredient_id, from_unit_id, shopping_unit_id, rule['factor']))
            print(f"    ✓ Conversion: {rule['from']} → {shopping_unit_name}: {rule['factor']:.6f}")
        
        # Add size estimation rules
        if size_rules:
            for size_rule in size_rules:
                ref_unit_id = get_unit_id(size_rule['unit'], cursor)
                cursor.execute("""
                    INSERT INTO size_estimation_rules (ingredient_id, size_qualifier, reference_unit_id, reference_value)
                    VALUES (?, ?, ?, ?)
                """, (ingredient_id, size_rule['size'], ref_unit_id, size_rule['value']))
                print(f"    ✓ Size rule: {size_rule['size']} = {size_rule['value']} {size_rule['unit']}")
        
        db.commit()
        return ingredient_id
    
    finally:
        if close_after:
            db.close()

def main():
    """Main function to add all ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Ingredients for Batch 4 Recipes")
        print("=" * 60)
        
        # Step 1: Add Savoy Cabbage
        print("\n--- Step 1: Adding Savoy Cabbage ---")
        create_ingredient_with_conversions(
            name='Savoy Cabbage',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},
                {'from': 'cup', 'factor': 95/680},  # 95/680 = 0.140 heads/cup (shredded)
                {'from': 'gram', 'factor': 1/680},  # 1/680 = 0.00147 heads/g
                {'from': 'pound', 'factor': 453.6/680},  # 453.6/680 = 0.667 heads/lb
            ],
            db=db
        )
        
        # Step 2: Add Fresh Sage
        print("\n--- Step 2: Adding Fresh Sage ---")
        create_ingredient_with_conversions(
            name='Fresh Sage',
            type_name='Herbs',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'bunch', 'factor': 1.0},
                {'from': 'tablespoon', 'factor': 1/14},  # 1/14 = 0.0714 bunches/tbsp (minced)
                {'from': 'teaspoon', 'factor': 0.33/14},  # 0.33/14 = 0.0236 bunches/tsp (dried equivalent)
                {'from': 'whole', 'factor': 0.33/14},  # 0.33/14 = 0.0236 bunches/leaf (~0.33g per leaf)
                {'from': 'gram', 'factor': 1/14},  # 1/14 = 0.0714 bunches/g
            ],
            db=db
        )
        
        # Step 3: Add Buckwheat Noodles
        print("\n--- Step 3: Adding Buckwheat Noodles ---")
        create_ingredient_with_conversions(
            name='Buckwheat Noodles',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1 package = 1 box/bag
                {'from': 'gram', 'factor': 1/225},  # 1/225 = 0.00444 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 1/8 = 0.125 packages/oz
                {'from': 'pound', 'factor': 1/0.5},  # 1/0.5 = 2 packages/lb
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All ingredients added successfully!")
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

