#!/usr/bin/env python3
"""
Script to add smoothie recipe ingredients:
1. Dried Barberries
2. Frozen Chopped Mango
3. Frozen Blackberries
4. Almond Butter
5. Sweet Potato
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
    """Main function to add all smoothie ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Smoothie Recipe Ingredients")
        print("=" * 60)
        
        # Step 1: Add Dried Barberries
        print("\n--- Step 1: Adding Dried Barberries ---")
        create_ingredient_with_conversions(
            name='Dried Barberries',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/14.13},  # 1/14.13 = 0.0708 packages/tbsp
                {'from': 'gram', 'factor': 1/113},  # 1/113 packages/g
                {'from': 'ounce', 'factor': 1/4},  # 1/4 = 0.25 packages/oz
            ],
            db=db
        )
        
        # Step 2: Add Frozen Chopped Mango
        print("\n--- Step 2: Adding Frozen Chopped Mango ---")
        create_ingredient_with_conversions(
            name='Frozen Chopped Mango',
            type_name='Fruits',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 140/454},  # 140/454 = 0.308 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 3: Add Frozen Blackberries
        print("\n--- Step 3: Adding Frozen Blackberries ---")
        create_ingredient_with_conversions(
            name='Frozen Blackberries',
            type_name='Fruits',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 130/454},  # 130/454 = 0.286 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 4: Add Almond Butter
        print("\n--- Step 4: Adding Almond Butter ---")
        create_ingredient_with_conversions(
            name='Almond Butter',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/28.38},  # 1/28.38 = 0.0352 packages/tbsp
                {'from': 'cup', 'factor': 250/454},  # 250/454 = 0.551 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'fluid_ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/fl oz
            ],
            db=db
        )
        
        # Step 5: Add Sweet Potato
        print("\n--- Step 5: Adding Sweet Potato ---")
        create_ingredient_with_conversions(
            name='Sweet Potato',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'cup', 'factor': 200/200},  # 200/200 = 1.0 whole/cup (mashed, medium)
                {'from': 'gram', 'factor': 1/200},  # 1/200 = 0.005 whole/g (mashed, medium)
                {'from': 'whole', 'factor': 1.0},
                {'from': 'piece', 'factor': 1.0},
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 150},
                {'size': 'medium', 'unit': 'gram', 'value': 200},
                {'size': 'large', 'unit': 'gram', 'value': 250},
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All smoothie ingredients added successfully!")
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

