#!/usr/bin/env python3
"""
Script to add ingredients for Curried Butternut Soup with Rainbow Chard recipe.
This script adds:
1. Butternut Squash
2. Curry Powder
3. Fresh Ginger
4. Crushed Tomatoes
5. Rainbow Chard
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
    """Main function to add all Butternut Soup ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Ingredients for Curried Butternut Soup")
        print("=" * 60)
        
        # Step 1: Add Butternut Squash
        print("\n--- Step 1: Adding Butternut Squash ---")
        create_ingredient_with_conversions(
            name='Butternut Squash',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'cup', 'factor': 0.125},  # 8 cups diced = 1 whole
                {'from': 'gram', 'factor': 0.00074},  # 1350g = 1 whole
                {'from': 'kilogram', 'factor': 0.74},  # 1.35 kg = 1 whole
                {'from': 'pound', 'factor': 0.333},  # 3 lbs = 1 whole
                {'from': 'ounce', 'factor': 0.0208},  # 48 oz = 1 whole
                {'from': 'whole', 'factor': 1.0},
                {'from': 'piece', 'factor': 1.0},
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 800},
                {'size': 'medium', 'unit': 'gram', 'value': 1200},
                {'size': 'large', 'unit': 'gram', 'value': 1600},
            ],
            db=db
        )
        
        # Step 2: Add Curry Powder
        print("\n--- Step 2: Adding Curry Powder ---")
        create_ingredient_with_conversions(
            name='Curry Powder',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 0.003},  # ~330 tsp per 3oz package
                {'from': 'tablespoon', 'factor': 0.01},  # ~100 tbsp per package
                {'from': 'gram', 'factor': 0.0118},  # 85g = 1 package
                {'from': 'kilogram', 'factor': 11.76},  # 1kg = 11.76 packages
                {'from': 'ounce', 'factor': 0.333},  # 3 oz = 1 package
                {'from': 'pound', 'factor': 5.33},  # 0.1875 lb (3 oz) = 1 package
            ],
            db=db
        )
        
        # Step 3: Add Fresh Ginger
        print("\n--- Step 3: Adding Fresh Ginger ---")
        create_ingredient_with_conversions(
            name='Fresh Ginger',
            type_name='Spices',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 0.033},  # 30 tsp grated = 1 whole
                {'from': 'tablespoon', 'factor': 0.011},  # 90 tbsp grated = 1 whole
                {'from': 'gram', 'factor': 0.033},  # 30g = 1 whole
                {'from': 'kilogram', 'factor': 33.33},  # 1kg = 33.33 whole
                {'from': 'ounce', 'factor': 0.943},  # 1.06 oz (30g) = 1 whole
                {'from': 'pound', 'factor': 15.08},  # 0.066 lb (30g) = 1 whole, or 1 lb = 15.08 whole
                {'from': 'whole', 'factor': 1.0},
                {'from': 'piece', 'factor': 1.0},
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 15},
                {'size': 'medium', 'unit': 'gram', 'value': 30},
                {'size': 'large', 'unit': 'gram', 'value': 50},
            ],
            db=db
        )
        
        # Step 4: Add Crushed Tomatoes
        print("\n--- Step 4: Adding Crushed Tomatoes ---")
        create_ingredient_with_conversions(
            name='Crushed Tomatoes',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 0.571},  # 1.75 cups = 1 package
                {'from': 'tablespoon', 'factor': 0.036},  # 28 tbsp = 1 package
                {'from': 'teaspoon', 'factor': 0.012},  # 84 tsp = 1 package
                {'from': 'gram', 'factor': 0.00243},  # 411g = 1 package
                {'from': 'kilogram', 'factor': 2.43},  # 1kg = 2.43 packages
                {'from': 'ounce', 'factor': 0.069},  # 14.5 oz = 1 package
                {'from': 'pound', 'factor': 1.103},  # 0.90625 lb (14.5 oz) = 1 package
                {'from': 'milliliter', 'factor': 0.00243},  # 411 ml = 1 package
                {'from': 'liter', 'factor': 2.43},  # 0.411 L = 1 package, or 1 L = 2.43 packages
            ],
            db=db
        )
        
        # Step 5: Add Rainbow Chard
        print("\n--- Step 5: Adding Rainbow Chard ---")
        create_ingredient_with_conversions(
            name='Rainbow Chard',
            type_name='Vegetables',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'cup', 'factor': 0.25},  # 4 cups chopped = 1 bunch
                {'from': 'gram', 'factor': 0.00556},  # 180g = 1 bunch
                {'from': 'kilogram', 'factor': 5.56},  # 1kg = 5.56 bunches
                {'from': 'ounce', 'factor': 0.157},  # 6.35 oz (180g) = 1 bunch
                {'from': 'pound', 'factor': 2.52},  # 0.397 lb (180g) = 1 bunch, or 1 lb = 2.52 bunches
                {'from': 'bunch', 'factor': 1.0},
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

