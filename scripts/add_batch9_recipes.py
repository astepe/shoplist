#!/usr/bin/env python3
"""
Script to add all 10 main recipes for Batch 9:
1. Millet and Cauliflower-Topped Shepherd's Pie
2. Turmeric Quinoa with Broccoli, Chickpeas, and Tomatoes
3. Savory Polenta Bake
4. Sorghum with Corn and Arugula
5. Barley Risotto with Artichokes and Mushrooms
6. Black Rice Pilaf with Edamame and Barberries
7. Kasha with Purple Sweet Potatoes and Kale
8. Three-Grain Loaf
9. Provençal-Style Vegetable Bake
10. Farro and White Beans with Radicchio and Basil Pesto
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

def create_recipe(name, is_sub_recipe, yield_quantity, yield_unit_name, items, cursor):
    """Create a recipe with items."""
    yield_unit_id = get_unit_id(yield_unit_name, cursor)
    
    # Check if recipe already exists
    cursor.execute("SELECT id FROM recipes WHERE name = ?", (name,))
    existing = cursor.fetchone()
    if existing:
        print(f"  ⚠ Recipe '{name}' already exists (ID: {existing['id']}) - skipping")
        return existing['id']
    
    cursor.execute("""
        INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
        VALUES (?, ?, ?, ?)
    """, (name, is_sub_recipe, yield_quantity, yield_unit_id))
    
    recipe_id = cursor.lastrowid
    print(f"  ✓ Created recipe '{name}' (ID: {recipe_id})")
    
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
            item.get("size_qualifier"),
            item.get("preparation_notes")
        ))
    
    print(f"    ✓ Added {len(items)} items")
    return recipe_id

def main():
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating Batch 9 Recipes")
        print("=" * 60)
        
        # Get common unit IDs
        cup_unit_id = get_unit_id("cup", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        clove_unit_id = get_unit_id("clove", cursor)
        serving_unit_id = get_unit_id("serving", cursor)
        ounce_unit_id = get_unit_id("ounce", cursor)
        rib_unit_id = get_unit_id("rib", cursor)
        head_unit_id = get_unit_id("head", cursor)
        
        # Recipe 1: Millet and Cauliflower-Topped Shepherd's Pie
        print("\n--- Recipe 1: Millet and Cauliflower-Topped Shepherd's Pie ---")
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Whole-Grain Millet", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "180g, soaked in water for 8 hours or overnight"},
            {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 2.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "600ml, or water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Cauliflower Florets", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "285g, finely chopped or grated"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 2 tablespoons hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Onion Powder", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 1.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "300ml, or water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Brown Lentils", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "90g, or Green Lentils"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Tomato Paste", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Carrot", cursor), "quantity": 2, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Mushrooms", cursor), "quantity": 2, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "130g, chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Corn Kernels", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "160g, fresh or thawed frozen"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Frozen Green Peas", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "125g, fresh or thawed frozen"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Thyme", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "dried thyme"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Marjoram", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Onion Powder", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Smoked Paprika", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
        ]
        
        create_recipe("Millet and Cauliflower-Topped Shepherd's Pie", False, 6, "serving", items, cursor)
        
        # Recipe 2: Turmeric Quinoa with Broccoli, Chickpeas, and Tomatoes
        print("\n--- Recipe 2: Turmeric Quinoa with Broccoli, Chickpeas, and Tomatoes ---")
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        roasted_garlic_id, _ = get_sub_recipe_id("Roasted Garlic", cursor)
        
        items = [
            {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 1.75, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "410ml, or water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "small", "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Quinoa", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "180g, rinsed well and drained"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Turmeric", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.25 cup / 60ml hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Broccoli Florets", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "250g, small florets"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Chickpeas", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "370g, drained and rinsed"},
            {"item_type": "sub_recipe", "sub_recipe_id": roasted_garlic_id, "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Onion Powder", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Grape Tomatoes", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "225g, halved lengthwise"},
        ]
        
        create_recipe("Turmeric Quinoa with Broccoli, Chickpeas, and Tomatoes", False, 4, "serving", items, cursor)
        
        # Recipe 3: Savory Polenta Bake
        print("\n--- Recipe 3: Savory Polenta Bake ---")
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        balsamic_syrup_id, _ = get_sub_recipe_id("Balsamic Syrup", cursor)
        roasted_garlic_id, _ = get_sub_recipe_id("Roasted Garlic", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Cornmeal", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "155g, medium or coarse"},
            {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "1.2L, or water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Rainbow Chard", cursor), "quantity": 4, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "180g, chopped Swiss chard leaves"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced, or 2 teaspoons Roasted Garlic"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.25 cup / 60ml hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Cherry Tomatoes", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "150g, quartered"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Basil", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Oregano", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Fennel Seeds", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "sub_recipe", "sub_recipe_id": balsamic_syrup_id, "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "drizzle, optional"},
        ]
        
        create_recipe("Savory Polenta Bake", False, 4, "serving", items, cursor)
        
        # Recipe 4: Sorghum with Corn and Arugula
        print("\n--- Recipe 4: Sorghum with Corn and Arugula ---")
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Sorghum", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "190g, whole-grain, soaked in water for 8 hours or overnight"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "finely chopped"},
            {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "700ml"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1.5, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.5 cup / 60ml hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Bell Pepper", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "120g, finely chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Corn Kernels", cursor), "quantity": 2, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "320g, fresh or thawed frozen"},
            {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lemon", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "fresh lemon juice"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pepitas (Pumpkin Seeds)", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Cilantro", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "chopped, optional"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Arugula", cursor), "quantity": 4, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "120g, chopped"},
        ]
        
        create_recipe("Sorghum with Corn and Arugula", False, 4, "serving", items, cursor)
        
        # Recipe 5: Barley Risotto with Artichokes and Mushrooms
        print("\n--- Recipe 5: Barley Risotto with Artichokes and Mushrooms ---")
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Frozen Artichoke Hearts", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "10-12 oz / 280-340g package, thawed and chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Mushrooms", cursor), "quantity": 8, "unit_id": ounce_unit_id, "size_qualifier": None, "preparation_notes": "225g, sliced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 3, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Barley Groats", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "185g, rinsed well and drained"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.25 cup / 60ml hot water"},
            {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Thyme", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "minced, or 0.5 teaspoon Ground Thyme"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Onion Powder", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 3.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "825ml, or more as needed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Sodium-Free Salt Substitute", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "optional"},
        ]
        
        create_recipe("Barley Risotto with Artichokes and Mushrooms", False, 4, "serving", items, cursor)
        
        # Recipe 6: Black Rice Pilaf with Edamame and Barberries
        print("\n--- Recipe 6: Black Rice Pilaf with Edamame and Barberries ---")
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Barberries", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "40g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "finely chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Turmeric", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Shelled Edamame", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "120g, cooked"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Rice", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "525g, cooked"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Scallions", cursor), "quantity": 2, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "green and white parts, chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Almonds", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "40g, slivered"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Parsley", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "or Fresh Cilantro, minced"},
        ]
        
        create_recipe("Black Rice Pilaf with Edamame and Barberries", False, 4, "serving", items, cursor)
        
        # Recipe 7: Kasha with Purple Sweet Potatoes and Kale
        print("\n--- Recipe 7: Kasha with Purple Sweet Potatoes and Kale ---")
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Purple Sweet Potatoes", cursor), "quantity": 2, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "peeled and cut into 0.5-inch/1-cm dice"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Bell Pepper", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "cored, seeded, and chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Onion Powder", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "350ml, or water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Kasha (Roasted Buckwheat Groats)", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "180g, medium-grain roasted"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Kale", cursor), "quantity": 4, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "85g, chopped, stems removed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Chickpeas", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "370g, drained and rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 2 tablespoons hot water"},
            {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
        ]
        
        create_recipe("Kasha with Purple Sweet Potatoes and Kale", False, 4, "serving", items, cursor)
        
        # Recipe 8: Three-Grain Loaf
        print("\n--- Recipe 8: Three-Grain Loaf ---")
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        umami_sauce_id, _ = get_sub_recipe_id("Umami Sauce", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "finely chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Celery", cursor), "quantity": 1, "unit_id": rib_unit_id, "size_qualifier": "large", "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 4, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Carrot", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "finely grated"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Barley Groats", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60g raw, rinsed well and drained, or 1 cup / 180g cooked"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Whole-Grain Millet", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60g raw, rinsed well and drained, or 1 cup / 180g cooked"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Quinoa", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60g raw, rinsed well and drained, or 1 cup / 180g cooked"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Walnuts", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "50g, chopped or coarsely crushed, or Pecan Pieces"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Flaxseeds", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Parsley", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "80g, finely chopped"},
            {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Thyme", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Sage", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Sodium-Free Salt Substitute", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "optional"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Whole-Grain Bread Crumbs", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "40g, or more as needed"},
            {"item_type": "sub_recipe", "sub_recipe_id": umami_sauce_id, "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
        ]
        
        create_recipe("Three-Grain Loaf", False, 6, "serving", items, cursor)
        
        # Recipe 9: Provençal-Style Vegetable Bake
        print("\n--- Recipe 9: Provençal-Style Vegetable Bake ---")
        nutty_parm_id, _ = get_sub_recipe_id("Nutty Parm", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "halved lengthwise and chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Yellow Potatoes", cursor), "quantity": 4, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "red potatoes, scrubbed, unpeeled, and cut into 0.25-inch/0.5-cm slices"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Japanese Eggplant", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "trimmed, halved lengthwise, and cut into 0.25-inch/0.5-cm slices"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Zucchini", cursor), "quantity": 3, "unit_id": whole_unit_id, "size_qualifier": "small", "preparation_notes": "cut into 0.25-inch/0.5-cm slices"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Plum Tomatoes", cursor), "quantity": 3, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "cut into 0.25-inch/0.5-cm slices"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 2 tablespoons hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Thyme", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "fresh thyme leaves, or 1 teaspoon Ground Thyme"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Marjoram", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Onion Powder", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Sodium-Free Salt Substitute", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "optional"},
            {"item_type": "sub_recipe", "sub_recipe_id": nutty_parm_id, "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "30g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Wheat Germ", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "30g, or Whole-Grain Bread Crumbs"},
        ]
        
        create_recipe("Provençal-Style Vegetable Bake", False, 4, "serving", items, cursor)
        
        # Recipe 10: Farro and White Beans with Radicchio and Basil Pesto
        print("\n--- Recipe 10: Farro and White Beans with Radicchio and Basil Pesto ---")
        basil_pesto_id, _ = get_sub_recipe_id("Basil Pesto", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Farro", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "165g raw, or 3 cups / 600g cooked"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "sub_recipe", "sub_recipe_id": basil_pesto_id, "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "120ml, or more"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Cannellini Beans", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "375g, drained and rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Radicchio", cursor), "quantity": 1, "unit_id": head_unit_id, "size_qualifier": None, "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper, to taste"},
        ]
        
        create_recipe("Farro and White Beans with Radicchio and Basil Pesto", False, 4, "serving", items, cursor)
        
        db.commit()
        print("\n" + "=" * 60)
        print("✓ All 10 recipes created successfully!")
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

