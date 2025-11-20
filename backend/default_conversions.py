"""
Default conversion rules for common vegan ingredients.
Provides pre-calculated conversion factors so users don't need to calculate them manually.
"""
from typing import Dict, List, Optional

# Default conversions organized by ingredient
# Format: {ingredient_name: {shopping_unit: str, conversions: List[Dict]}}
DEFAULT_CONVERSIONS = {
    # Vegetables
    'Celery': {
        'shopping_unit': 'head',
        'conversions': [
            {'from': 'cup', 'category': 'volume', 'factor': 0.167},  # 1 head ≈ 6 cups chopped
            {'from': 'tablespoon', 'category': 'volume', 'factor': 0.0104},  # 1 head ≈ 96 tbsp chopped
            {'from': 'whole', 'category': 'count', 'factor': 1.0},  # 1 head = 1 head
        ],
        'size_estimation': []
    },
    'Onion': {
        'shopping_unit': 'piece',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.00667},  # 150g = 1 piece (medium)
            {'from': 'kilogram', 'category': 'weight', 'factor': 6.67},  # 1kg = 6.67 pieces
            {'from': 'cup', 'category': 'volume', 'factor': 1.0},  # 1 cup chopped ≈ 1 medium onion (150g)
            {'from': 'whole', 'category': 'count', 'factor': 1.0},  # 1 whole = 1 piece
        ],
        'size_estimation': [
            {'size': 'small', 'reference_unit': 'gram', 'value': 100},
            {'size': 'medium', 'reference_unit': 'gram', 'value': 150},
            {'size': 'large', 'reference_unit': 'gram', 'value': 200},
        ]
    },
    'Tomato': {
        'shopping_unit': 'piece',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.00667},  # 150g = 1 piece (medium)
            {'from': 'cup', 'category': 'volume', 'factor': 0.8},  # 1 cup chopped ≈ 1.25 pieces
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': [
            {'size': 'small', 'reference_unit': 'gram', 'value': 85},
            {'size': 'medium', 'reference_unit': 'gram', 'value': 150},
            {'size': 'large', 'reference_unit': 'gram', 'value': 200},
        ]
    },
    'Carrot': {
        'shopping_unit': 'piece',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.005},  # 200g = 1 piece
            {'from': 'cup', 'category': 'volume', 'factor': 1.0},  # 1 cup chopped/grated ≈ 1 carrot
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': [
            {'size': 'small', 'reference_unit': 'gram', 'value': 100},
            {'size': 'medium', 'reference_unit': 'gram', 'value': 150},
            {'size': 'large', 'reference_unit': 'gram', 'value': 200},
        ]
    },
    'Bell Pepper': {
        'shopping_unit': 'piece',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.005},  # 200g = 1 piece
            {'from': 'cup', 'category': 'volume', 'factor': 0.5},  # 1 cup chopped ≈ 2 pieces
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': [
            {'size': 'small', 'reference_unit': 'gram', 'value': 100},
            {'size': 'medium', 'reference_unit': 'gram', 'value': 150},
            {'size': 'large', 'reference_unit': 'gram', 'value': 250},
        ]
    },
    'Garlic': {
        'shopping_unit': 'clove',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.1},  # 10g = 1 clove
            {'from': 'whole', 'category': 'count', 'factor': 0.1},  # 1 head ≈ 10 cloves
            {'from': 'piece', 'category': 'count', 'factor': 1.0},  # 1 clove = 1 clove
        ],
        'size_estimation': []
    },
    'Potato': {
        'shopping_unit': 'piece',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.0025},  # 400g = 1 piece (large)
            {'from': 'kilogram', 'category': 'weight', 'factor': 2.5},  # 1kg = 2.5 pieces
            {'from': 'cup', 'category': 'volume', 'factor': 0.5},  # 1 cup diced ≈ 2 pieces
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': [
            {'size': 'small', 'reference_unit': 'gram', 'value': 150},
            {'size': 'medium', 'reference_unit': 'gram', 'value': 250},
            {'size': 'large', 'reference_unit': 'gram', 'value': 400},
        ]
    },
    'Sweet Potato': {
        'shopping_unit': 'piece',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.00333},  # 300g = 1 piece (medium)
            {'from': 'cup', 'category': 'volume', 'factor': 0.5},  # 1 cup mashed ≈ 2 pieces
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': [
            {'size': 'small', 'reference_unit': 'gram', 'value': 200},
            {'size': 'medium', 'reference_unit': 'gram', 'value': 300},
            {'size': 'large', 'reference_unit': 'gram', 'value': 450},
        ]
    },
    'Broccoli': {
        'shopping_unit': 'head',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.002},  # 500g = 1 head
            {'from': 'kilogram', 'category': 'weight', 'factor': 2.0},  # 1kg = 2 heads
            {'from': 'cup', 'category': 'volume', 'factor': 0.25},  # 1 head ≈ 4 cups chopped
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': []
    },
    'Cauliflower': {
        'shopping_unit': 'head',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.002},  # 500g = 1 head
            {'from': 'kilogram', 'category': 'weight', 'factor': 2.0},
            {'from': 'cup', 'category': 'volume', 'factor': 0.25},  # 1 head ≈ 4 cups chopped
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': []
    },
    'Cabbage': {
        'shopping_unit': 'head',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.001},  # 1000g = 1 head
            {'from': 'kilogram', 'category': 'weight', 'factor': 1.0},
            {'from': 'cup', 'category': 'volume', 'factor': 0.125},  # 1 head ≈ 8 cups shredded
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': []
    },
    'Spinach': {
        'shopping_unit': 'bunch',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.01},  # 100g = 1 bunch
            {'from': 'cup', 'category': 'volume', 'factor': 1.0},  # 1 cup fresh ≈ 1 bunch
            {'from': 'kilogram', 'category': 'weight', 'factor': 10.0},
        ],
        'size_estimation': []
    },
    'Lettuce': {
        'shopping_unit': 'head',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.001},  # 1000g = 1 head
            {'from': 'kilogram', 'category': 'weight', 'factor': 1.0},
            {'from': 'cup', 'category': 'volume', 'factor': 0.167},  # 1 head ≈ 6 cups shredded
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': []
    },
    
    # Fruits
    'Avocado': {
        'shopping_unit': 'piece',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.005},  # 200g = 1 piece
            {'from': 'cup', 'category': 'volume', 'factor': 2.0},  # 1 cup mashed ≈ 0.5 pieces
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': [
            {'size': 'small', 'reference_unit': 'gram', 'value': 150},
            {'size': 'medium', 'reference_unit': 'gram', 'value': 200},
            {'size': 'large', 'reference_unit': 'gram', 'value': 300},
        ]
    },
    'Lemon': {
        'shopping_unit': 'piece',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.01},  # 100g = 1 piece
            {'from': 'cup', 'category': 'volume', 'factor': 4.0},  # 1 cup juice ≈ 0.25 pieces (4 lemons per cup)
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': [
            {'size': 'small', 'reference_unit': 'gram', 'value': 75},
            {'size': 'medium', 'reference_unit': 'gram', 'value': 100},
            {'size': 'large', 'reference_unit': 'gram', 'value': 150},
        ]
    },
    'Lime': {
        'shopping_unit': 'piece',
        'conversions': [
            {'from': 'gram', 'category': 'weight', 'factor': 0.0125},  # 80g = 1 piece
            {'from': 'cup', 'category': 'volume', 'factor': 6.0},  # 1 cup juice ≈ 0.17 pieces
            {'from': 'whole', 'category': 'count', 'factor': 1.0},
        ],
        'size_estimation': [
            {'size': 'small', 'reference_unit': 'gram', 'value': 60},
            {'size': 'medium', 'reference_unit': 'gram', 'value': 80},
            {'size': 'large', 'reference_unit': 'gram', 'value': 100},
        ]
    },
    
    # Grains & Legumes
    'Rice': {
        'shopping_unit': 'package',
        'conversions': [
            {'from': 'cup', 'category': 'volume', 'factor': 0.0625},  # 1 package (16 cups) = 1 package
            {'from': 'gram', 'category': 'weight', 'factor': 0.0005},  # 2000g (2kg) package
            {'from': 'kilogram', 'category': 'weight', 'factor': 0.5},  # 2kg package
        ],
        'size_estimation': []
    },
    'Lentils': {
        'shopping_unit': 'package',
        'conversions': [
            {'from': 'cup', 'category': 'volume', 'factor': 0.125},  # 1 package (8 cups dry) = 1 package
            {'from': 'gram', 'category': 'weight', 'factor': 0.001},  # 1000g (1kg) package
            {'from': 'kilogram', 'category': 'weight', 'factor': 1.0},
        ],
        'size_estimation': []
    },
    'Quinoa': {
        'shopping_unit': 'package',
        'conversions': [
            {'from': 'cup', 'category': 'volume', 'factor': 0.0625},  # 1 package (16 cups dry)
            {'from': 'gram', 'category': 'weight', 'factor': 0.0005},  # 2000g package
            {'from': 'kilogram', 'category': 'weight', 'factor': 0.5},
        ],
        'size_estimation': []
    },
    
    # Herbs
    'Parsley': {
        'shopping_unit': 'bunch',
        'conversions': [
            {'from': 'cup', 'category': 'volume', 'factor': 0.5},  # 1 bunch ≈ 2 cups chopped
            {'from': 'gram', 'category': 'weight', 'factor': 0.05},  # 20g = 1 bunch
            {'from': 'tablespoon', 'category': 'volume', 'factor': 0.125},  # 1 bunch ≈ 8 tbsp
        ],
        'size_estimation': []
    },
    'Cilantro': {
        'shopping_unit': 'bunch',
        'conversions': [
            {'from': 'cup', 'category': 'volume', 'factor': 0.5},  # 1 bunch ≈ 2 cups chopped
            {'from': 'gram', 'category': 'weight', 'factor': 0.05},  # 20g = 1 bunch
            {'from': 'tablespoon', 'category': 'volume', 'factor': 0.125},
        ],
        'size_estimation': []
    },
    'Basil': {
        'shopping_unit': 'bunch',
        'conversions': [
            {'from': 'cup', 'category': 'volume', 'factor': 0.25},  # 1 bunch ≈ 4 cups chopped
            {'from': 'gram', 'category': 'weight', 'factor': 0.025},  # 40g = 1 bunch
            {'from': 'tablespoon', 'category': 'volume', 'factor': 0.0625},  # 1 bunch ≈ 16 tbsp
        ],
        'size_estimation': []
    },
    
    # Nuts & Seeds
    'Almonds': {
        'shopping_unit': 'package',
        'conversions': [
            {'from': 'cup', 'category': 'volume', 'factor': 0.0714},  # 1 package (14 cups) = 1 package
            {'from': 'gram', 'category': 'weight', 'factor': 0.0005},  # 2000g package
            {'from': 'kilogram', 'category': 'weight', 'factor': 0.5},
        ],
        'size_estimation': []
    },
    'Cashews': {
        'shopping_unit': 'package',
        'conversions': [
            {'from': 'cup', 'category': 'volume', 'factor': 0.0625},  # 1 package (16 cups)
            {'from': 'gram', 'category': 'weight', 'factor': 0.0005},  # 2000g package
            {'from': 'kilogram', 'category': 'weight', 'factor': 0.5},
        ],
        'size_estimation': []
    },
}


