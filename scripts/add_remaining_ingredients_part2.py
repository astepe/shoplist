#!/usr/bin/env python3
"""
Script to add remaining ingredients:
1. Whole-Grain Bread Crumbs
2. Whole-Grain Tortillas
3. Tempeh
4. Salt-Free Chickpeas
5. Aluminum- and Sodium-Free Baking Powder
6. Ground Fennel Seeds
7. Dried Basil
8. Smoked Paprika
9. Dried Oregano
10. Chili Powder
11. Salt-Free Whole-Grain Sprouted Bread
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
        print("Adding Remaining Ingredients (Part 2)")
        print("=" * 60)
        
        # Step 1: Add Whole-Grain Bread Crumbs
        print("\n--- Step 1: Adding Whole-Grain Bread Crumbs ---")
        create_ingredient_with_conversions(
            name='Whole-Grain Bread Crumbs',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 100/425},  # 100/425 = 0.235 packages/cup
                {'from': 'gram', 'factor': 1/425},  # 1/425 packages/g
                {'from': 'ounce', 'factor': 1/15},  # 1/15 = 0.0667 packages/oz
            ],
            db=db
        )
        
        # Step 2: Add Whole-Grain Tortillas
        print("\n--- Step 2: Adding Whole-Grain Tortillas ---")
        create_ingredient_with_conversions(
            name='Whole-Grain Tortillas',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'whole', 'factor': 1/8},  # 1/8 = 0.125 packages/whole
                {'from': 'piece', 'factor': 1/8},  # 1/8 = 0.125 packages/piece
            ],
            db=db
        )
        
        # Step 3: Add Tempeh
        print("\n--- Step 3: Adding Tempeh ---")
        create_ingredient_with_conversions(
            name='Tempeh',
            type_name='Plant Proteins',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'gram', 'factor': 1/230},  # 1/230 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 1/8 = 0.125 packages/oz
            ],
            db=db
        )
        
        # Step 4: Add Salt-Free Chickpeas
        print("\n--- Step 4: Adding Salt-Free Chickpeas ---")
        create_ingredient_with_conversions(
            name='Salt-Free Chickpeas',
            type_name='Plant Proteins',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'cup', 'factor': 165/425},  # 165/425 = 0.388 cans/cup
                {'from': 'gram', 'factor': 1/425},  # 1/425 cans/g
                {'from': 'ounce', 'factor': 1/15},  # 1/15 = 0.0667 cans/oz
            ],
            db=db
        )
        
        # Step 5: Add Aluminum- and Sodium-Free Baking Powder
        print("\n--- Step 5: Adding Aluminum- and Sodium-Free Baking Powder ---")
        create_ingredient_with_conversions(
            name='Aluminum- and Sodium-Free Baking Powder',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/28.25},  # 1/28.25 = 0.0354 packages/tsp
                {'from': 'gram', 'factor': 1/113},  # 1/113 packages/g
                {'from': 'ounce', 'factor': 1/4},  # 1/4 = 0.25 packages/oz
            ],
            db=db
        )
        
        # Step 6: Add Ground Fennel Seeds
        print("\n--- Step 6: Adding Ground Fennel Seeds ---")
        create_ingredient_with_conversions(
            name='Ground Fennel Seeds',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/14},  # 1/14 = 0.0714 packages/tsp
                {'from': 'gram', 'factor': 1/28},  # 1/28 packages/g
                {'from': 'ounce', 'factor': 1.0},  # 1 package/oz
            ],
            db=db
        )
        
        # Step 7: Add Dried Basil
        print("\n--- Step 7: Adding Dried Basil ---")
        create_ingredient_with_conversions(
            name='Dried Basil',
            type_name='Herbs',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/14},  # 1/14 = 0.0714 packages/tsp
                {'from': 'gram', 'factor': 1/14},  # 1/14 packages/g
                {'from': 'ounce', 'factor': 1/0.5},  # 1/0.5 = 2 packages/oz
            ],
            db=db
        )
        
        # Step 8: Add Smoked Paprika
        print("\n--- Step 8: Adding Smoked Paprika ---")
        create_ingredient_with_conversions(
            name='Smoked Paprika',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/22.8},  # 1/22.8 = 0.0439 packages/tsp
                {'from': 'gram', 'factor': 1/57},  # 1/57 packages/g
                {'from': 'ounce', 'factor': 1/2},  # 1/2 = 0.5 packages/oz
            ],
            db=db
        )
        
        # Step 9: Add Dried Oregano
        print("\n--- Step 9: Adding Dried Oregano ---")
        create_ingredient_with_conversions(
            name='Dried Oregano',
            type_name='Herbs',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/14},  # 1/14 = 0.0714 packages/tsp
                {'from': 'gram', 'factor': 1/14},  # 1/14 packages/g
                {'from': 'ounce', 'factor': 1/0.5},  # 1/0.5 = 2 packages/oz
            ],
            db=db
        )
        
        # Step 10: Add Chili Powder
        print("\n--- Step 10: Adding Chili Powder ---")
        create_ingredient_with_conversions(
            name='Chili Powder',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/22.8},  # 1/22.8 = 0.0439 packages/tsp
                {'from': 'gram', 'factor': 1/57},  # 1/57 packages/g
                {'from': 'ounce', 'factor': 1/2},  # 1/2 = 0.5 packages/oz
            ],
            db=db
        )
        
        # Step 11: Add Salt-Free Whole-Grain Sprouted Bread
        print("\n--- Step 11: Adding Salt-Free Whole-Grain Sprouted Bread ---")
        create_ingredient_with_conversions(
            name='Salt-Free Whole-Grain Sprouted Bread',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1 package = 1 loaf
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
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

