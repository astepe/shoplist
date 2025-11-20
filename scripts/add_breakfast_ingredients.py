#!/usr/bin/env python3
"""
Script to add breakfast recipe ingredients:
1. Rolled Oats (by weight - pound)
2. Ground Chia Seeds
3. Ground Flaxseeds
4. Unsweetened Soy Milk
5. Pure Vanilla Extract
6. Carrot (already exists, but verify)
7. Pecans (already exists as Raw Pecans, verify if we need separate)
8. Ground Cinnamon
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
    """Main function to add all breakfast ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Breakfast Recipe Ingredients")
        print("=" * 60)
        
        # Step 1: Add Rolled Oats (by weight - pound)
        print("\n--- Step 1: Adding Rolled Oats ---")
        create_ingredient_with_conversions(
            name='Rolled Oats',
            type_name='Grains',
            shopping_unit_name='pound',
            conversion_rules=[
                {'from': 'cup', 'factor': 100/454},  # 100/454 = 0.2203 pounds/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 = 0.002203 pounds/g
                {'from': 'kilogram', 'factor': 2.205},  # 2.205 pounds/kg
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 pounds/oz
                {'from': 'pound', 'factor': 1.0},  # 1 pound = 1 pound
            ],
            db=db
        )
        
        # Step 2: Add Ground Chia Seeds
        print("\n--- Step 2: Adding Ground Chia Seeds ---")
        create_ingredient_with_conversions(
            name='Ground Chia Seeds',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/28.33},  # 1/28.33 = 0.0353 packages/tbsp
                {'from': 'teaspoon', 'factor': 1/85},  # 1/85 = 0.0118 packages/tsp
                {'from': 'gram', 'factor': 1/340},  # 1/340 packages/g
                {'from': 'ounce', 'factor': 1/12},  # 1/12 = 0.0833 packages/oz
            ],
            db=db
        )
        
        # Step 3: Add Ground Flaxseeds
        print("\n--- Step 3: Adding Ground Flaxseeds ---")
        create_ingredient_with_conversions(
            name='Ground Flaxseeds',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/64.86},  # 1/64.86 = 0.0154 packages/tbsp
                {'from': 'teaspoon', 'factor': 1/197.39},  # 1/197.39 = 0.0051 packages/tsp
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 4: Add Unsweetened Soy Milk
        print("\n--- Step 4: Adding Unsweetened Soy Milk ---")
        create_ingredient_with_conversions(
            name='Unsweetened Soy Milk',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 1/4},  # 1/4 = 0.25 packages/cup
                {'from': 'milliliter', 'factor': 1/946},  # 1/946 packages/ml
                {'from': 'fluid_ounce', 'factor': 1/32},  # 1/32 = 0.03125 packages/fl oz
                {'from': 'gram', 'factor': 1/960},  # 1/960 packages/g
            ],
            db=db
        )
        
        # Step 5: Add Pure Vanilla Extract
        print("\n--- Step 5: Adding Pure Vanilla Extract ---")
        create_ingredient_with_conversions(
            name='Pure Vanilla Extract',
            type_name='Pantry Items',
            shopping_unit_name='bottle',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/23.6},  # 1/23.6 = 0.0424 bottles/tsp
                {'from': 'tablespoon', 'factor': 1/7.87},  # 1/7.87 = 0.127 bottles/tbsp
                {'from': 'milliliter', 'factor': 1/118},  # 1/118 bottles/ml
                {'from': 'fluid_ounce', 'factor': 1/4},  # 1/4 = 0.25 bottles/fl oz
            ],
            db=db
        )
        
        # Step 6: Verify Carrot exists
        print("\n--- Step 6: Verifying Carrot ---")
        cursor = db.cursor()
        cursor.execute("SELECT id FROM ingredients WHERE name = 'Carrot'")
        carrot = cursor.fetchone()
        if carrot:
            print(f"  ✓ Carrot already exists (ID: {carrot['id']})")
        else:
            # Add Carrot if missing
            create_ingredient_with_conversions(
                name='Carrot',
                type_name='Vegetables',
                shopping_unit_name='whole',
                conversion_rules=[
                    {'from': 'cup', 'factor': 110/60},  # 110/60 = 1.83 whole/cup (grated)
                    {'from': 'gram', 'factor': 1/60},  # 1/60 = 0.0167 whole/g (medium)
                    {'from': 'whole', 'factor': 1.0},
                ],
                size_rules=[
                    {'size': 'small', 'unit': 'gram', 'value': 40},
                    {'size': 'medium', 'unit': 'gram', 'value': 60},
                    {'size': 'large', 'unit': 'gram', 'value': 80},
                ],
                db=db
            )
        
        # Step 7: Verify Pecans exist (may be Raw Pecans)
        print("\n--- Step 7: Verifying Pecans ---")
        cursor.execute("SELECT id FROM ingredients WHERE name IN ('Pecans', 'Raw Pecans')")
        pecans = cursor.fetchone()
        if pecans:
            print(f"  ✓ Pecans already exist (ID: {pecans['id']})")
        else:
            # Note: Raw Pecans already exists, so we can use that
            print("  ℹ Note: 'Raw Pecans' already exists in system - will use that for recipes")
        
        # Step 8: Add Ground Cinnamon
        print("\n--- Step 8: Adding Ground Cinnamon ---")
        create_ingredient_with_conversions(
            name='Ground Cinnamon',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/22.8},  # 1/22.8 = 0.0439 packages/tsp (assuming 2oz package, ~57g)
                {'from': 'gram', 'factor': 1/57},  # 1/57 packages/g
                {'from': 'ounce', 'factor': 1/2},  # 1/2 = 0.5 packages/oz
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All breakfast ingredients added successfully!")
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

