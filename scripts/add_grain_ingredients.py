#!/usr/bin/env python3
"""
Script to add grain and grain-related ingredients:
1. Buckwheat Groats
2. Medium Bulgur
3. Whole-Grain Millet
4. Chickpea Flour
5. Pumpkin Pie Spice
6. Pepitas (Pumpkin Seeds)
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
    """Main function to add all grain ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Grain Ingredients")
        print("=" * 60)
        
        # Step 1: Add Buckwheat Groats
        print("\n--- Step 1: Adding Buckwheat Groats ---")
        create_ingredient_with_conversions(
            name='Buckwheat Groats',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 155/454},  # 155/454 = 0.341 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
                {'from': 'pound', 'factor': 1.0},  # 1 package/lb
            ],
            db=db
        )
        
        # Step 2: Add Medium Bulgur
        print("\n--- Step 2: Adding Medium Bulgur ---")
        create_ingredient_with_conversions(
            name='Medium Bulgur',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 140/454},  # 140/454 = 0.308 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 3: Add Whole-Grain Millet
        print("\n--- Step 3: Adding Whole-Grain Millet ---")
        create_ingredient_with_conversions(
            name='Whole-Grain Millet',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 190/454},  # 190/454 = 0.418 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 4: Add Chickpea Flour
        print("\n--- Step 4: Adding Chickpea Flour ---")
        create_ingredient_with_conversions(
            name='Chickpea Flour',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 90/454},  # 90/454 = 0.198 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 5: Add Pumpkin Pie Spice
        print("\n--- Step 5: Adding Pumpkin Pie Spice ---")
        create_ingredient_with_conversions(
            name='Pumpkin Pie Spice',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/11.2},  # 1/11.2 = 0.0893 packages/tsp
                {'from': 'gram', 'factor': 1/28},  # 1/28 packages/g
                {'from': 'ounce', 'factor': 1.0},  # 1 package/oz
            ],
            db=db
        )
        
        # Step 6: Add Pepitas (Pumpkin Seeds)
        print("\n--- Step 6: Adding Pepitas (Pumpkin Seeds) ---")
        create_ingredient_with_conversions(
            name='Pepitas (Pumpkin Seeds)',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/28.38},  # 1/28.38 = 0.0352 packages/tbsp
                {'from': 'gram', 'factor': 1/227},  # 1/227 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 1/8 = 0.125 packages/oz
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All grain ingredients added successfully!")
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

