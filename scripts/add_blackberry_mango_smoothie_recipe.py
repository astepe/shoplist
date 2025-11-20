#!/usr/bin/env python3
"""
Script to create the Blackberry-Mango Smoothie Bowls with Barberries recipe.
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
        print("Creating Blackberry-Mango Smoothie Bowls with Barberries Recipe")
        print("=" * 60)
        
        # Check if recipe already exists
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Blackberry-Mango Smoothie Bowls with Barberries",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        # Get unit IDs
        serving_unit_id = get_unit_id("serving", cursor)
        cup_unit_id = get_unit_id("cup", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        
        # Create recipe
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Blackberry-Mango Smoothie Bowls with Barberries", False, 2, serving_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        # Add recipe items
        items = [
            # 1. Dried Barberries - 2 tablespoons (soaked in water for 10 minutes)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Dried Barberries", cursor),
                "quantity": 2,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": "soaked in water for 10 minutes"
            },
            # 2. Frozen Chopped Mango - 1 cup
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Frozen Chopped Mango", cursor),
                "quantity": 1,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 3. Frozen Blackberries - 1 cup
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Frozen Blackberries", cursor),
                "quantity": 1,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 4. Ground Chia Seeds - 2 tablespoons
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Ground Chia Seeds", cursor),
                "quantity": 2,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 5. Almond Butter - 2 tablespoons
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Almond Butter", cursor),
                "quantity": 2,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 6. Unsweetened Soy Milk - 0.75 cup
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Unsweetened Soy Milk", cursor),
                "quantity": 0.75,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 7. Sweet Potato - 0.5 cup (mashed cooked)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Sweet Potato", cursor),
                "quantity": 0.5,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": "mashed cooked"
            },
            # 8. Ground Turmeric - 1 teaspoon
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Ground Turmeric", cursor),
                "quantity": 1,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 9. Pure Vanilla Extract - 1 teaspoon
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Pure Vanilla Extract", cursor),
                "quantity": 1,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
        ]
        
        # Insert items
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

