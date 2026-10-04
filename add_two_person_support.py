# -*- coding: utf-8 -*-
"""
Adds two-person preference support (Rob & Ana) to names_db.json and names_db_backup.json.
Initializes:
- rob_status: set to current status
- ana_status: set to 'favorites' for the 23 consensus favorites, and 'unrated' for others so Ana can evaluate them.
"""

import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('names_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print(f"Total names loaded: {len(db)}")

fav_count = 0
for item in db:
    current_st = item.get('status', 'possible')
    
    # Preserve existing rob_status if already set, else set from current status
    if 'rob_status' not in item:
        item['rob_status'] = current_st
    
    # Initialize ana_status
    if 'ana_status' not in item:
        if current_st == 'favorites':
            item['ana_status'] = 'favorites'  # Both agreed on the 23 top favorites
            fav_count += 1
        else:
            item['ana_status'] = 'unrated'

# Save back to names_db.json
with open('names_db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

# Also save backup
with open('names_db_backup.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"Successfully updated {len(db)} names.")
print(f"Rob favorites: {sum(1 for x in db if x['rob_status'] == 'favorites')}")
print(f"Ana favorites: {sum(1 for x in db if x['ana_status'] == 'favorites')}")
print(f"Ana unrated: {sum(1 for x in db if x['ana_status'] == 'unrated')}")
