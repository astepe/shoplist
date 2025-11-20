#!/usr/bin/env python3
"""
Script to add pantry/grain ingredients for new batch recipes:
1. Tahini
2. Salt-Free Pinto Beans
3. Oat Flour
4. Dried Wakame Seaweed
5. Purple Sweet Potato
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
    """Main function to add all pantry/grain ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Pantry/Grain Ingredients for New Batch Recipes")
        print("=" * 60)
        
        # Step 1: Add Tahini
        print("\n--- Step 1: Adding Tahini ---")
        create_ingredient_with_conversions(
            name='Tahini',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/30.27},  # 1/30.27 = 0.0330 packages/tbsp (15g/tbsp)
                {'from': 'cup', 'factor': 240/454},  # 240/454 = 0.529 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'fluid_ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/fl oz
            ],
            db=db
        )
        
        # Step 2: Add Salt-Free Pinto Beans
        print("\n--- Step 2: Adding Salt-Free Pinto Beans ---")
        create_ingredient_with_conversions(
            name='Salt-Free Pinto Beans',
            type_name='Plant Proteins',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'cup', 'factor': 165/425},  # 165/425 = 0.388 cans/cup
                {'from': 'gram', 'factor': 1/425},  # 1/425 cans/g
                {'from': 'ounce', 'factor': 1/15},  # 1/15 = 0.0667 cans/oz
            ],
            db=db
        )
        
        # Step 3: Add Oat Flour
        print("\n--- Step 3: Adding Oat Flour ---")
        create_ingredient_with_conversions(
            name='Oat Flour',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 120/454},  # 120/454 = 0.264 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 4: Add Dried Wakame Seaweed
        print("\n--- Step 4: Adding Dried Wakame Seaweed ---")
        create_ingredient_with_conversions(
            name='Dried Wakame Seaweed',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/14},  # 1/14 = 0.0714 packages/tbsp
                {'from': 'gram', 'factor': 1/28},  # 1/28 packages/g
                {'from': 'ounce', 'factor': 1.0},  # 1 package/oz
            ],
            db=db
        )
        
        # Step 5: Add Purple Sweet Potato
        print("\n--- Step 5: Adding Purple Sweet Potato ---")
        create_ingredient_with_conversions(
            name='Purple Sweet Potato',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'cup', 'factor': 200/200},  # 200/200 = 1.0 whole/cup (mashed)
                {'from': 'gram', 'factor': 1/200},  # 1/200 = 0.005 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 150},
                {'size': 'medium', 'unit': 'gram', 'value': 200},
                {'size': 'large', 'unit': 'gram', 'value': 250},
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All pantry/grain ingredients added successfully!")
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

