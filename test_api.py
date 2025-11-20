#!/usr/bin/env python3
"""Quick API test"""
from app import app

with app.test_client() as client:
    r = client.get('/api/ingredient-types')
    print(f'✓ API test: GET /api/ingredient-types returned status {r.status_code}')
    data = r.get_json()
    print(f'✓ Response has {len(data)} ingredient types')
    
    r2 = client.get('/api/unit-types')
    print(f'✓ API test: GET /api/unit-types returned status {r2.status_code}')
    data2 = r2.get_json()
    print(f'✓ Response has {len(data2)} unit types')

