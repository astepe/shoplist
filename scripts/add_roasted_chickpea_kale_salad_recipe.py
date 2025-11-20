#!/usr/bin/env python3
"""
Script to create the Roasted Chickpea and Kale Salad with Sweet Potatoes and Apples recipe.
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
        print("Creating Roasted Chickpea and Kale Salad with Sweet Potatoes and Apples Recipe")
        print("=" * 60)
        
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Roasted Chickpea and Kale Salad with Sweet Potatoes and Apples",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        serving_unit_id = get_unit_id("serving", cursor)
        cup_unit_id = get_unit_id("cup", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        pound_unit_id = get_unit_id("pound", cursor)
        fluid_ounce_unit_id = get_unit_id("fluid_ounce", cursor)
        
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Roasted Chickpea and Kale Salad with Sweet Potatoes and Apples", False, 4, serving_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Chickpeas", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "370g, home-cooked or from BPA-free cans or Tetra Paks, drained and rinsed, roasted until browned and crunchy"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Barberries", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "soaked in hot water for 10 minutes to soften"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Sweet Potato", cursor), "quantity": 1, "unit_id": pound_unit_id, "size_qualifier": None, "preparation_notes": "450g, peeled and cut into ½-inch dice, steamed until just tender"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Kale", cursor), "quantity": 6, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "120g, coarsely chopped baby kale or arugula"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Balsamic Vinegar", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60ml, or apple cider vinegar"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Almond Butter", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Apple", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "Fuji or Gala, or another crisp, sweet apple, cored and cut into ½-inch dice"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Celery", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60g, chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Almonds", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "25g, slivered"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Scallions", cursor), "quantity": 2, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "green and white parts, minced"},
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

