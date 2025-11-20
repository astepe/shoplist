#!/usr/bin/env python3
"""
Script to add ingredients for Savory Spice Blend 2.0 recipe.
This script adds:
1. Nutritional Yeast
2. Onion Powder
3. Garlic Powder
4. Ground Paprika
5. Ground Black Cumin (Nigella Seeds)
6. Ground Ginger
7. Ground Thyme
8. Mustard Powder
9. Ground Turmeric
10. Celery Seeds
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
    """Main function to add all Savory Spice Blend ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Ingredients for Savory Spice Blend 2.0")
        print("=" * 60)
        
        # Step 1: Add Nutritional Yeast
        print("\n--- Step 1: Adding Nutritional Yeast ---")
        create_ingredient_with_conversions(
            name='Nutritional Yeast',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/23.33},  # 1/23.33 = 0.04286 packages/tbsp
                {'from': 'cup', 'factor': 1/2},  # 1/2 = 0.5 packages/cup
                {'from': 'gram', 'factor': 1/140},  # 1/140 packages/g
                {'from': 'ounce', 'factor': 1/5},  # 1/5 = 0.2 packages/oz
            ],
            db=db
        )
        
        # Step 2: Add Onion Powder
        print("\n--- Step 2: Adding Onion Powder ---")
        create_ingredient_with_conversions(
            name='Onion Powder',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/6.33},  # 1/6.33 = 0.1579 packages/tbsp
                {'from': 'teaspoon', 'factor': 1/19},  # 1/19 = 0.05263 packages/tsp
                {'from': 'gram', 'factor': 1/57},  # 1/57 packages/g
                {'from': 'ounce', 'factor': 1/2},  # 1/2 = 0.5 packages/oz
            ],
            db=db
        )
        
        # Step 3: Add Garlic Powder
        print("\n--- Step 3: Adding Garlic Powder ---")
        create_ingredient_with_conversions(
            name='Garlic Powder',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/5.43},  # 1/5.43 = 0.1842 packages/tbsp
                {'from': 'teaspoon', 'factor': 1/16.29},  # 1/16.29 = 0.0614 packages/tsp
                {'from': 'gram', 'factor': 1/57},  # 1/57 packages/g
                {'from': 'ounce', 'factor': 1/2},  # 1/2 = 0.5 packages/oz
            ],
            db=db
        )
        
        # Step 4: Add Ground Paprika
        print("\n--- Step 4: Adding Ground Paprika ---")
        create_ingredient_with_conversions(
            name='Ground Paprika',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/7.6},  # 1/7.6 = 0.1316 packages/tbsp
                {'from': 'teaspoon', 'factor': 1/22.8},  # 1/22.8 = 0.04386 packages/tsp
                {'from': 'gram', 'factor': 1/57},  # 1/57 packages/g
                {'from': 'ounce', 'factor': 1/2},  # 1/2 = 0.5 packages/oz
            ],
            db=db
        )
        
        # Step 5: Add Ground Black Cumin (Nigella Seeds)
        print("\n--- Step 5: Adding Ground Black Cumin (Nigella Seeds) ---")
        create_ingredient_with_conversions(
            name='Ground Black Cumin (Nigella Seeds)',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/11.2},  # 1/11.2 = 0.08929 packages/tsp
                {'from': 'gram', 'factor': 1/28},  # 1/28 packages/g
                {'from': 'ounce', 'factor': 1/1},  # 1 oz = 1 package
            ],
            db=db
        )
        
        # Step 6: Add Ground Ginger
        print("\n--- Step 6: Adding Ground Ginger ---")
        create_ingredient_with_conversions(
            name='Ground Ginger',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/11.2},  # 1/11.2 = 0.08929 packages/tsp
                {'from': 'gram', 'factor': 1/28},  # 1/28 packages/g
                {'from': 'ounce', 'factor': 1/1},  # 1 oz = 1 package
            ],
            db=db
        )
        
        # Step 7: Add Ground Thyme
        print("\n--- Step 7: Adding Ground Thyme ---")
        create_ingredient_with_conversions(
            name='Ground Thyme',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/11.67},  # 1/11.67 = 0.08571 packages/tsp
                {'from': 'gram', 'factor': 1/14},  # 1/14 packages/g
                {'from': 'ounce', 'factor': 1/0.5},  # 1/0.5 = 2 packages/oz
            ],
            db=db
        )
        
        # Step 8: Add Mustard Powder
        print("\n--- Step 8: Adding Mustard Powder ---")
        create_ingredient_with_conversions(
            name='Mustard Powder',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/11.2},  # 1/11.2 = 0.08929 packages/tsp
                {'from': 'gram', 'factor': 1/28},  # 1/28 packages/g
                {'from': 'ounce', 'factor': 1/1},  # 1 oz = 1 package
            ],
            db=db
        )
        
        # Step 9: Add Ground Turmeric
        print("\n--- Step 9: Adding Ground Turmeric ---")
        create_ingredient_with_conversions(
            name='Ground Turmeric',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/11.2},  # 1/11.2 = 0.08929 packages/tsp
                {'from': 'gram', 'factor': 1/28},  # 1/28 packages/g
                {'from': 'ounce', 'factor': 1/1},  # 1 oz = 1 package
            ],
            db=db
        )
        
        # Step 10: Add Celery Seeds
        print("\n--- Step 10: Adding Celery Seeds ---")
        create_ingredient_with_conversions(
            name='Celery Seeds',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/11.2},  # 1/11.2 = 0.08929 packages/tsp
                {'from': 'gram', 'factor': 1/28},  # 1/28 packages/g
                {'from': 'ounce', 'factor': 1/1},  # 1 oz = 1 package
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All Savory Spice Blend ingredients added successfully!")
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

