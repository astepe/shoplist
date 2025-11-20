/**
 * Shopping List Generator Page Logic
 */

let recipes = [];
let selectedRecipes = [];
let filteredRecipesForDropdown = [];
let recipesWithIngredients = null; // Cache for recipes with ingredient data

// Initialize page
async function initShoppingPage() {
    try {
        // Load recipes
        recipes = await getRecipes();
        
        // Setup search dropdown
        setupRecipeDropdown();
        
        // Display selected recipes
        displaySelectedRecipes();
        
        // Setup handlers
        setupHandlers();

        // Load snapshots history
        loadSnapshots();
        
    } catch (error) {
        showError('Failed to load recipes: ' + error.message);
    }
}

function setupRecipeDropdown() {
    const searchInput = document.getElementById('recipe-search');
    const dropdown = document.getElementById('recipe-dropdown');
    
    if (!searchInput || !dropdown) {
        console.error('setupRecipeDropdown: searchInput or dropdown not found!');
        return;
    }
    
    // Show dropdown on focus
    searchInput.addEventListener('focus', function() {
        filterAndShowDropdown();
    });
    
    // Filter dropdown as user types
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Show dropdown immediately (will be populated async)
        const dropdown = document.getElementById('recipe-dropdown');
        
        if (dropdown) {
            if (query) {
                dropdown.style.display = 'block';
                dropdown.style.visibility = 'visible';
                dropdown.style.opacity = '1';
                dropdown.innerHTML = '<div style="padding: 12px; color: #666;">Searching...</div>';
            } else {
                dropdown.style.display = 'none';
            }
        }
        
        // Don't await - let it run async
        filterAndShowDropdown().catch(error => {
            console.error('Error in filterAndShowDropdown:', error);
            if (dropdown) {
                dropdown.innerHTML = '<div style="padding: 12px; color: red;">Error searching recipes</div>';
            }
        });
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        // Check if click is outside both search input and dropdown
        const isClickInside = searchInput.contains(e.target) || dropdown.contains(e.target);
        if (!isClickInside) {
            dropdown.style.display = 'none';
        }
    });
}

async function filterAndShowDropdown() {
    const searchInput = document.getElementById('recipe-search');
    const dropdown = document.getElementById('recipe-dropdown');
    
    if (!searchInput || !dropdown) {
        console.error('filterAndShowDropdown: searchInput or dropdown not found');
        return;
    }
    
    const query = searchInput.value.trim();
    
    // If empty query, show all unselected recipes
    if (query === '') {
        filteredRecipesForDropdown = recipes.filter(r => !selectedRecipes.find(sr => sr.recipe_id === r.id));
        displayDropdownItems();
        return;
    }
    
    const queryLower = query.toLowerCase();
    
    // Search by recipe name (fast, local)
    let nameMatches = recipes.filter(recipe => 
        recipe.name.toLowerCase().includes(queryLower) &&
        !selectedRecipes.find(sr => sr.recipe_id === recipe.id)
    );
    
    // Always search by ingredients via API (in addition to name search)
    let ingredientMatches = [];
    try {
        const params = new URLSearchParams();
        params.append('ingredients', query);
        const url = `/api/recipes?${params.toString()}`;
        
        const apiResults = await apiRequest(url);
        
        if (apiResults && Array.isArray(apiResults)) {
            // Filter out already selected recipes
            ingredientMatches = apiResults.filter(recipe => 
                !selectedRecipes.find(sr => sr.recipe_id === recipe.id)
            );
        }
    } catch (error) {
        console.error('Error searching by ingredients:', error);
        // Continue with just name matches if ingredient search fails
    }
    
    // Combine results, removing duplicates (by recipe ID)
    const combinedMatches = new Map();
    
    // Add name matches first
    nameMatches.forEach(recipe => {
        combinedMatches.set(recipe.id, recipe);
    });
    
    // Add ingredient matches (won't duplicate if already in name matches)
    ingredientMatches.forEach(recipe => {
        if (!combinedMatches.has(recipe.id)) {
            combinedMatches.set(recipe.id, recipe);
        }
    });
    
    // Convert map to array
    filteredRecipesForDropdown = Array.from(combinedMatches.values());
    
    displayDropdownItems();
}

