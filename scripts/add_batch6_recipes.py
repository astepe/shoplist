#!/usr/bin/env python3
"""
Script to create all Batch 6 recipes.
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
        print("Creating Batch 6 Recipes")
        print("=" * 60)
        
        # Get sub-recipes
        umami_id, _ = get_sub_recipe_id("Umami Sauce", cursor)
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        nutty_parm_id, _ = get_sub_recipe_id("Nutty Parm", cursor)
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        balsamic_syrup_id, _ = get_sub_recipe_id("Balsamic Syrup", cursor)
        
        # Recipe 1: Grilled Vegetable Skewers with Umami Sauce
        print("\n--- Recipe 1: Grilled Vegetable Skewers with Umami Sauce ---")
        create_recipe(
            name="Grilled Vegetable Skewers with Umami Sauce",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Yellow Bell Pepper", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": "cored, seeded, cut into 1½-inch pieces"},
                {"item_type": "ingredient", "ingredient": "Zucchini", "quantity": 2, "unit": "whole", "size_qualifier": "small", "preparation_notes": "cut into 1-inch chunks"},
                {"item_type": "ingredient", "ingredient": "Mushrooms", "quantity": 8, "unit": "ounce", "preparation_notes": "225g, fresh button or cremini mushrooms, halved lengthwise if large"},
                {"item_type": "ingredient", "ingredient": "Shallot", "quantity": 6, "unit": "whole", "preparation_notes": "halved lengthwise"},
                {"item_type": "ingredient", "ingredient": "Cherry Tomatoes", "quantity": 16, "unit": "whole", "size_qualifier": "large", "preparation_notes": "cherry or Campari tomatoes"},
                {"item_type": "ingredient", "ingredient": "Onion Powder", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Black Pepper", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "ground pippali or black pepper"},
                {"item_type": "sub_recipe", "sub_recipe_id": umami_id, "quantity": 0.5, "unit": "cup", "preparation_notes": "120ml, warmed"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 2: White Bean Mac & Cheese with Grape Tomatoes and Peas
        print("\n--- Recipe 2: White Bean Mac & Cheese with Grape Tomatoes and Peas ---")
        create_recipe(
            name="White Bean Mac & Cheese with Grape Tomatoes and Peas",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Yellow Onion", "quantity": 0.5, "unit": "cup", "preparation_notes": "60g, chopped"},
                {"item_type": "ingredient", "ingredient": "Russet Potatoes", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": "peeled and chopped"},
                {"item_type": "ingredient", "ingredient": "Garlic", "quantity": 1, "unit": "clove", "size_qualifier": "large", "preparation_notes": "chopped"},
                {"item_type": "ingredient", "ingredient": "Salt-Free White Beans", "quantity": 1.5, "unit": "cup", "preparation_notes": "375g, home-cooked or from BPA-free cans, drained and rinsed (cannellini beans)"},
                {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 1, "unit": "cup", "preparation_notes": "235ml, or water"},
                {"item_type": "ingredient", "ingredient": "Ground Turmeric", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Onion Powder", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Ground Paprika", "quantity": 0.75, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Unsweetened Soy Milk", "quantity": 1, "unit": "cup", "preparation_notes": "235ml"},
                {"item_type": "ingredient", "ingredient": "Nutritional Yeast", "quantity": 0.33, "unit": "cup", "preparation_notes": "25g"},
                {"item_type": "ingredient", "ingredient": "Lemon", "quantity": 1, "unit": "tablespoon", "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 1, "unit": "tablespoon", "preparation_notes": "blended with 0.25 cup hot water, 60ml"},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Elbow Macaroni", "quantity": 8, "unit": "ounce", "preparation_notes": "225g"},
                {"item_type": "ingredient", "ingredient": "Frozen Green Peas", "quantity": 1, "unit": "cup", "preparation_notes": "125g, thawed"},
                {"item_type": "ingredient", "ingredient": "Grape Tomatoes", "quantity": 1, "unit": "cup", "preparation_notes": "150g, halved lengthwise"},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Bread Crumbs", "quantity": 0.5, "unit": "cup", "preparation_notes": "60g"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 3: Tomato Pesto Pasta with Green Beans, Chickpeas, and Bell Peppers
        print("\n--- Recipe 3: Tomato Pesto Pasta with Green Beans, Chickpeas, and Bell Peppers ---")
        create_recipe(
            name="Tomato Pesto Pasta with Green Beans, Chickpeas, and Bell Peppers",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Garlic", "quantity": 3, "unit": "clove", "size_qualifier": "large", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Pine Nuts", "quantity": 0.33, "unit": "cup", "preparation_notes": "45g, or slivered almonds"},
                {"item_type": "ingredient", "ingredient": "Ripe Tomatoes", "quantity": 12, "unit": "ounce", "preparation_notes": "340g, Roma tomatoes, stem end removed, quartered lengthwise"},
                {"item_type": "ingredient", "ingredient": "Fresh Basil", "quantity": 1, "unit": "cup", "preparation_notes": "30g, packed fresh leaves"},
                {"item_type": "ingredient", "ingredient": "Nutritional Yeast", "quantity": 2, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 1, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Spaghetti", "quantity": 8, "unit": "ounce", "preparation_notes": "225g"},
                {"item_type": "ingredient", "ingredient": "Green Beans", "quantity": 8, "unit": "ounce", "preparation_notes": "225g, trimmed and cut into 1-inch pieces"},
                {"item_type": "ingredient", "ingredient": "Yellow Bell Pepper", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": "cored, seeded, cut into ½-inch pieces"},
                {"item_type": "ingredient", "ingredient": "Red Bell Pepper", "quantity": 1, "unit": "whole", "size_qualifier": "small", "preparation_notes": "or orange bell pepper, cored, seeded, cut into ½-inch pieces"},
                {"item_type": "ingredient", "ingredient": "Salt-Free Chickpeas", "quantity": 1.5, "unit": "cup", "preparation_notes": "370g, home-cooked or from BPA-free cans, drained and rinsed"},
                {"item_type": "sub_recipe", "sub_recipe_id": nutty_parm_id, "quantity": 1, "unit": "as_needed", "preparation_notes": "optional, to serve"},
                {"item_type": "ingredient", "ingredient": "Red Pepper Flakes", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "optional, 0.25 to 0.5 teaspoon"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 4: Vegetable Sheet Pan Supper
        print("\n--- Recipe 4: Vegetable Sheet Pan Supper ---")
        create_recipe(
            name="Vegetable Sheet Pan Supper",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Beets", "quantity": 1, "unit": "pound", "preparation_notes": "455g, peeled and cut into 1-inch pieces"},
                {"item_type": "ingredient", "ingredient": "Red Onion", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": "halved lengthwise and sliced"},
                {"item_type": "ingredient", "ingredient": "Purple Sweet Potatoes", "quantity": 1, "unit": "pound", "preparation_notes": "455g, purple or orange sweet potatoes, peeled and cut into 1-inch pieces"},
                {"item_type": "ingredient", "ingredient": "Red Bell Pepper", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": "halved, seeded, and sliced"},
                {"item_type": "ingredient", "ingredient": "Brussels Sprouts", "quantity": 8, "unit": "ounce", "preparation_notes": "225g, trimmed and halved"},
                {"item_type": "ingredient", "ingredient": "Salt-Free Chickpeas", "quantity": 1.5, "unit": "cup", "preparation_notes": "370g, home-cooked or from BPA-free cans, drained and rinsed"},
                {"item_type": "ingredient", "ingredient": "Garlic", "quantity": 3, "unit": "clove", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Lemon", "quantity": 3, "unit": "tablespoon", "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient": "Nutritional Yeast", "quantity": 1, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Ground Thyme", "quantity": 1, "unit": "teaspoon", "preparation_notes": "dried"},
                {"item_type": "ingredient", "ingredient": "Dried Oregano", "quantity": 1, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 1, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Black Pepper", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": "ground pippali or black pepper"},
                {"item_type": "ingredient", "ingredient": "Cherry Tomatoes", "quantity": 2, "unit": "cup", "preparation_notes": "300g"},
                {"item_type": "ingredient", "ingredient": "Fresh Parsley", "quantity": 0.25, "unit": "cup", "preparation_notes": "15g, chopped fresh flat-leaf parsley or basil"},
                {"item_type": "ingredient", "ingredient": "Sodium-Free Salt Substitute", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "optional"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 5: Kale and Millet-Stuffed Bell Peppers
        print("\n--- Recipe 5: Kale and Millet-Stuffed Bell Peppers ---")
        create_recipe(
            name="Kale and Millet-Stuffed Bell Peppers",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Whole-Grain Millet", "quantity": 1, "unit": "cup", "preparation_notes": "180g, rinsed well and drained"},
                {"item_type": "ingredient", "ingredient": "Red Onion", "quantity": 1, "unit": "whole", "size_qualifier": "medium", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Kale", "quantity": 4, "unit": "cup", "preparation_notes": "85g, coarsely chopped, stems removed"},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 1, "unit": "tablespoon", "preparation_notes": "blended with 0.5 cup hot water, 60ml"},
                {"item_type": "ingredient", "ingredient": "Dried Barberries", "quantity": 0.25, "unit": "cup", "preparation_notes": "35g, soaked in hot water for 10 minutes, then drained"},
                {"item_type": "ingredient", "ingredient": "Sunflower Seeds", "quantity": 2, "unit": "tablespoon", "preparation_notes": "unsalted"},
                {"item_type": "ingredient", "ingredient": "Ground Flaxseeds", "quantity": 1, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Nutritional Yeast", "quantity": 2, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Black Pepper", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "ground pippali or black pepper"},
                {"item_type": "ingredient", "ingredient": "Sodium-Free Salt Substitute", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": "optional"},
                {"item_type": "ingredient", "ingredient": "Red Bell Pepper", "quantity": 4, "unit": "whole", "size_qualifier": "large", "preparation_notes": "halved lengthwise and seeded"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 6: Kabocha Squash with Black Rice and Beans
        print("\n--- Recipe 6: Kabocha Squash with Black Rice and Beans ---")
        create_recipe(
            name="Kabocha Squash with Black Rice and Beans",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Black Rice", "quantity": 0.75, "unit": "cup", "preparation_notes": "135g"},
                {"item_type": "ingredient", "ingredient": "Kabocha Squash", "quantity": 2, "unit": "whole", "size_qualifier": "small", "preparation_notes": "or other small winter squashes, halved and seeded"},
                {"item_type": "ingredient", "ingredient": "Raw Walnuts", "quantity": 0.33, "unit": "cup", "preparation_notes": "35g, walnut pieces"},
                {"item_type": "ingredient", "ingredient": "Red Bell Pepper", "quantity": 1, "unit": "whole", "size_qualifier": "small", "preparation_notes": "or yellow bell pepper, cored, seeded, finely chopped"},
                {"item_type": "ingredient", "ingredient": "Scallions", "quantity": 6, "unit": "whole", "preparation_notes": "green and white parts, minced"},
                {"item_type": "ingredient", "ingredient": "Garlic", "quantity": 2, "unit": "clove", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Fresh Ginger", "quantity": 2, "unit": "teaspoon", "preparation_notes": "grated"},
                {"item_type": "ingredient", "ingredient": "Salt-Free Black Beans", "quantity": 1.5, "unit": "cup", "preparation_notes": "375g, home-cooked or from BPA-free cans, drained and rinsed"},
                {"item_type": "sub_recipe", "sub_recipe_id": umami_id, "quantity": 2, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Fresh Cilantro", "quantity": 0.25, "unit": "cup", "preparation_notes": "15g, minced fresh cilantro or parsley"},
                {"item_type": "ingredient", "ingredient": "Onion Powder", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Sodium-Free Salt Substitute", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "optional"},
                {"item_type": "sub_recipe", "sub_recipe_id": balsamic_syrup_id, "quantity": 1, "unit": "as_needed", "preparation_notes": "optional, to serve"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 7: Cabbage Rolls Stuffed with Bulgur and White Beans
        print("\n--- Recipe 7: Cabbage Rolls Stuffed with Bulgur and White Beans ---")
        create_recipe(
            name="Cabbage Rolls Stuffed with Bulgur and White Beans",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Green Cabbage", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Yellow Onion", "quantity": 1, "unit": "whole", "size_qualifier": "medium", "preparation_notes": "finely chopped"},
                {"item_type": "ingredient", "ingredient": "Carrot", "quantity": 1, "unit": "whole", "size_qualifier": "small", "preparation_notes": "finely chopped"},
                {"item_type": "ingredient", "ingredient": "Red Bell Pepper", "quantity": 1, "unit": "whole", "size_qualifier": "small", "preparation_notes": "cored, seeded, finely chopped"},
                {"item_type": "ingredient", "ingredient": "Medium Bulgur", "quantity": 1, "unit": "cup", "preparation_notes": "140g"},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 1, "unit": "tablespoon", "preparation_notes": "blended with 0.25 cup hot water, 60ml"},
                {"item_type": "ingredient", "ingredient": "Salt-Free White Beans", "quantity": 1.5, "unit": "cup", "preparation_notes": "365g, Great Northern white beans or other small white beans, home-cooked or from BPA-free cans, drained and rinsed"},
                {"item_type": "ingredient", "ingredient": "Dried Barberries", "quantity": 2, "unit": "tablespoon", "preparation_notes": "soaked in hot water for 10 minutes, then drained"},
                {"item_type": "sub_recipe", "sub_recipe_id": umami_id, "quantity": 1, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Fresh Parsley", "quantity": 0.25, "unit": "cup", "preparation_notes": "15g, minced"},
                {"item_type": "ingredient", "ingredient": "Ground Thyme", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": "dried"},
                {"item_type": "ingredient", "ingredient": "Garlic Powder", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Black Pepper", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "ground pippali or black pepper"},
                {"item_type": "ingredient", "ingredient": "Lemon", "quantity": 1, "unit": "tablespoon", "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient": "Sodium-Free Salt Substitute", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": "optional"},
                {"item_type": "ingredient", "ingredient": "Salt-Free Marinara Sauce", "quantity": 2, "unit": "cup", "preparation_notes": "475ml"},
                {"item_type": "ingredient", "ingredient": "Balsamic Vinegar", "quantity": 1, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Date Sugar", "quantity": 1, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Onion Powder", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 8: Singapore-Style Noodles with Tempeh
        print("\n--- Recipe 8: Singapore-Style Noodles with Tempeh ---")
        create_recipe(
            name="Singapore-Style Noodles with Tempeh",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Tempeh", "quantity": 1, "unit": "package", "preparation_notes": "8 oz, 230g, cut into ½-inch dice"},
                {"item_type": "sub_recipe", "sub_recipe_id": umami_id, "quantity": 3, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Creamy Peanut Butter", "quantity": 0.5, "unit": "cup", "preparation_notes": "130g"},
                {"item_type": "ingredient", "ingredient": "Lemon", "quantity": 2, "unit": "tablespoon", "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient": "Yellow Curry Powder", "quantity": 1.5, "unit": "teaspoon", "preparation_notes": "or more"},
                {"item_type": "ingredient", "ingredient": "Ground Cayenne", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Napa Cabbage", "quantity": 3, "unit": "cup", "preparation_notes": "250g, shredded, or bok choy"},
                {"item_type": "ingredient", "ingredient": "Red Bell Pepper", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": "cored, seeded, chopped"},
                {"item_type": "ingredient", "ingredient": "Garlic", "quantity": 2, "unit": "clove", "size_qualifier": "large", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Scallions", "quantity": 0.5, "unit": "cup", "preparation_notes": "20g, chopped, green and white parts"},
                {"item_type": "ingredient", "ingredient": "Fresh Ginger", "quantity": 2, "unit": "teaspoon", "preparation_notes": "grated"},
                {"item_type": "ingredient", "ingredient": "Whole-Grain Angel Hair Pasta", "quantity": 8, "unit": "ounce", "preparation_notes": "225g"},
                {"item_type": "ingredient", "ingredient": "Frozen Green Peas", "quantity": 1, "unit": "cup", "preparation_notes": "125g, thawed"},
                {"item_type": "ingredient", "ingredient": "Unsalted Peanuts", "quantity": 0.25, "unit": "cup", "preparation_notes": "32g, chopped"},
                {"item_type": "ingredient", "ingredient": "Fresh Cilantro", "quantity": 2, "unit": "tablespoon", "preparation_notes": "minced"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 9: Winter Vegetable Stew
        print("\n--- Recipe 9: Winter Vegetable Stew ---")
        create_recipe(
            name="Winter Vegetable Stew",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Red Onion", "quantity": 1.5, "unit": "cup", "preparation_notes": "180g, chopped"},
                {"item_type": "ingredient", "ingredient": "Carrot", "quantity": 1.5, "unit": "cup", "preparation_notes": "165g, chopped"},
                {"item_type": "ingredient", "ingredient": "Celery", "quantity": 1, "unit": "rib", "size_qualifier": "large", "preparation_notes": "chopped"},
                {"item_type": "ingredient", "ingredient": "Garlic", "quantity": 2, "unit": "clove", "preparation_notes": "minced"},
                {"item_type": "ingredient", "ingredient": "Fresh Ginger", "quantity": 1, "unit": "teaspoon", "preparation_notes": "grated, 1 or 2 teaspoons"},
                {"item_type": "ingredient", "ingredient": "Onion Powder", "quantity": 0.75, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Ground Black Cumin (Nigella Seeds)", "quantity": 0.75, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Smoked Paprika", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Ground Thyme", "quantity": 0.75, "unit": "teaspoon", "preparation_notes": "dried"},
                {"item_type": "ingredient", "ingredient": "Fresh Turmeric", "quantity": 2, "unit": "whole", "preparation_notes": "slices, or 0.25 teaspoon ground turmeric powder"},
                {"item_type": "ingredient", "ingredient": "Bay Leaf", "quantity": 1, "unit": "whole", "preparation_notes": None},
                {"item_type": "ingredient", "ingredient": "Purple Sweet Potatoes", "quantity": 3, "unit": "cup", "preparation_notes": "330g, peeled and diced"},
                {"item_type": "ingredient", "ingredient": "Green Beans", "quantity": 8, "unit": "ounce", "preparation_notes": "225g, trimmed and cut into 1-inch pieces"},
                {"item_type": "ingredient", "ingredient": "Kale", "quantity": 2, "unit": "cup", "preparation_notes": "45g, chopped, stems removed"},
                {"item_type": "ingredient", "ingredient": "Salt-Free Diced Tomatoes", "quantity": 1, "unit": "can", "preparation_notes": "14.5 oz, 400g, BPA-free can or Tetra Pak, undrained"},
                {"item_type": "ingredient", "ingredient": "Salt-Free Chickpeas", "quantity": 1.5, "unit": "cup", "preparation_notes": "370g, home-cooked or from BPA-free cans, drained and rinsed"},
                {"item_type": "ingredient", "ingredient": "Frozen Green Peas", "quantity": 0.5, "unit": "cup", "preparation_notes": "65g"},
                {"item_type": "ingredient", "ingredient": "White Miso Paste", "quantity": 1, "unit": "tablespoon", "preparation_notes": "blended with 0.25 cup hot water, 60ml"},
                {"item_type": "ingredient", "ingredient": "Black Pepper", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "ground pippali or black pepper"},
                {"item_type": "ingredient", "ingredient": "Sodium-Free Salt Substitute", "quantity": 0.25, "unit": "teaspoon", "preparation_notes": "optional"},
                {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 1, "unit": "cup", "preparation_notes": "235ml, or water"},
            ],
            cursor=cursor,
            db=db
        )
        
        # Recipe 10: Tahini Soba Noodles with Bok Choy
        print("\n--- Recipe 10: Tahini Soba Noodles with Bok Choy ---")
        create_recipe(
            name="Tahini Soba Noodles with Bok Choy",
            is_sub_recipe=False,
            yield_quantity=4,
            yield_unit_name="serving",
            items=[
                {"item_type": "ingredient", "ingredient": "Tahini", "quantity": 3, "unit": "tablespoon", "preparation_notes": None},
                {"item_type": "sub_recipe", "sub_recipe_id": umami_id, "quantity": 0.5, "unit": "cup", "preparation_notes": "80ml"},
                {"item_type": "ingredient", "ingredient": "Lemon", "quantity": 1, "unit": "tablespoon", "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient": "Red Pepper Flakes", "quantity": 0.5, "unit": "teaspoon", "preparation_notes": "optional"},
                {"item_type": "ingredient", "ingredient": "Red Onion", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": "halved lengthwise and thinly sliced"},
                {"item_type": "ingredient", "ingredient": "Bok Choy", "quantity": 3, "unit": "cup", "preparation_notes": "250g, shredded, or napa cabbage"},
                {"item_type": "ingredient", "ingredient": "Carrot", "quantity": 1, "unit": "whole", "size_qualifier": "large", "preparation_notes": "thinly sliced"},
                {"item_type": "ingredient", "ingredient": "Snow Peas", "quantity": 1, "unit": "cup", "preparation_notes": "80g, trimmed"},
                {"item_type": "ingredient", "ingredient": "Fresh Ginger", "quantity": 2, "unit": "teaspoon", "preparation_notes": "grated"},
                {"item_type": "ingredient", "ingredient": "Soba Noodles", "quantity": 8, "unit": "ounce", "preparation_notes": "225g"},
                {"item_type": "ingredient", "ingredient": "Raw Sesame Seeds", "quantity": 2, "unit": "tablespoon", "preparation_notes": None},
            ],
            cursor=cursor,
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All recipes created successfully!")
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

