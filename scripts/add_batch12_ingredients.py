#!/usr/bin/env python3
"""
Script to add new ingredients for Batch 12 recipes.
Ingredients: Ground Allspice, Unsweetened Cocoa Powder, Strong Brewed Coffee, Fresh Mint Leaves
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
        print("Adding Batch 12 Ingredients")
        print("=" * 60)
        
        # 1. Ground Allspice
        print("\n1. Ground Allspice")
        cursor.execute("SELECT id FROM ingredients WHERE name = ?", ("Ground Allspice",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Ground Allspice already exists (ID: {existing['id']}) - skipping")
        else:
            type_id = get_type_id("Spices", cursor)
            shopping_unit_id = get_unit_id("package", cursor)
            
            cursor.execute("""
                INSERT INTO ingredients (name, type_id, shopping_unit_id)
                VALUES (?, ?, ?)
            """, ("Ground Allspice", type_id, shopping_unit_id))
            
            ingredient_id = cursor.lastrowid
            print(f"  ✓ Created Ground Allspice (ID: {ingredient_id})")
            
            # Conversion rules: 1 oz / 28g package
            teaspoon_unit_id = get_unit_id("teaspoon", cursor)
            gram_unit_id = get_unit_id("gram", cursor)
            ounce_unit_id = get_unit_id("ounce", cursor)
            
            conversion_rules = [
                {'from': 'package', 'from_unit_id': shopping_unit_id, 'factor': 1.0},
                {'from': 'teaspoon', 'from_unit_id': teaspoon_unit_id, 'factor': 1/50},  # ~50 tsp per 1 oz package
                {'from': 'gram', 'from_unit_id': gram_unit_id, 'factor': 1/28},
                {'from': 'ounce', 'from_unit_id': ounce_unit_id, 'factor': 1/1},
            ]
            
            for rule in conversion_rules:
                cursor.execute("""
                    INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                    VALUES (?, ?, ?, ?)
                """, (ingredient_id, rule['from_unit_id'], shopping_unit_id, rule['factor']))
            print(f"    ✓ Added conversion rules")
        
        # 2. Unsweetened Cocoa Powder
        print("\n2. Unsweetened Cocoa Powder")
        cursor.execute("SELECT id FROM ingredients WHERE name = ?", ("Unsweetened Cocoa Powder",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Unsweetened Cocoa Powder already exists (ID: {existing['id']}) - skipping")
        else:
            type_id = get_type_id("Pantry Items", cursor)
            shopping_unit_id = get_unit_id("package", cursor)
            
            cursor.execute("""
                INSERT INTO ingredients (name, type_id, shopping_unit_id)
                VALUES (?, ?, ?)
            """, ("Unsweetened Cocoa Powder", type_id, shopping_unit_id))
            
            ingredient_id = cursor.lastrowid
            print(f"  ✓ Created Unsweetened Cocoa Powder (ID: {ingredient_id})")
            
            # Conversion rules: 8 oz / 227g package
            # 0.25 cup = 20g, so 1 cup = 80g, so ~2.84 cups per package
            tablespoon_unit_id = get_unit_id("tablespoon", cursor)
            cup_unit_id = get_unit_id("cup", cursor)
            gram_unit_id = get_unit_id("gram", cursor)
            ounce_unit_id = get_unit_id("ounce", cursor)
            
            conversion_rules = [
                {'from': 'package', 'from_unit_id': shopping_unit_id, 'factor': 1.0},
                {'from': 'tablespoon', 'from_unit_id': tablespoon_unit_id, 'factor': 1/45.4},  # ~45.4 tbsp per package
                {'from': 'cup', 'from_unit_id': cup_unit_id, 'factor': 1/2.84},  # ~2.84 cups per package
                {'from': 'gram', 'from_unit_id': gram_unit_id, 'factor': 1/227},
                {'from': 'ounce', 'from_unit_id': ounce_unit_id, 'factor': 1/8},
            ]
            
            for rule in conversion_rules:
                cursor.execute("""
                    INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                    VALUES (?, ?, ?, ?)
                """, (ingredient_id, rule['from_unit_id'], shopping_unit_id, rule['factor']))
            print(f"    ✓ Added conversion rules")
        
        # 3. Strong Brewed Coffee
        print("\n3. Strong Brewed Coffee")
        cursor.execute("SELECT id FROM ingredients WHERE name = ?", ("Strong Brewed Coffee",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Strong Brewed Coffee already exists (ID: {existing['id']}) - skipping")
        else:
            type_id = get_type_id("Pantry Items", cursor)
            shopping_unit_id = get_unit_id("package", cursor)
            
            cursor.execute("""
                INSERT INTO ingredients (name, type_id, shopping_unit_id)
                VALUES (?, ?, ?)
            """, ("Strong Brewed Coffee", type_id, shopping_unit_id))
            
            ingredient_id = cursor.lastrowid
            print(f"  ✓ Created Strong Brewed Coffee (ID: {ingredient_id})")
            
            # Conversion rules: 12 oz / 340g package ground coffee
            # Estimate 85 cups brewed per 12 oz package
            cup_unit_id = get_unit_id("cup", cursor)
            milliliter_unit_id = get_unit_id("milliliter", cursor)
            fluid_ounce_unit_id = get_unit_id("fluid_ounce", cursor)
            
            conversion_rules = [
                {'from': 'package', 'from_unit_id': shopping_unit_id, 'factor': 1.0},
                {'from': 'cup', 'from_unit_id': cup_unit_id, 'factor': 1/85},  # ~85 cups brewed per package
                {'from': 'milliliter', 'from_unit_id': milliliter_unit_id, 'factor': 1/20040},  # ~20040 ml per package
                {'from': 'fluid_ounce', 'from_unit_id': fluid_ounce_unit_id, 'factor': 1/680},  # ~680 fl oz per package
            ]
            
            for rule in conversion_rules:
                cursor.execute("""
                    INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                    VALUES (?, ?, ?, ?)
                """, (ingredient_id, rule['from_unit_id'], shopping_unit_id, rule['factor']))
            print(f"    ✓ Added conversion rules")
        
        # 4. Fresh Mint Leaves
        print("\n4. Fresh Mint Leaves")
        cursor.execute("SELECT id FROM ingredients WHERE name = ?", ("Fresh Mint Leaves",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Fresh Mint Leaves already exists (ID: {existing['id']}) - skipping")
        else:
            type_id = get_type_id("Herbs", cursor)
            shopping_unit_id = get_unit_id("bunch", cursor)
            
            cursor.execute("""
                INSERT INTO ingredients (name, type_id, shopping_unit_id)
                VALUES (?, ?, ?)
            """, ("Fresh Mint Leaves", type_id, shopping_unit_id))
            
            ingredient_id = cursor.lastrowid
            print(f"  ✓ Created Fresh Mint Leaves (ID: {ingredient_id})")
            
            # Conversion rules: estimate 20 leaves per bunch, 10g per bunch
            whole_unit_id = get_unit_id("whole", cursor)
            gram_unit_id = get_unit_id("gram", cursor)
            
            conversion_rules = [
                {'from': 'bunch', 'from_unit_id': shopping_unit_id, 'factor': 1.0},
                {'from': 'whole', 'from_unit_id': whole_unit_id, 'factor': 1/20},  # ~20 leaves per bunch
                {'from': 'gram', 'from_unit_id': gram_unit_id, 'factor': 1/10},  # ~10g per bunch
            ]
            
            for rule in conversion_rules:
                cursor.execute("""
                    INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                    VALUES (?, ?, ?, ?)
                """, (ingredient_id, rule['from_unit_id'], shopping_unit_id, rule['factor']))
            print(f"    ✓ Added conversion rules")
        
        db.commit()
        print("\n" + "=" * 60)
        print("✓ All Batch 12 ingredients added successfully!")
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