function displayDropdownItems() {
    const searchInput = document.getElementById('recipe-search');
    const dropdown = document.getElementById('recipe-dropdown');
    
    if (!searchInput || !dropdown) {
        console.error('displayDropdownItems: searchInput or dropdown not found');
        return;
    }
    
    // Display dropdown
    if (filteredRecipesForDropdown.length === 0) {
        dropdown.style.display = 'block';
        dropdown.innerHTML = '<div style="padding: 12px; color: #666; font-style: italic;">No recipes found</div>';
        return;
    }
    
    dropdown.innerHTML = '';
    dropdown.style.display = 'block';
    dropdown.style.visibility = 'visible';
    dropdown.style.opacity = '1';
    
    filteredRecipesForDropdown.forEach(recipe => {
        const item = document.createElement('div');
        item.className = 'recipe-dropdown-item';
        item.textContent = recipe.name;
        item.onclick = function() {
            addRecipe(recipe);
            searchInput.value = '';
            dropdown.style.display = 'none';
        };
        dropdown.appendChild(item);
    });
}

function addRecipe(recipe) {
    // Check if already added
    if (selectedRecipes.find(r => r.recipe_id === recipe.id)) {
        return;
    }
    
    // Add to selected recipes
    selectedRecipes.push({
        recipe_id: recipe.id,
        recipe_name: recipe.name,
        is_sub_recipe: recipe.is_sub_recipe,
        yield_quantity: recipe.yield_quantity,
        yield_unit_name: recipe.yield_unit_name,
        batches: 1
    });
    
    displaySelectedRecipes();
}

function removeRecipe(recipeId) {
    selectedRecipes = selectedRecipes.filter(r => r.recipe_id !== recipeId);
    displaySelectedRecipes();
    // Refresh dropdown to show removed recipe
    filterAndShowDropdown();
}

function updateBatches(recipeId, batches) {
    const selection = selectedRecipes.find(r => r.recipe_id === recipeId);
    if (selection) {
        const batchesNum = parseInt(batches) || 1;
        if (batchesNum < 1) {
            selection.batches = 1;
        } else {
            selection.batches = batchesNum;
        }
    }
}

async function loadSnapshots() {
    const container = document.getElementById('snapshots-container');
    if (!container) return;
    try {
        const snapshots = await getShoppingListSnapshots();
        if (!snapshots || snapshots.length === 0) {
            container.innerHTML = '<p style="color: #666;">No snapshots yet.</p>';
            return;
        }
        const list = document.createElement('ul');
        list.style.listStyle = 'none';
        list.style.padding = '0';
        snapshots.forEach(s => {
            const li = document.createElement('li');
            li.style.display = 'flex';
            li.style.justifyContent = 'space-between';
            li.style.alignItems = 'center';
            li.style.padding = '8px 0';
            const left = document.createElement('span');
            const date = new Date(s.created_at).toLocaleString();
            left.textContent = `#${s.id} • ${date}`;
            const btn = document.createElement('button');
            btn.className = 'btn-primary';
            btn.textContent = 'View';
            btn.onclick = () => viewSnapshot(s.id);
            li.appendChild(left);
            li.appendChild(btn);
            list.appendChild(li);
        });
        container.innerHTML = '';
        container.appendChild(list);
    } catch (e) {
        container.innerHTML = '<p style="color: red;">Failed to load history.</p>';
    }
}

async function viewSnapshot(id) {
    try {
        const snap = await getShoppingListSnapshot(id);
        
        // Populate selected recipes from snapshot
        if (snap.recipe_selections && Array.isArray(snap.recipe_selections)) {
            selectedRecipes = [];
            
            // Match recipe selections with full recipe data
            for (const selection of snap.recipe_selections) {
                const recipe = recipes.find(r => r.id === selection.recipe_id);
                if (recipe) {
                    selectedRecipes.push({
                        recipe_id: recipe.id,
                        recipe_name: recipe.name,
                        is_sub_recipe: recipe.is_sub_recipe,
                        yield_quantity: recipe.yield_quantity,
                        yield_unit_name: recipe.yield_unit_name,
                        batches: selection.batches || 1
                    });
                }
            }
            
            // Display the selected recipes in the UI
            displaySelectedRecipes();
        }
        
        // Replace current list with snapshot data for review
        currentShoppingList = snap.shopping_list;
        displayShoppingList(snap.shopping_list);
        
        // Update formatted text for the loaded snapshot
        await updateFormattedText();
        
        
        showSuccess(`Loaded snapshot #${id}`);
    } catch (e) {
        showError('Failed to load snapshot: ' + e.message);
    }
}

