#!/usr/bin/env python3
"""
Script to create the Nutty Parm 2.0 recipe.
"""

import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import get_db

def get_ingredient_id(name, cursor):
    """Get ingredient ID by name."""
    cursor.execute("SELECT id FROM ingredients WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Ingredient '{name}' not found")
    return result['id']

def get_unit_id(name, cursor):
    """Get unit type ID by name."""
    cursor.execute("SELECT id FROM unit_types WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Unit '{name}' not found")
    return result['id']

def main():
    """Main function to create the recipe."""
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating Nutty Parm 2.0 Recipe")
        print("=" * 60)
        
        # Check if recipe already exists
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Nutty Parm 2.0",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        # Get unit IDs
        cup_unit_id = get_unit_id("cup", cursor)
        
        # Create recipe
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Nutty Parm 2.0", True, 1.5, cup_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        # Add recipe items
        items = [
            # 1. 0.5 cup nutritional yeast
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor),
                "quantity": 0.5,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 2. 0.5 cup raw cashews (alternative: Brazil Nuts)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Raw Cashews", cursor),
                "quantity": 0.5,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": "alternative: Brazil Nuts"
            },
            # 3. 0.25 cup raw walnuts (alternative: Raw Pecans)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Raw Walnuts", cursor),
                "quantity": 0.25,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": "alternative: Raw Pecans"
            },
            # 4. 0.25 cup raw sesame seeds
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Raw Sesame Seeds", cursor),
                "quantity": 0.25,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
        ]
        
        # Add each item
        for item in items:
            cursor.execute("""
                INSERT INTO recipe_items (recipe_id, item_type, ingredient_id, sub_recipe_id,
                                         quantity, unit_id, size_qualifier, preparation_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_id,
                item['item_type'],
                item.get('ingredient_id'),
                item.get('sub_recipe_id'),
                item['quantity'],
                item['unit_id'],
                item.get('size_qualifier'),
                item.get('preparation_notes')
            ))
        
        db.commit()
        print(f"\n  ✓ Added {len(items)} recipe items")
        print("\n" + "=" * 60)
        print("✓ Recipe created successfully!")
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