def get_default_conversions(ingredient_name: str) -> Optional[Dict]:
    """
    Get default conversion rules for an ingredient by name.
    
    Args:
        ingredient_name: Name of the ingredient (case-insensitive)
        
    Returns:
        Dict with 'shopping_unit', 'conversions', and 'size_estimation' keys, or None if not found
    """
    # Try exact match first
    if ingredient_name in DEFAULT_CONVERSIONS:
        return DEFAULT_CONVERSIONS[ingredient_name]
    
    # Try case-insensitive match
    for key, value in DEFAULT_CONVERSIONS.items():
        if key.lower() == ingredient_name.lower():
            return value
    
    return None


def apply_default_conversions(ingredient_name: str, shopping_unit_id: int, db) -> tuple:
    """
    Apply default conversion rules when creating an ingredient.
    
    Args:
        ingredient_name: Name of the ingredient
        shopping_unit_id: ID of the shopping unit selected by user
        db: Database connection
        
    Returns:
        Tuple of (conversion_rules, size_estimation_rules) lists ready for API
    """
    defaults = get_default_conversions(ingredient_name)
    if not defaults:
        return [], []
    
    cursor = db.cursor()
    
    # Get shopping unit name to verify it matches default
    cursor.execute("SELECT name FROM unit_types WHERE id = ?", (shopping_unit_id,))
    shopping_unit = cursor.fetchone()
    if not shopping_unit:
        return [], []
    
    # Check if user's shopping unit matches default shopping unit
    # If not, we'll still apply defaults but user might want to adjust
    default_shopping_unit = defaults['shopping_unit']
    if shopping_unit['name'] != default_shopping_unit:
        # User chose different shopping unit, still apply defaults but they may need adjustment
        pass
    
    # Get unit IDs by name
    unit_map = {}
    cursor.execute("SELECT id, name, category FROM unit_types")
    for unit in cursor.fetchall():
        unit_map[unit['name']] = unit['id']
    
    # Build conversion rules - convert to user's selected shopping unit
    conversion_rules = []
    for conv in defaults['conversions']:
        from_unit_name = conv['from']
        if from_unit_name in unit_map:
            # Calculate conversion factor to user's shopping unit
            # If default shopping unit matches user's selection, use default factor
            # Otherwise, we'd need intermediate conversion, but for simplicity use default
            factor = conv['factor']
            
            # If shopping unit doesn't match, we'd need to adjust factor
            # For now, if shopping units differ, skip or adjust
            if shopping_unit['name'] == default_shopping_unit:
                conversion_rules.append({
                    'from_unit_id': unit_map[from_unit_name],
                    'to_unit_id': shopping_unit_id,
                    'conversion_factor': factor
                })
    
    # Build size estimation rules
    size_estimation_rules = []
    for size_rule in defaults.get('size_estimation', []):
        ref_unit_name = size_rule['reference_unit']
        if ref_unit_name in unit_map:
            size_estimation_rules.append({
                'size_qualifier': size_rule['size'],
                'reference_unit_id': unit_map[ref_unit_name],
                'reference_value': size_rule['value']
            })
    
    return conversion_rules, size_estimation_rules


def get_available_default_ingredients() -> List[str]:
    """Get list of ingredients that have default conversions available."""
    return sorted(DEFAULT_CONVERSIONS.keys())