function displaySelectedRecipes() {
    const container = document.getElementById('selected-recipes-list');
    if (!container) return;
    
    if (selectedRecipes.length === 0) {
        container.innerHTML = '<p style="color: #666; font-style: italic;">No recipes selected yet. Search above to add recipes.</p>';
        return;
    }
    
    container.innerHTML = '';
    
    selectedRecipes.forEach(selection => {
        const recipe = recipes.find(r => r.id === selection.recipe_id);
        if (!recipe) return;
        
        const recipeDiv = document.createElement('div');
        recipeDiv.className = 'selected-recipe-item';
        recipeDiv.id = `selected-recipe-${selection.recipe_id}`;
        
        const subRecipeBadge = selection.is_sub_recipe 
            ? '<span class="badge">Sub-Recipe</span>' 
            : '';
        
        recipeDiv.innerHTML = `
            <div class="selected-recipe-header">
                <div class="selected-recipe-name">
                    <strong>${selection.recipe_name}</strong>${subRecipeBadge}
                    <span class="recipe-yield">(${selection.yield_quantity} ${selection.yield_unit_name})</span>
                </div>
                <button class="btn-remove" onclick="removeRecipe(${selection.recipe_id})" title="Remove recipe">×</button>
            </div>
            <div class="selected-recipe-batches">
                <label for="batches-${selection.recipe_id}">Batches:</label>
                <input type="number" min="1" value="${selection.batches}" id="batches-${selection.recipe_id}" 
                       onchange="updateBatches(${selection.recipe_id}, this.value)">
            </div>
        `;
        
        container.appendChild(recipeDiv);
    });
}

let currentShoppingList = null; // Store current shopping list
let checkedItems = new Set(); // Track which items are checked (using item IDs)

function setupHandlers() {
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateShoppingList);
    }
    
    const clearBtn = document.getElementById('clear-list-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearShoppingList);
    }
    
    // Copy text button handler
    const copyTextBtn = document.getElementById('copy-text-btn');
    if (copyTextBtn) {
        copyTextBtn.addEventListener('click', copyFormattedText);
    }
    
}

async function generateShoppingList() {
    // Prevent duplicate submissions
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn && generateBtn.disabled) return;
    if (generateBtn) generateBtn.disabled = true;
    if (selectedRecipes.length === 0) {
        showError('Please select at least one recipe.');
        return;
    }
    
    try {
        showLoading('Generating shopping list...');
        
        // Prepare recipe selections for API
        const recipeSelections = selectedRecipes.map(r => ({
            recipe_id: r.recipe_id,
            batches: r.batches || 1
        }));
        
        // Call API to generate shopping list
        const shoppingList = await generateShoppingListAPI(recipeSelections);
        
        if (!shoppingList || !Array.isArray(shoppingList)) {
            throw new Error('Invalid response from server');
        }
        
        // Store shopping list
        currentShoppingList = shoppingList;
        
        displayShoppingList(shoppingList);
        
        // Fetch and display formatted text
        await updateFormattedText();
        
        showSuccess('Shopping list generated successfully!');
        
        
    } catch (error) {
        showError('Failed to generate shopping list: ' + error.message);
        currentShoppingList = null;
    } finally {
        hideLoading();
        if (generateBtn) generateBtn.disabled = false;
    }
}

function getItemId(item) {
    // Generate a unique ID for each item
    if (item.is_sub_recipe) {
        return `subrecipe-${item.sub_recipe_id}-${item.quantity}-${item.unit_id}`;
    } else {
        return `ingredient-${item.ingredient_id}-${item.quantity}-${item.unit_id}-${item.size_qualifier || ''}`;
    }
}

function toggleItemChecked(itemId) {
    if (checkedItems.has(itemId)) {
        checkedItems.delete(itemId);
    } else {
        checkedItems.add(itemId);
    }
    // Update the visual state
    const checkbox = document.querySelector(`input[data-item-id="${itemId}"]`);
    if (checkbox) {
        checkbox.checked = checkedItems.has(itemId);
    }
    // Update the list item styling
    const listItem = checkbox?.closest('.shopping-list-item');
    if (listItem) {
        if (checkedItems.has(itemId)) {
            listItem.classList.add('checked-item');
        } else {
            listItem.classList.remove('checked-item');
        }
    }
    
    // Update formatted text when items are checked/unchecked
    updateFormattedText();
}

