#!/usr/bin/env python3
"""
Script to create all remaining Batch 5 recipes.
Due to the large number, we'll create them all in one script.
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

def get_sub_recipe_id(name_pattern, cursor):
    cursor.execute("""
        SELECT id, name FROM recipes 
        WHERE (name LIKE ? OR name LIKE ?) AND is_sub_recipe = 1
        ORDER BY name
        LIMIT 1
    """, (f'%{name_pattern}%', f'%{name_pattern.split()[0]}%'))
    results = cursor.fetchall()
    if not results:
        raise ValueError(f"Sub-recipe '{name_pattern}' not found")
    for r in results:
        if name_pattern.lower() in r['name'].lower():
            return r['id'], r['name']
    return results[0]['id'], results[0]['name']

def create_recipe(name, is_sub_recipe, yield_quantity, yield_unit_name, items, cursor, db):
    """Helper function to create a recipe."""
    cursor.execute("SELECT id FROM recipes WHERE name = ?", (name,))
    existing = cursor.fetchone()
    if existing:
        print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
        return
    
    yield_unit_id = get_unit_id(yield_unit_name, cursor)
    
    cursor.execute("""
        INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
        VALUES (?, ?, ?, ?)
    """, (name, is_sub_recipe, yield_quantity, yield_unit_id))
    
    recipe_id = cursor.lastrowid
    print(f"  ✓ Created recipe (ID: {recipe_id})")
    
    for item in items:
        unit_id = get_unit_id(item['unit'], cursor)
        ingredient_id = item.get('ingredient_id')
        sub_recipe_id = item.get('sub_recipe_id')
        
        if ingredient_id is None and sub_recipe_id is None:
            # Need to resolve
            if 'ingredient' in item:
                ingredient_id = get_ingredient_id(item['ingredient'], cursor)
            elif 'sub_recipe' in item:
                sub_recipe_id, _ = get_sub_recipe_id(item['sub_recipe'], cursor)
        
        cursor.execute("""
            INSERT INTO recipe_items 
            (recipe_id, item_type, ingredient_id, sub_recipe_id, quantity, unit_id, size_qualifier, preparation_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            recipe_id,
            item['item_type'],
            ingredient_id,
            sub_recipe_id,
            item['quantity'],
            unit_id,
            item.get('size_qualifier'),
            item.get('preparation_notes')
        ))
    
    db.commit()
    print(f"  ✓ Added {len(items)} items to recipe\n")
    return recipe_id

