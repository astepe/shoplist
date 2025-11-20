#!/usr/bin/env python3
"""
Script to add Ripe Bananas ingredient.
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

def main():
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Adding Ripe Bananas Ingredient")
        print("=" * 60)
        
        # Check if ingredient already exists
        cursor.execute("SELECT id FROM ingredients WHERE name = ?", ("Ripe Bananas",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Ripe Bananas already exists (ID: {existing['id']}) - skipping")
            return existing['id']
        
        # Get IDs
        type_id = get_type_id("Fruits", cursor)
        shopping_unit_id = get_unit_id("whole", cursor)
        
        # Create ingredient
        cursor.execute("""
            INSERT INTO ingredients (name, type_id, shopping_unit_id)
            VALUES (?, ?, ?)
        """, ("Ripe Bananas", type_id, shopping_unit_id))
        
        ingredient_id = cursor.lastrowid
        print(f"  ✓ Created Ripe Bananas (ID: {ingredient_id})")
        
        # Add conversion rules
        # Recipe: 1.5 cups mashed = 340g = 2 to 3 large bananas
        # Assuming ~227g per large banana, 1.5 cups ≈ 340g ≈ 1.5 large bananas
        # 1 cup mashed ≈ 227g ≈ 1 large banana
        conversion_rules = [
            {'from': 'whole', 'factor': 1.0},  # 1.0
            {'from': 'cup', 'factor': 1.533},  # 1.5 cups = 340g = 2.3 large bananas, so ~1.533 wholes/cup
        ]
        
        # Add size estimation rules
        # large = ~227g (113g per cup mashed)
        # medium = ~150g (100g per cup mashed)  
        # small = ~100g (67g per cup mashed)
        size_rules = [
            {'size': 'large', 'unit': 'gram', 'value': 227},
            {'size': 'medium', 'unit': 'gram', 'value': 150},
            {'size': 'small', 'unit': 'gram', 'value': 100},
        ]
        
        for rule in conversion_rules:
            from_unit_id = get_unit_id(rule['from'], cursor)
            cursor.execute("""
                INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                VALUES (?, ?, ?, ?)
            """, (ingredient_id, from_unit_id, shopping_unit_id, rule['factor']))
            print(f"    ✓ Conversion: {rule['from']} → whole: {rule['factor']:.6f}")
        
        for size_rule in size_rules:
            ref_unit_id = get_unit_id(size_rule['unit'], cursor)
            cursor.execute("""
                INSERT INTO size_estimation_rules (ingredient_id, size_qualifier, reference_unit_id, reference_value)
                VALUES (?, ?, ?, ?)
            """, (ingredient_id, size_rule['size'], ref_unit_id, size_rule['value']))
            print(f"    ✓ Size rule: {size_rule['size']} = {size_rule['value']} {size_rule['unit']}")
        
        db.commit()
        print("\n" + "=" * 60)
        print("✓ Ripe Bananas added successfully!")
        print("=" * 60)
        
        return ingredient_id
        
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