function displayShoppingList(shoppingList) {
    const container = document.getElementById('shopping-list');
    if (!container) return;
    
    // Validate input
    if (!shoppingList) {
        container.innerHTML = '<p style="color: red;">Error: No shopping list data received.</p>';
        return;
    }
    
    if (!Array.isArray(shoppingList)) {
        container.innerHTML = '<p style="color: red;">Error: Invalid shopping list format.</p>';
        return;
    }
    
    if (shoppingList.length === 0) {
        container.innerHTML = '<p>No ingredients needed for selected recipes.</p>';
        return;
    }
    
    // Reset checked items when generating new list (or preserve if viewing snapshot)
    // For now, clear checked items on new generation
    if (currentShoppingList !== shoppingList) {
        checkedItems.clear();
    }
    
    // Create the list without duplicate heading (heading already exists in HTML)
    container.innerHTML = '<ul class="shopping-list-items"></ul>';
    const list = container.querySelector('.shopping-list-items');
    
    shoppingList.forEach(item => {
        const li = document.createElement('li');
        li.className = 'shopping-list-item';
        
        const itemId = getItemId(item);
        const isChecked = checkedItems.has(itemId);
        if (isChecked) {
            li.classList.add('checked-item');
        }
        
        // Create checkbox
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'item-checkbox';
        checkbox.checked = isChecked;
        checkbox.setAttribute('data-item-id', itemId);
        checkbox.addEventListener('change', () => toggleItemChecked(itemId));
        
        // Create label wrapper for checkbox and text
        const label = document.createElement('label');
        label.className = 'shopping-item-label';
        label.appendChild(checkbox);
        
        // Check if this is a sub-recipe
        if (item.is_sub_recipe) {
            // Handle sub-recipe display
            const quantity = item.quantity || 0;
            const subRecipeName = item.sub_recipe_name || 'Unknown Recipe';
            const yieldQuantity = item.yield_quantity || 0;
            const yieldUnitName = item.yield_unit_name || '';
            
            // For sub-recipes, display the amount in the unit requested by the recipe
            // Keep the yield info in parentheses for context
            const displayUnitName = item.unit_name || '';
            
            // Build sub-recipe text
            let itemText = `${quantity} ${displayUnitName} ${subRecipeName}`;
            
            // Add yield info if available
            if (yieldQuantity && yieldUnitName) {
                itemText += ` (yields ${yieldQuantity} ${yieldUnitName})`;
            }
            
            // Add sub-recipe badge
            const subRecipeBadge = document.createElement('span');
            subRecipeBadge.className = 'badge';
            subRecipeBadge.textContent = 'Sub-Recipe';
            
            const textSpan = document.createElement('span');
            textSpan.innerHTML = subRecipeBadge.outerHTML + ' ' + itemText;
            label.appendChild(textSpan);
            li.appendChild(label);
        } else {
            // Handle regular ingredient display
            const quantity = item.quantity || 0;
            const unitName = item.unit_name || '';
            const ingredientName = item.ingredient_name || 'Unknown';
            const sizeQualifier = item.size_qualifier;
            
            // Check if this is a container/package unit (bottle, package, can, jar, etc.)
            const containerUnits = ['package', 'can', 'bottle', 'jar', 'container'];
            const isContainerUnit = containerUnits.includes(unitName.toLowerCase());
            
            // For packaged/container ingredients with recipe_volume or recipe_weight,
            // show only the needed amount, not the package count
            // Check if recipe_volume/recipe_weight exist and are not null/undefined
            const hasRecipeVolume = item.recipe_volume !== null && item.recipe_volume !== undefined && item.recipe_volume > 0;
            const hasRecipeWeight = item.recipe_weight !== null && item.recipe_weight !== undefined && item.recipe_weight > 0;
            
            if (isContainerUnit && (hasRecipeVolume || hasRecipeWeight)) {
                const details = [];
                
                if (hasRecipeVolume) {
                    const vol = parseFloat(item.recipe_volume);
                    // For fluid ounces: if less than 1 oz, show 2 decimals; otherwise show 1 decimal
                    const volFormatted = vol < 1 ? vol.toFixed(2) : vol.toFixed(1);
                    details.push(`${volFormatted} ${item.recipe_volume_unit || 'fl oz'}`);
                }
                
                if (hasRecipeWeight) {
                    const wt = parseFloat(item.recipe_weight);
                    // For weights less than 1g, show 2 decimal places; otherwise show 1 decimal place
                    const wtFormatted = wt < 1 ? wt.toFixed(2) : wt.toFixed(1);
                    details.push(`${wtFormatted} ${item.recipe_weight_unit || 'g'}`);
                }
                
                if (details.length > 0) {
                    // Show only the need amount for container ingredients
                    let itemText = `${ingredientName} (need: ${details.join(', ')})`;
                    const textSpan = document.createElement('span');
                    textSpan.textContent = itemText;
                    label.appendChild(textSpan);
                } else {
                    // Fallback if no details available
                    const textSpan = document.createElement('span');
                    textSpan.textContent = `${quantity} ${unitName} ${ingredientName}`;
                    label.appendChild(textSpan);
                }
            } else {
                // For non-container ingredients, show quantity and unit as normal
                let itemText = `${quantity} ${unitName} ${ingredientName}`;
                if (sizeQualifier) {
                    itemText = `${quantity} ${sizeQualifier} ${unitName} ${ingredientName}`;
                }
                
                // For non-container ingredients, still show need amount if available
                if (item.recipe_volume || item.recipe_weight) {
                    const details = [];
                    
                    if (item.recipe_volume) {
                        const vol = parseFloat(item.recipe_volume);
                        const volFormatted = vol < 1 ? vol.toFixed(2) : vol.toFixed(1);
                        details.push(`${volFormatted} ${item.recipe_volume_unit || 'fl oz'}`);
                    }
                    
                    if (item.recipe_weight) {
                        const wt = parseFloat(item.recipe_weight);
                        const wtFormatted = wt < 1 ? wt.toFixed(2) : wt.toFixed(1);
                        details.push(`${wtFormatted} ${item.recipe_weight_unit || 'g'}`);
                    }
                    
                    if (details.length > 0) {
                        itemText += ` (need: ${details.join(', ')})`;
                    }
                }
                
                const textSpan = document.createElement('span');
                textSpan.textContent = itemText;
                label.appendChild(textSpan);
            }
        }
        
        li.appendChild(label);
        list.appendChild(li);
    });
}

