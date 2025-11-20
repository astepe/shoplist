#!/usr/bin/env python3
"""
Script to rename recipe images based on manual mapping.
Since we can't visually inspect images, you need to provide which image numbers 
correspond to which recipes.
"""

import os
import re
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db

def sanitize_filename(name):
    """Convert recipe name to a safe filename."""
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name.strip('_').lower()

def get_recipes():
    """Get all main recipes from database."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, name FROM recipes 
        WHERE is_sub_recipe = 0
        ORDER BY id
    """)
    recipes = cursor.fetchall()
    db.close()
    return recipes

def extract_image_number(filename):
    """Extract the number from image filename."""
    match = re.search(r'_(\d+)\.', filename)
    return int(match.group(1)) if match else None

def main():
    """Main function to rename images."""
    image_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "how_not_to_age_cookbook")
    
    if not os.path.exists(image_dir):
        print(f"Error: Directory not found: {image_dir}")
        sys.exit(1)
    
    # Get recipes
    recipes = get_recipes()
    
    # Get all image files
    all_images = [f for f in os.listdir(image_dir) if f.endswith('.JPG')]
    images = sorted([f for f in all_images if 'copy' not in f.lower()], 
                    key=lambda x: extract_image_number(x) or 0)
    
    print("=" * 60)
    print("Recipe Image Renaming")
    print("=" * 60)
    print(f"\nFound {len(recipes)} recipes and {len(images)} images")
    
    print("\nRecipes (in order):")
    for i, recipe in enumerate(recipes):
        print(f"  {i+1:2d}. {recipe['name']} (ID: {recipe['id']})")
    
    print(f"\nImages: numbered {extract_image_number(images[0])} to {extract_image_number(images[-1])}")
    
    # MANUAL MAPPING - You need to specify which image numbers correspond to which recipes
    # Format: recipe_name: [image_numbers]
    # For multi-page recipes, list multiple image numbers
    
    print("\n" + "=" * 60)
    print("MANUAL MAPPING REQUIRED")
    print("=" * 60)
    print("\nPlease provide the mapping of image numbers to recipes.")
    print("Since some recipes span 2 pages, specify which image numbers each recipe uses.")
    print("\nExample format:")
    print("  Curried Butternut Soup with Rainbow Chard: [16, 17]")
    print("  Baked Carrot Cake Oatmeal: [18]")
    print("  etc.")
    
    # Create a mapping dictionary - EDIT THIS with the actual mapping
    # This is a placeholder that needs to be filled in
    manual_mapping = {
        # "Recipe Name": [image_numbers]
        # Example:
        # "Curried Butternut Soup with Rainbow Chard": [16, 17],
        # "Baked Carrot Cake Oatmeal": [18, 19],
        # etc.
    }
    
    # If no manual mapping provided, use a default (assuming sequential order, 1-2 pages per recipe)
    if not manual_mapping:
        print("\nNo manual mapping provided. Using default sequential mapping...")
        print("WARNING: This assumes recipes appear sequentially and each takes ~9-10 pages.")
        print("This is likely incorrect - please provide the correct mapping.")
        
        # Default sequential mapping (evenly distribute)
        images_per_recipe = len(images) // len(recipes)
        remainder = len(images) % len(recipes)
        
        image_index = 0
        manual_mapping = {}
        
        for recipe in recipes:
            num_pages = images_per_recipe + (1 if len(manual_mapping) < remainder else 0)
            image_numbers = []
            for _ in range(num_pages):
                if image_index < len(images):
                    image_numbers.append(extract_image_number(images[image_index]))
                    image_index += 1
            manual_mapping[recipe['name']] = image_numbers
    
    # Create filename mapping
    print("\n" + "=" * 60)
    print("RENAMING PLAN")
    print("=" * 60)
    
    rename_map = {}
    for recipe_name, image_numbers in manual_mapping.items():
        sanitized_name = sanitize_filename(recipe_name)
        
        # Find image files with these numbers
        for i, img_num in enumerate(image_numbers):
            # Find the image file with this number
            matching_images = [img for img in images if extract_image_number(img) == img_num]
            
            if not matching_images:
                print(f"  ⚠ Warning: No image found with number {img_num} for {recipe_name}")
                continue
            
            img_file = matching_images[0]
            
            # Determine new name
            if len(image_numbers) > 1:
                new_name = f"{sanitized_name}_page{i+1}.JPG"
            else:
                new_name = f"{sanitized_name}.JPG"
            
            rename_map[img_file] = new_name
            
            print(f"  {img_file} -> {new_name}")
    
    # Confirm and rename
    print(f"\nTotal files to rename: {len(rename_map)}")
    response = input("\nProceed with renaming? (yes/no): ").strip().lower()
    
    if response == 'yes':
        renamed_count = 0
        errors = []
        
        for old_name, new_name in rename_map.items():
            old_path = os.path.join(image_dir, old_name)
            new_path = os.path.join(image_dir, new_name)
            
            if os.path.exists(new_path) and new_path != old_path:
                errors.append(f"{new_name} already exists")
                continue
            
            try:
                os.rename(old_path, new_path)
                renamed_count += 1
            except Exception as e:
                errors.append(f"Error renaming {old_name}: {e}")
        
        print(f"\n✓ Renamed {renamed_count} files")
        
        if errors:
            print(f"\n⚠ {len(errors)} errors:")
            for error in errors[:10]:  # Show first 10
                print(f"  {error}")
    else:
        print("\nRenaming cancelled.")
        print("\nTo provide the correct mapping, edit this script and modify the 'manual_mapping' dictionary.")

if __name__ == '__main__':
    main()
