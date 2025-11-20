#!/usr/bin/env python3
"""
Script to create the Groatnola Plus sub-recipe.
Note: This yields 24 servings but we'll set it to 6 cups (0.25 cup per serving).
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
        print("Creating Groatnola Plus Sub-Recipe")
        print("=" * 60)
        
        # Check if recipe already exists
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Groatnola Plus",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        # Get unit IDs
        cup_unit_id = get_unit_id("cup", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        
        # Create recipe (yields 6 cups = 24 servings × 0.25 cup/serving)
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Groatnola Plus", True, 6, cup_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created sub-recipe (ID: {recipe_id})")
        print(f"  ✓ Yield: 6 cups (24 servings × 0.25 cup/serving)")
        
        # Add recipe items
        items = [
            # 1. Buckwheat Groats - 1 cup (rinsed)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Buckwheat Groats", cursor),
                "quantity": 1,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": "rinsed"
            },
            # 2. Sweet Potato - 1 whole (large, cooked, peeled, and mashed, about 1.5 cups/200g)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Sweet Potato", cursor),
                "quantity": 1,
                "unit_id": get_unit_id("whole", cursor),
                "size_qualifier": "large",
                "preparation_notes": "cooked, peeled, and mashed, about 1.5 cups/200g"
            },
            # 3. Ground Cinnamon - 2 teaspoons
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Ground Cinnamon", cursor),
                "quantity": 2,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 4. Pumpkin Pie Spice - 2 teaspoons
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Pumpkin Pie Spice", cursor),
                "quantity": 2,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 5. Ground Flaxseeds - 1 tablespoon
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Ground Flaxseeds", cursor),
                "quantity": 1,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 6. Ground Turmeric - 0.5 teaspoon
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Ground Turmeric", cursor),
                "quantity": 0.5,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 7. Pepitas (Pumpkin Seeds) - 3 tablespoons
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Pepitas (Pumpkin Seeds)", cursor),
                "quantity": 3,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 8. Raw Walnuts - 3 tablespoons (chopped)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Raw Walnuts", cursor),
                "quantity": 3,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": "chopped"
            },
            # 9. Rolled Oats - 8 cups (note: 8-12 cups range for different chunkiness, using 8 as default)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Rolled Oats", cursor),
                "quantity": 8,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": "8-12 cups range for different chunkiness, using 8 as default"
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
        print("✓ Sub-recipe created successfully!")
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