function clearShoppingList() {
    const container = document.getElementById('shopping-list');
    if (!container) return;
    currentShoppingList = null;
    checkedItems.clear();
    container.innerHTML = '<p>Select recipes and click "Generate Shopping List" to create your list.</p>';
    
    // Clear formatted text
    const textarea = document.getElementById('formatted-text');
    const copyBtn = document.getElementById('copy-text-btn');
    if (textarea) {
        textarea.value = '';
    }
    if (copyBtn) {
        copyBtn.disabled = true;
    }
    
}

function showLoading(message) {
    const alert = document.getElementById('alert');
    if (alert) {
        alert.className = 'alert alert-info';
        alert.textContent = message;
        alert.style.display = 'block';
    }
}

function hideLoading() {
    // Loading will be replaced by success/error message
}

function showError(message) {
    const alert = document.getElementById('alert');
    if (alert) {
        alert.className = 'alert alert-error';
        alert.textContent = message;
        alert.style.display = 'block';
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}

function showSuccess(message) {
    const alert = document.getElementById('alert');
    if (alert) {
        alert.className = 'alert alert-success';
        alert.textContent = message;
        alert.style.display = 'block';
        setTimeout(() => {
            alert.style.display = 'none';
        }, 3000);
    }
}

async function updateFormattedText() {
    if (!currentShoppingList || selectedRecipes.length === 0) {
        const textarea = document.getElementById('formatted-text');
        const copyBtn = document.getElementById('copy-text-btn');
        if (textarea) {
            textarea.value = '';
        }
        if (copyBtn) {
            copyBtn.disabled = true;
        }
        return;
    }
    
    try {
        // Prepare recipe selections
        const recipeSelections = selectedRecipes.map(r => ({
            recipe_id: r.recipe_id,
            batches: r.batches || 1
        }));
        
        // Get checked item IDs
        const checkedItemIds = Array.from(checkedItems);
        
        // Fetch formatted text
        const response = await getFormattedShoppingListText(recipeSelections, checkedItemIds);
        
        const textarea = document.getElementById('formatted-text');
        const copyBtn = document.getElementById('copy-text-btn');
        
        if (textarea && response.formatted_text) {
            textarea.value = response.formatted_text;
        }
        
        if (copyBtn) {
            copyBtn.disabled = !response.formatted_text;
        }
    } catch (error) {
        console.error('Failed to update formatted text:', error);
        const textarea = document.getElementById('formatted-text');
        if (textarea) {
            textarea.value = 'Error generating formatted text.';
        }
    }
}

async function copyFormattedText() {
    const textarea = document.getElementById('formatted-text');
    if (!textarea || !textarea.value) {
        return;
    }
    
    try {
        // Use modern Clipboard API if available
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(textarea.value);
        } else {
            // Fallback to execCommand for older browsers
            textarea.select();
            textarea.setSelectionRange(0, 99999); // For mobile devices
            document.execCommand('copy');
        }
        
        // Show feedback
        const copyBtn = document.getElementById('copy-text-btn');
        if (copyBtn) {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            copyBtn.disabled = false;
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        }
        showSuccess('Shopping list copied to clipboard!');
    } catch (err) {
        console.error('Failed to copy text:', err);
        showError('Failed to copy text. Please select and copy manually.');
    }
}

// Make functions available globally
window.addRecipe = addRecipe;
window.removeRecipe = removeRecipe;
window.updateBatches = updateBatches;

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initShoppingPage);
} else {
    initShoppingPage();
}
