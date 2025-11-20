# ShopList

A web application for managing recipes and generating aggregated shopping lists with intelligent unit conversion. Perfect for meal planning and grocery shopping!

## Features

- **Recipe Management**: Create and manage recipes with ingredients and sub-recipes
- **Ingredient Management**: Configure ingredients with conversion rules and size estimation
- **Shopping List Generation**: Aggregate ingredients across multiple recipes with intelligent unit conversion
- **Sub-Recipe Support**: Recipes can reference other recipes as ingredients
- **Size Qualifier Preservation**: Preserves size qualifiers for count-based units, estimates them for volume/weight conversions
- **Copyable Shopping Lists**: Generate formatted shopping lists that can be easily copied and pasted
- **Progressive Web App**: Install on iPad/iPhone for easy access
- **Ingredient Search**: Search recipes by ingredient names

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (Vanilla)

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd shoplist
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize the Database

The database will be automatically initialized when you first run the application. However, to populate it with default ingredients and conversion formulas, run:

```bash
python setup_database.py
```

This script will:
- Create the database schema (if it doesn't exist)
- Load all default ingredients from `backend/default_conversions.py`
- Add conversion formulas for common ingredients
- **Note**: Recipes are NOT included - you'll add your own through the web interface

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000` (or `http://0.0.0.0:5000` for network access).

### 5. Access the Application

Open your browser and navigate to:
- **Local**: `http://localhost:5000`
- **Network**: `http://<your-ip>:5000` (for iPad/iPhone access)

## Default Data

The setup script includes:

- **Unit Types**: Volume (cup, tablespoon, etc.), Weight (gram, kilogram, etc.), Count (piece, head, etc.), and Special units
- **Ingredient Types**: Vegetables, Fruits, Grains, Plant Proteins, Nuts & Seeds, Spices, Herbs, Liquids, Pantry Items
- **Default Ingredients**: Common vegan ingredients with pre-configured conversion formulas:
  - Vegetables: Celery, Onion, Tomato, Carrot, Bell Pepper, Garlic, Potato, Sweet Potato, Broccoli, Cauliflower, Cabbage, Spinach, Lettuce
  - Fruits: Avocado, Lemon, Lime
  - Grains & Legumes: Rice, Lentils, Quinoa
  - Herbs: Parsley, Cilantro, Basil
  - Nuts & Seeds: Almonds, Cashews

All ingredients include conversion formulas for common unit conversions (e.g., cups to pieces, grams to pieces, etc.).

**Important**: Recipes are NOT included in the default setup. You'll need to add your own recipes through the web interface.

## Usage

### Adding Ingredients

1. Navigate to the "Ingredients" page
2. Click "Add Ingredient"
3. Fill in the ingredient details:
   - Name
   - Type (Vegetables, Fruits, etc.)
   - Shopping Unit (the unit you buy it in)
   - Conversion Rules (or use default conversions if available)
   - Size Estimation Rules (for count-based ingredients)

### Adding Recipes

1. Navigate to the "Recipes" page
2. Click "Add Recipe"
3. Fill in recipe details:
   - Name
   - Yield (quantity and unit)
   - Page number (optional, for cookbook reference)
   - Is Sub-Recipe (if this recipe can be used as an ingredient in other recipes)
4. Add ingredients or sub-recipes to the recipe
5. Save

### Generating Shopping Lists

1. Navigate to the "Shopping Lists" page
2. Search for recipes by name or ingredient
3. Select recipes and specify batch counts
4. Click "Generate Shopping List"
5. The list will be organized by category (Produce, Dry/Bulk, etc.)
6. Check off items you already have (they'll move to "Already Have" section)
7. Copy the formatted text to use anywhere you need it

## Progressive Web App (PWA)

The application can be installed on iPad/iPhone:

1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. The app will appear as an icon on your home screen

See `IPAD_SETUP.md` for detailed instructions.

## Project Structure

```
shoplist/
├── app.py                      # Flask application entry point
├── setup_database.py           # Database setup script (loads default ingredients)
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── backend/
│   ├── database.py            # Database initialization and connection
│   ├── services.py            # Business logic (conversion, aggregation)
│   ├── default_conversions.py # Default ingredient conversions
│   └── mac_messages.py        # macOS Messages.app integration
├── frontend/
│   ├── index.html             # Main page
│   ├── ingredients.html       # Ingredient management
│   ├── recipes.html           # Recipe management
│   ├── shopping.html          # Shopping list generator
│   ├── manifest.json          # PWA manifest
│   ├── service-worker.js      # PWA service worker
│   ├── css/
│   │   └── style.css          # Styles
│   └── js/
│       ├── api.js             # API client
│       ├── ingredients.js    # Ingredient management logic
│       ├── recipes.js         # Recipe management logic
│       └── shopping.js        # Shopping list logic
└── scripts/                   # Utility scripts (not required for basic usage)
```

## Database

The application uses SQLite for data storage. The database file (`database.db`) is created automatically on first run.

**Important**: The database file is excluded from git (see `.gitignore`). Each user will have their own database with their own recipes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license here]

## Troubleshooting

### Database Issues

If you encounter database errors:
1. Delete `database.db` (if it exists)
2. Run `python setup_database.py` to recreate the database
3. Restart the application

### Port Already in Use

If port 5000 is already in use, modify `app.py` to use a different port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## Support

For issues or questions, please open an issue on GitHub.
