#!/usr/bin/env python3
"""
Script to add ingredients for batch 6 recipes:
22 new ingredients total
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
        print("Adding Ingredients for Batch 6 Recipes")
        print("=" * 60)
        
        # Step 1: Whole-Grain Elbow Macaroni
        print("\n--- Step 1: Adding Whole-Grain Elbow Macaroni ---")
        create_ingredient_with_conversions(
            name='Whole-Grain Elbow Macaroni',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (16 oz)
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
                {'from': 'pound', 'factor': 1/1},  # 1.0 packages/lb
            ],
            db=db
        )
        
        # Step 2: Whole-Grain Angel Hair Pasta
        print("\n--- Step 2: Adding Whole-Grain Angel Hair Pasta ---")
        create_ingredient_with_conversions(
            name='Whole-Grain Angel Hair Pasta',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (16 oz)
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
                {'from': 'pound', 'factor': 1/1},  # 1.0 packages/lb
            ],
            db=db
        )
        
        # Step 3: Green Beans
        print("\n--- Step 3: Adding Green Beans ---")
        create_ingredient_with_conversions(
            name='Green Beans',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 lb package)
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
                {'from': 'pound', 'factor': 1/1},  # 1.0 packages/lb
            ],
            db=db
        )
        
        # Step 4: Green Cabbage
        print("\n--- Step 4: Adding Green Cabbage ---")
        create_ingredient_with_conversions(
            name='Green Cabbage',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},  # 1.0 (~680g per head)
                {'from': 'cup', 'factor': 95/680},  # ~0.140 heads/cup (shredded)
                {'from': 'gram', 'factor': 1/680},  # 0.00147 heads/g
                {'from': 'pound', 'factor': 453.6/680},  # 0.667 heads/lb
            ],
            db=db
        )
        
        # Step 5: Sodium-Free Salt Substitute
        print("\n--- Step 5: Adding Sodium-Free Salt Substitute ---")
        create_ingredient_with_conversions(
            name='Sodium-Free Salt Substitute',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (small package)
                {'from': 'teaspoon', 'factor': 1/100},  # ~100 tsp per package
                {'from': 'gram', 'factor': 1/200},  # ~200g per package
            ],
            db=db
        )
        
        # Step 6: Black Rice
        print("\n--- Step 6: Adding Black Rice ---")
        create_ingredient_with_conversions(
            name='Black Rice',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 lb package)
                {'from': 'cup', 'factor': 135/454},  # 0.297 packages/cup (~135g per cup dry)
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
            ],
            db=db
        )
        
        # Step 7: Yellow Curry Powder
        print("\n--- Step 7: Adding Yellow Curry Powder ---")
        create_ingredient_with_conversions(
            name='Yellow Curry Powder',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (small spice jar)
                {'from': 'teaspoon', 'factor': 1/30},  # ~30 tsp per jar
                {'from': 'gram', 'factor': 1/60},  # ~60g per jar
            ],
            db=db
        )
        
        # Step 8: Ground Cayenne
        print("\n--- Step 8: Adding Ground Cayenne ---")
        create_ingredient_with_conversions(
            name='Ground Cayenne',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (small spice jar)
                {'from': 'teaspoon', 'factor': 1/25},  # ~25 tsp per jar
                {'from': 'gram', 'factor': 1/28},  # ~28g per jar
            ],
            db=db
        )
        
        # Step 9: Fresh Turmeric
        print("\n--- Step 9: Adding Fresh Turmeric ---")
        create_ingredient_with_conversions(
            name='Fresh Turmeric',
            type_name='Spices',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0 (~15g per piece)
                {'from': 'gram', 'factor': 1/15},  # 0.0667 whole/g
                {'from': 'pound', 'factor': 453.6/15},  # 30.24 whole/lb
            ],
            db=db
        )
        
        # Step 10: Purple Sweet Potatoes
        print("\n--- Step 10: Adding Purple Sweet Potatoes ---")
        create_ingredient_with_conversions(
            name='Purple Sweet Potatoes',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0 (medium sweet potato ~300g)
                {'from': 'gram', 'factor': 1/300},  # 0.00333 whole/g
                {'from': 'pound', 'factor': 453.6/300},  # 1.512 whole/lb
                {'from': 'cup', 'factor': 1/2},  # ~2 cups diced per medium sweet potato
            ],
            db=db
        )
        
        # Step 11: Pine Nuts
        print("\n--- Step 11: Adding Pine Nuts ---")
        create_ingredient_with_conversions(
            name='Pine Nuts',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (small package ~100g)
                {'from': 'cup', 'factor': 1/2},  # ~2 cups per 100g package
                {'from': 'gram', 'factor': 1/100},  # 0.01 packages/g
                {'from': 'ounce', 'factor': 1/3.5},  # ~3.5 oz package
            ],
            db=db
        )
        
        # Step 12: Creamy Peanut Butter
        print("\n--- Step 12: Adding Creamy Peanut Butter ---")
        create_ingredient_with_conversions(
            name='Creamy Peanut Butter',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (16 oz jar)
                {'from': 'cup', 'factor': 1/2},  # ~2 cups per jar
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 13: Beets
        print("\n--- Step 13: Adding Beets ---")
        create_ingredient_with_conversions(
            name='Beets',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0 (medium beet ~150g)
                {'from': 'gram', 'factor': 1/150},  # 0.00667 whole/g
                {'from': 'pound', 'factor': 453.6/150},  # 3.024 whole/lb
                {'from': 'cup', 'factor': 1/2},  # ~2 cups diced per medium beet
            ],
            db=db
        )
        
        # Step 14: Brussels Sprouts
        print("\n--- Step 14: Adding Brussels Sprouts ---")
        create_ingredient_with_conversions(
            name='Brussels Sprouts',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 lb package)
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
                {'from': 'whole', 'factor': 1/20},  # ~20 sprouts per lb package
            ],
            db=db
        )
        
        # Step 15: Kabocha Squash
        print("\n--- Step 15: Adding Kabocha Squash ---")
        create_ingredient_with_conversions(
            name='Kabocha Squash',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0 (small squash ~1.5 lb)
                {'from': 'gram', 'factor': 1/680},  # 0.00147 whole/g
                {'from': 'pound', 'factor': 1/1.5},  # 0.667 whole/lb (small squash)
            ],
            db=db
        )
        
        # Step 16: Napa Cabbage
        print("\n--- Step 16: Adding Napa Cabbage ---")
        create_ingredient_with_conversions(
            name='Napa Cabbage',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},  # 1.0 (~800g per head)
                {'from': 'cup', 'factor': 1/6},  # ~6 cups shredded per head
                {'from': 'gram', 'factor': 1/800},  # 0.00125 heads/g
                {'from': 'pound', 'factor': 453.6/800},  # 0.567 heads/lb
            ],
            db=db
        )
        
        # Step 17: Unsalted Peanuts
        print("\n--- Step 17: Adding Unsalted Peanuts ---")
        create_ingredient_with_conversions(
            name='Unsalted Peanuts',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (16 oz package)
                {'from': 'cup', 'factor': 1/2},  # ~2 cups per package
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 18: Soba Noodles
        print("\n--- Step 18: Adding Soba Noodles ---")
        create_ingredient_with_conversions(
            name='Soba Noodles',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (8 oz package)
                {'from': 'gram', 'factor': 1/225},  # 0.00444 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 0.125 packages/oz
            ],
            db=db
        )
        
        # Step 19: Snow Peas
        print("\n--- Step 19: Adding Snow Peas ---")
        create_ingredient_with_conversions(
            name='Snow Peas',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 lb package)
                {'from': 'cup', 'factor': 1/2},  # ~2 cups per lb
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 20: Bok Choy
        print("\n--- Step 20: Adding Bok Choy ---")
        create_ingredient_with_conversions(
            name='Bok Choy',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},  # 1.0 (~400g per head)
                {'from': 'cup', 'factor': 1/4},  # ~4 cups shredded per head
                {'from': 'gram', 'factor': 1/400},  # 0.0025 heads/g
                {'from': 'pound', 'factor': 453.6/400},  # 1.134 heads/lb
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

