#!/usr/bin/env python3
"""
Script to add ingredients for batch 8 recipes:
1. Salt-Free Tomato Sauce
2. Whole-Grain Salt-Free Tortillas
3. Dried Marjoram
4. Filé Powder
5. Soy Curls
6. Dried Savory
7. Salt-Free Great Northern Beans
8. Salt-Free Cannellini Beans
9. Ground Fenugreek Seeds
10. Chile Pepper
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
        print("Adding Ingredients for Batch 8 Recipes")
        print("=" * 60)
        
        # Step 1: Salt-Free Tomato Sauce
        print("\n--- Step 1: Adding Salt-Free Tomato Sauce ---")
        create_ingredient_with_conversions(
            name='Salt-Free Tomato Sauce',
            type_name='Pantry Items',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'can', 'factor': 1.0},  # 1.0 (15 oz / 400g)
                {'from': 'cup', 'factor': 1/15 * 8},  # ~0.5333 cans/cup (estimate 1 cup = ~8 oz)
                {'from': 'gram', 'factor': 1/400},  # 0.0025 cans/g
                {'from': 'ounce', 'factor': 1/15},  # 0.0667 cans/oz
            ],
            db=db
        )
        
        # Step 2: Whole-Grain Salt-Free Tortillas
        print("\n--- Step 2: Adding Whole-Grain Salt-Free Tortillas ---")
        create_ingredient_with_conversions(
            name='Whole-Grain Salt-Free Tortillas',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (8 tortillas per package)
                {'from': 'whole', 'factor': 1/8},  # 0.125 packages/whole
            ],
            db=db
        )
        
        # Step 3: Dried Marjoram
        print("\n--- Step 3: Adding Dried Marjoram ---")
        create_ingredient_with_conversions(
            name='Dried Marjoram',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 oz / 28g package)
                {'from': 'teaspoon', 'factor': 1/50},  # 0.02 packages/tsp (estimate)
                {'from': 'tablespoon', 'factor': 1/16.67},  # 0.06 packages/tbsp (estimate)
                {'from': 'gram', 'factor': 1/28},  # 0.0357 packages/g
            ],
            db=db
        )
        
        # Step 4: Filé Powder
        print("\n--- Step 4: Adding Filé Powder ---")
        create_ingredient_with_conversions(
            name='Filé Powder',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 oz / 28g package, optional ingredient)
                {'from': 'teaspoon', 'factor': 1/50},  # 0.02 packages/tsp (estimate)
                {'from': 'gram', 'factor': 1/28},  # 0.0357 packages/g
            ],
            db=db
        )
        
        # Step 5: Soy Curls
        print("\n--- Step 5: Adding Soy Curls ---")
        create_ingredient_with_conversions(
            name='Soy Curls',
            type_name='Plant Proteins',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (8 oz / 226.8g package)
                {'from': 'ounce', 'factor': 1/8},  # 0.125 packages/oz
                {'from': 'gram', 'factor': 1/226.8},  # 0.00441 packages/g
            ],
            db=db
        )
        
        # Step 6: Dried Savory
        print("\n--- Step 6: Adding Dried Savory ---")
        create_ingredient_with_conversions(
            name='Dried Savory',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 oz / 28g package)
                {'from': 'teaspoon', 'factor': 1/50},  # 0.02 packages/tsp (estimate)
                {'from': 'gram', 'factor': 1/28},  # 0.0357 packages/g
            ],
            db=db
        )
        
        # Step 7: Salt-Free Great Northern Beans
        print("\n--- Step 7: Adding Salt-Free Great Northern Beans ---")
        create_ingredient_with_conversions(
            name='Salt-Free Great Northern Beans',
            type_name='Plant Proteins',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'can', 'factor': 1.0},  # 1.0 (15 oz / 425g)
                {'from': 'cup', 'factor': 1/1.75},  # 0.571 cans/cup (estimate)
                {'from': 'gram', 'factor': 1/425},  # 0.00235 cans/g
                {'from': 'ounce', 'factor': 1/15},  # 0.0667 cans/oz
            ],
            db=db
        )
        
        # Step 8: Salt-Free Cannellini Beans
        print("\n--- Step 8: Adding Salt-Free Cannellini Beans ---")
        create_ingredient_with_conversions(
            name='Salt-Free Cannellini Beans',
            type_name='Plant Proteins',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'can', 'factor': 1.0},  # 1.0 (15 oz / 425g)
                {'from': 'cup', 'factor': 1/1.75},  # 0.571 cans/cup (estimate)
                {'from': 'gram', 'factor': 1/425},  # 0.00235 cans/g
                {'from': 'ounce', 'factor': 1/15},  # 0.0667 cans/oz
            ],
            db=db
        )
        
        # Step 9: Ground Fenugreek Seeds
        print("\n--- Step 9: Adding Ground Fenugreek Seeds ---")
        create_ingredient_with_conversions(
            name='Ground Fenugreek Seeds',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 oz / 28g package, optional ingredient)
                {'from': 'teaspoon', 'factor': 1/50},  # 0.02 packages/tsp (estimate)
                {'from': 'gram', 'factor': 1/28},  # 0.0357 packages/g
            ],
            db=db
        )
        
        # Step 10: Chile Pepper
        print("\n--- Step 10: Adding Chile Pepper ---")
        create_ingredient_with_conversions(
            name='Chile Pepper',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0
            ],
            db=db
        )
        
        # Step 11: Green Lentils
        print("\n--- Step 11: Adding Green Lentils ---")
        create_ingredient_with_conversions(
            name='Green Lentils',
            type_name='Plant Proteins',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (16 oz / 454g package)
                {'from': 'cup', 'factor': 1/3.13},  # 0.319 packages/cup (145g dry per 0.75 cup, ~3.13 cups per 454g package)
                {'from': 'gram', 'factor': 1/454},  # 0.00220 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
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

