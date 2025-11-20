#!/usr/bin/env python3
"""
Script to create the Spiralized Zucchini Noodles with Spinach-Walnut Pesto recipe.
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
        print("Creating Spiralized Zucchini Noodles with Spinach-Walnut Pesto Recipe")
        print("=" * 60)
        
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Spiralized Zucchini Noodles with Spinach-Walnut Pesto",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        serving_unit_id = get_unit_id("serving", cursor)
        cup_unit_id = get_unit_id("cup", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        clove_unit_id = get_unit_id("clove", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Spiralized Zucchini Noodles with Spinach-Walnut Pesto", False, 4, serving_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Walnuts", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "35g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": "large", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Baby Spinach", cursor), "quantity": 5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "150g, packed chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Basil", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "30g, packed fresh leaves"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Zucchini", cursor), "quantity": 3, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "ends trimmed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Grape Tomatoes", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "150g, cherry or grape tomatoes, halved"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free White Beans", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "375g, home-cooked or from BPA-free cans, drained and rinsed (cannellini beans)"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Pepper Flakes", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "optional"},
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