def main():
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating Remaining Batch 5 Recipes")
        print("=" * 60)
        
        # Recipe 3: Spicy Potato and Spinach Quesadillas
        print("\n--- Recipe 3: Spicy Potato and Spinach Quesadillas ---")
        tomato_salsa_id, _ = get_sub_recipe_id("Tomato Salsa", cursor)
        create_recipe(
            name="Spicy Potato and Spinach Quesadillas",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Red Onion", "quantity": 0.5, "unit": "cup", "preparation_notes": "60g, minced"},
                {"item_type": "ingredient", "ingredient": "Mushrooms", "quantity": 2, "unit": "cup", "preparation_notes": "130g, chopped"},
                {"item_type": "ingredient", "ingredient": "Garlic", "quantity": 2, "unit": "clove", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Chipotle Chile Powder", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": "or to taste"},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 2, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Fresh Baby Spinach", "quantity": 8, "unit": "cup", "preparation_notes": "240g, baby spinach"},
                {"item_type": "ingredient", "ingredient": "Russet Potatoes", "quantity": 2, "unit": "whole", "size_qualifier": "large", "preparation_notes": "cooked, coarsely mashed"},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Tortillas", "quantity": 4, "unit": "whole", "size_qualifier": "large", "preparation_notes": None},
                {"item_type": "sub_recipe", "sub_recipe_id": tomato_salsa_id, "quantity": 1, "unit": "as_needed", "preparation_notes": "optional, to serve"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 4: Black Bean Burritos with Tomato Salsa
        print("\n--- Recipe 4: Black Bean Burritos with Tomato Salsa ---")
        cheesy_id, _ = get_sub_recipe_id("Cheesy Sauce", cursor)
        create_recipe(
            name="Black Bean Burritos with Tomato Salsa",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Red Onion", "quantity": 1, "unit": "whole", "size_qualifier": "small", "preparation_notes": "minced, reserve 2 tablespoons for Tomato Salsa"},
                {"item_type": "ingredient", "ingredient": "Salt-Free Black Beans", "quantity": 1.5, "unit": "cup", "preparation_notes": "375g, home-cooked or from BPA-free cans, drained and rinsed"},
                {"item_type": "sub_recipe", "sub_recipe_id": tomato_salsa_id, "quantity": 0.5, "unit": "cup", "preparation_notes": "for cooking"},
                {"item_type": "ingredient", "ingredient": "Quinoa", "quantity": 1, "unit": "cup", "preparation_notes": "180g, cooked quinoa or other cooked whole grain or riced cauliflower"},
                {"item_type": "ingredient", "ingredient": "Corn Kernels", "quantity": 1, "unit": "cup", "preparation_notes": "160g, cooked fresh or frozen"},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Tortillas", "quantity": 4, "unit": "whole", "size_qualifier": "large", "preparation_notes": "warmed"},
                {"item_type": "sub_recipe", "sub_recipe_id": cheesy_id, "quantity": 1, "unit": "as_needed", "preparation_notes": "optional"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 5: Curried Tempeh Wraps
        print("\n--- Recipe 5: Curried Tempeh Wraps ---")
        create_recipe(
            name="Curried Tempeh Wraps",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Raw Cashews", "quantity": 1, "unit": "cup", "preparation_notes": "120g"},
                {"item_type": "ingredient", "ingredient": "Pitted Dates", "quantity": 2, "unit": "whole", "preparation_notes": "pitted"},
                {"item_type": "ingredient", "ingredient": "Lemon", "quantity": 1, "unit": "tablespoon", "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient": "Curry Powder", "quantity": 2, "unit": "teaspoon", "preparation_notes": "or to taste"},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 1, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Onion Powder", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Garlic Powder", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Tempeh", "quantity": 1, "unit": "package", "preparation_notes": "8 oz, 230g"},
                {"item_type": "ingredient", "ingredient": "Raw Walnuts", "quantity": 0.5, "unit": "cup", "preparation_notes": "50g, chopped"},
                {"item_type": "ingredient", "ingredient": "Apple", "quantity": 0.5, "unit": "cup", "preparation_notes": "50g, chopped"},
                {"item_type": "ingredient", "ingredient": "Carrot", "quantity": 0.5, "unit": "cup", "preparation_notes": "55g, shredded"},
                {"item_type": "ingredient", "ingredient": "Celery", "quantity": 0.25, "unit": "cup", "preparation_notes": "30g, finely chopped"},
                {"item_type": "ingredient", "ingredient": "Scallions", "quantity": 0.25, "unit": "cup", "preparation_notes": "10g, finely chopped, green and white parts"},
                {"item_type": "ingredient", "ingredient": "Red Bell Pepper", "quantity": 0.25, "unit": "cup", "preparation_notes": "30g, finely chopped"},
                {"item_type": "ingredient", "ingredient": "Fresh Parsley", "quantity": 2, "unit": "tablespoon", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Tortillas", "quantity": 4, "unit": "whole", "size_qualifier": "large", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Romaine Lettuce", "quantity": 2, "unit": "cup", "preparation_notes": "100 to 150g, shredded"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 6: Lasagna with Kale and Red Lentil Tomato Sauce
        print("\n--- Recipe 6: Lasagna with Kale and Red Lentil Tomato Sauce ---")
        nutty_parm_id, _ = get_sub_recipe_id("Nutty Parm", cursor)
        create_recipe(
            name="Lasagna with Kale and Red Lentil Tomato Sauce",
            is_sub_recipe=False,
            yield_quantity=6,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Red Lentils", "quantity": 1, "unit": "cup", "preparation_notes": "190g, sorted and rinsed"},
                {"item_type": "ingredient", "ingredient": "Salt-Free Marinara Sauce", "quantity": 6, "unit": "cup", "preparation_notes": "1.5L, bottled or homemade"},
                {"item_type": "ingredient", "ingredient": "Cauliflower Florets", "quantity": 2, "unit": "cup", "preparation_notes": "160g"},
                {"item_type": "ingredient", "ingredient": "Salt-Free White Beans", "quantity": 1.5, "unit": "cup", "preparation_notes": "375g, home-cooked or from BPA-free cans, drained and rinsed (cannellini beans)"},
                {"item_type": "ingredient", "ingredient": "Nutritional Yeast", "quantity": 0.33, "unit": "cup", "preparation_notes": "25g"},
                {"item_type": "ingredient", "ingredient": "Fresh Parsley", "quantity": 0.25, "unit": "cup", "preparation_notes": "15g, minced"},
                {"item_type": "ingredient", "ingredient": "Lemon", "quantity": 1, "unit": "tablespoon", "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 1, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Dried Oregano", "quantity": 1, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Dried Basil", "quantity": 1, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Garlic Powder", "quantity": 1, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Onion Powder", "quantity": 1, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Ground Fennel Seeds", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Red Pepper Flakes", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Black Pepper", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "ground pippali or black pepper"},
                {"item_type": "ingredient", "ingredient": "Kale", "quantity": 4, "unit": "cup", "preparation_notes": "85g, chopped, stems removed"},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Lasagna Noodles", "quantity": 12, "unit": "whole", "preparation_notes": None},
                {"item_type": "sub_recipe", "sub_recipe_id": nutty_parm_id, "quantity": 0.33, "unit": "cup", "preparation_notes": "45g, optional"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 7: Lettuce Wraps with Mango Sauce
        print("\n--- Recipe 7: Lettuce Wraps with Mango Sauce ---")
        umami_id, _ = get_sub_recipe_id("Umami Sauce", cursor)
        mango_sauce_id, _ = get_sub_recipe_id("Mango Sauce", cursor)
        create_recipe(
            name="Lettuce Wraps with Mango Sauce",
            is_sub_recipe=False,
            yield_quantity=8,
            yield_unit_name="whole",
            items=[
                {"item_type": "ingredient", "ingredient": "Tempeh", "quantity": 1, "unit": "package", "preparation_notes": "8 oz, 230g"},
                {"item_type": "ingredient", "ingredient": "Mushrooms", "quantity": 1, "unit": "cup", "preparation_notes": "65g, chopped"},
                {"item_type": "ingredient", "ingredient": "Fresh Ginger", "quantity": 2, "unit": "teaspoon", "preparation_notes": "grated"},
                {"item_type": "ingredient", "ingredient": "Red Bell Pepper", "quantity": 0.5, "unit": "whole", "size_qualifier": "medium", "preparation_notes": "cored, seeded, chopped"},
                {"item_type": "ingredient", "ingredient": "Scallions", "quantity": 2, "unit": "whole", "preparation_notes": "green and white parts, minced"},
                {"item_type": "sub_recipe", "sub_recipe_id": umami_id, "quantity": 2, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Hass Avocado", "quantity": 1, "unit": "whole", "preparation_notes": "ripe"},
                {"item_type": "ingredient", "ingredient": "Lemon", "quantity": 1, "unit": "tablespoon", "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient": "Boston Lettuce", "quantity": 8, "unit": "whole", "size_qualifier": "large", "preparation_notes": "leaves, or butter lettuce"},
                {"item_type": "ingredient", "ingredient": "Carrot", "quantity": 1, "unit": "cup", "preparation_notes": "110g, finely shredded"},
                {"item_type": "ingredient", "ingredient": "Fresh Cilantro", "quantity": 0.33, "unit": "cup", "preparation_notes": "25g, chopped"},
                {"item_type": "sub_recipe", "sub_recipe_id": mango_sauce_id, "quantity": 1, "unit": "as_needed", "preparation_notes": None},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 8: Spaghetti with Mushroom Bolognese
        print("\n--- Recipe 8: Spaghetti with Mushroom Bolognese ---")
        create_recipe(
            name="Spaghetti with Mushroom Bolognese",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Red Onion", "quantity": 1, "unit": "whole", "size_qualifier": "medium", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Carrot", "quantity": 1, "unit": "whole", "size_qualifier": "medium", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Celery", "quantity": 1, "unit": "rib", "size_qualifier": "medium", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Garlic", "quantity": 3, "unit": "clove", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Mushrooms", "quantity": 12, "unit": "ounce", "preparation_notes": "340g, fresh mushrooms, finely chopped"},
                {"item_type": "ingredient", "ingredient": "Salt-Free Crushed Tomatoes", "quantity": 1, "unit": "can", "preparation_notes": "28 oz, 800g, BPA-free can or Tetra Pak"},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 2, "unit": "tablespoon", "preparation_notes": "blended with 0.25 cup hot water, 60ml"},
                {"item_type": "ingredient", "ingredient": "Nutritional Yeast", "quantity": 2, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Dried Basil", "quantity": 1, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Dried Oregano", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Ground Fennel Seeds", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Black Pepper", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "ground pippali or black pepper"},
                {"item_type": "ingredient", "ingredient": "Unsweetened Soy Milk", "quantity": 0.25, "unit": "cup", "preparation_notes": "60ml"},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Spaghetti", "quantity": 8, "unit": "ounce", "preparation_notes": "225g"},
                {"item_type": "ingredient", "ingredient": "Fresh Parsley", "quantity": 2, "unit": "tablespoon", "preparation_notes": "minced fresh flat-leaf parsley"},
                {"item_type": "sub_recipe", "sub_recipe_id": nutty_parm_id, "quantity": 2, "unit": "tablespoon", "preparation_notes": "optional"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 9: Rotini with Broccoli and Creamy Cauliflower Sauce
        print("\n--- Recipe 9: Rotini with Broccoli and Creamy Cauliflower Sauce ---")
        create_recipe(
            name="Rotini with Broccoli and Creamy Cauliflower Sauce",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Cauliflower Florets", "quantity": 2.5, "unit": "cup", "preparation_notes": "200g"},
                {"item_type": "ingredient", "ingredient": "Salt-Free White Beans", "quantity": 1.5, "unit": "cup", "preparation_notes": "375g, home-cooked or from BPA-free cans, drained and rinsed (cannellini beans)"},
                {"item_type": "ingredient", "ingredient": "Garlic", "quantity": 3, "unit": "clove", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Nutritional Yeast", "quantity": 2, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Lemon", "quantity": 2, "unit": "tablespoon", "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 1, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Dried Basil", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Dried Oregano", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Unsweetened Soy Milk", "quantity": 0.5, "unit": "cup", "preparation_notes": "120ml, or more as needed"},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Rotini", "quantity": 8, "unit": "ounce", "preparation_notes": "225g, or other whole-grain pasta"},
                {"item_type": "ingredient", "ingredient": "Broccoli Florets", "quantity": 4, "unit": "cup", "preparation_notes": "350g, small broccoli florets"},
                {"item_type": "ingredient", "ingredient": "Fresh Parsley", "quantity": 2, "unit": "tablespoon", "preparation_notes": "minced fresh parsley or basil, for garnish"},
                {"item_type": "sub_recipe", "sub_recipe_id": nutty_parm_id, "quantity": 1, "unit": "as_needed", "preparation_notes": "optional, to serve"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 10: Mushroom-Hummus Wraps
        print("\n--- Recipe 10: Mushroom-Hummus Wraps ---")
        create_recipe(
            name="Mushroom-Hummus Wraps",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Garlic", "quantity": 1, "unit": "clove", "size_qualifier": "large", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Salt-Free Chickpeas", "quantity": 1.5, "unit": "cup", "preparation_notes": "370g, home-cooked or from BPA-free cans, drained and rinsed"},
                {"item_type": "ingredient", "ingredient": "Tahini", "quantity": 3, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Lemon", "quantity": 2, "unit": "tablespoon", "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 1, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Red Onion", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": "halved lengthwise and cut into strips"},
                {"item_type": "ingredient", "ingredient": "Red Bell Pepper", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": "any color, cored, seeded, thinly sliced"},
                {"item_type": "ingredient", "ingredient": "Portobello Mushrooms", "quantity": 3, "unit": "whole", "size_qualifier": "large", "preparation_notes": "caps, cut into strips"},
                {"item_type": "ingredient", "ingredient": "Ground Black Cumin (Nigella Seeds)", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Dried Oregano", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Black Pepper", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "ground pippali or black pepper"},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Tortillas", "quantity": 4, "unit": "whole", "size_qualifier": "large", "preparation_notes": "warmed"},
                {"item_type": "sub_recipe", "sub_recipe_id": tomato_salsa_id, "quantity": 1, "unit": "as_needed", "preparation_notes": "optional, to serve"},
                {"item_type": "ingredient", "ingredient": "Fresh Cilantro", "quantity": 0.25, "unit": "cup", "preparation_notes": "15g, chopped"},
                {"item_type": "ingredient", "ingredient": "Lime", "quantity": 4, "unit": "whole", "preparation_notes": "wedges, to serve"},
            ],
            cursor=cursor,
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All remaining recipes created successfully!")
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

