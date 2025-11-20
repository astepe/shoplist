#!/usr/bin/env python3
"""
Script to add ingredients for Umami Sauce 2.0 recipe.
This script adds:
1. Blackstrap Molasses
2. Salt-Free Tomato Paste
3. Apple Cider Vinegar
4. Lemon (for fresh lemon juice)
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
            print(f"    ✓ Conversion: {rule['from']} → {shopping_unit_name}: {rule['factor']}")
        
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
    """Main function to add all Umami Sauce ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Ingredients for Umami Sauce 2.0")
        print("=" * 60)
        
        # Step 1: Add Blackstrap Molasses
        print("\n--- Step 1: Adding Blackstrap Molasses ---")
        create_ingredient_with_conversions(
            name='Blackstrap Molasses',
            type_name='Pantry Items',
            shopping_unit_name='bottle',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/24},  # 1/24 = 0.04167 bottles/tbsp
                {'from': 'cup', 'factor': 1/1.5},  # 1/1.5 = 0.6667 bottles/cup
                {'from': 'fluid_ounce', 'factor': 1/12},  # 1/12 = 0.0833 bottles/fl oz
                {'from': 'milliliter', 'factor': 1/355},  # 1/355 bottles/ml
                {'from': 'gram', 'factor': 1/480},  # 1/480 bottles/g
            ],
            db=db
        )
        
        # Step 2: Add Salt-Free Tomato Paste
        print("\n--- Step 2: Adding Salt-Free Tomato Paste ---")
        create_ingredient_with_conversions(
            name='Salt-Free Tomato Paste',
            type_name='Pantry Items',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/11.33},  # 1/11.33 = 0.08826 cans/tbsp
                {'from': 'teaspoon', 'factor': 1/34},  # 1/34 = 0.02941 cans/tsp
                {'from': 'gram', 'factor': 1/170},  # 1/170 cans/g
                {'from': 'ounce', 'factor': 1/6},  # 1/6 = 0.1667 cans/oz
            ],
            db=db
        )
        
        # Step 3: Add Apple Cider Vinegar
        print("\n--- Step 3: Adding Apple Cider Vinegar ---")
        create_ingredient_with_conversions(
            name='Apple Cider Vinegar',
            type_name='Pantry Items',
            shopping_unit_name='bottle',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/32},  # 1/32 = 0.03125 bottles/tbsp
                {'from': 'cup', 'factor': 1/2},  # 1/2 = 0.5 bottles/cup
                {'from': 'fluid_ounce', 'factor': 1/16},  # 1/16 = 0.0625 bottles/fl oz
                {'from': 'milliliter', 'factor': 1/473},  # 1/473 bottles/ml
                {'from': 'gram', 'factor': 1/473},  # 1/473 bottles/g
            ],
            db=db
        )
        
        # Step 4: Add Lemon
        print("\n--- Step 4: Adding Lemon ---")
        create_ingredient_with_conversions(
            name='Lemon',
            type_name='Fruits',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 0.4},  # 0.4 whole/tbsp (assuming medium)
                {'from': 'teaspoon', 'factor': 0.1333},  # 0.1333 whole/tsp
                {'from': 'milliliter', 'factor': 0.0267},  # 0.0267 whole/ml (37.5ml per lemon)
                {'from': 'whole', 'factor': 1.0},
                {'from': 'piece', 'factor': 1.0},
            ],
            size_rules=[
                {'size': 'small', 'unit': 'milliliter', 'value': 25},  # ~2 tbsp juice
                {'size': 'medium', 'unit': 'milliliter', 'value': 37.5},  # ~2.5 tbsp juice
                {'size': 'large', 'unit': 'milliliter', 'value': 50},  # ~3 tbsp juice
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All Umami Sauce ingredients added successfully!")
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

