#!/usr/bin/env python3
"""
Script to create the French-Style Potato Salad recipe.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db

def get_ingredient_id(name, cursor):
    cursor.execute("SELECT id FROM ingredients WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Ingredient '{name}' not found")
    return result['id']

def get_unit_id(name, cursor):
    cursor.execute("SELECT id FROM unit_types WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Unit '{name}' not found")
    return result['id']

def main():
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating French-Style Potato Salad Recipe")
        print("=" * 60)
        
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("French-Style Potato Salad",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        serving_unit_id = get_unit_id("serving", cursor)
        pound_unit_id = get_unit_id("pound", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("French-Style Potato Salad", False, 6, serving_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Small Potatoes", cursor), "quantity": 2, "unit_id": pound_unit_id, "size_qualifier": None, "preparation_notes": "1kg, small yellow potatoes, unpeeled"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Scallions", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "minced, green and white parts"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Parsley", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "minced, flat-leaf"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Dill", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Chives", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lemon", cursor), "quantity": 2.5, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "fresh lemon juice or apple cider vinegar (2.5 to 3 tablespoons)"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Onion Powder", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
        ]
        
        for item in items:
            cursor.execute("""
                INSERT INTO recipe_items 
                (recipe_id, item_type, ingredient_id, sub_recipe_id, quantity, unit_id, size_qualifier, preparation_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_id,
                item["item_type"],
                item.get("ingredient_id"),
                item.get("sub_recipe_id"),
                item["quantity"],
                item["unit_id"],
                item["size_qualifier"],
                item["preparation_notes"]
            ))
        
        db.commit()
        print(f"\n  ✓ Added {len(items)} items to recipe")
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

