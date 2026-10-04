# -*- coding: utf-8 -*-
"""
Sets all 2,500 new names to 'unrated' for both Rob and Ana so they can classify them.
Leaves the 1,172 PDF v1.0 names intact:
- 23 favorites
- 58 possible
- 1,091 excluded
For Ana, 23 favorites are preserved, rest unrated.
"""

import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('names_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print(f"Total names: {len(db)}")

pdf_count = 0
new_count = 0

for item in db:
    is_pdf = item.get('source') and 'PDF' in item.get('source')
    if is_pdf:
        pdf_count += 1
        # Keep original PDF classification for Rob
        # rob_status is already set from PDF
        if item.get('status') == 'favorites':
            item['rob_status'] = 'favorites'
            item['ana_status'] = 'favorites'
        elif item.get('status') == 'possible':
            item['rob_status'] = 'possible'
            if 'ana_status' not in item or item['ana_status'] != 'favorites':
                item['ana_status'] = 'unrated'
        elif item.get('status') == 'excluded':
            item['rob_status'] = 'excluded'
            if 'ana_status' not in item or item['ana_status'] != 'favorites':
                item['ana_status'] = 'unrated'
    else:
        new_count += 1
        # All new additions have NOT been classified by Rob and Ana yet!
        item['status'] = 'unrated'
        item['rob_status'] = 'unrated'
        item['ana_status'] = 'unrated'

print(f"PDF names preserved: {pdf_count}")
print(f"New names set to unrated for classification: {new_count}")

# Verification
rob_favs = sum(1 for x in db if x.get('rob_status') == 'favorites')
rob_poss = sum(1 for x in db if x.get('rob_status') == 'possible')
rob_excl = sum(1 for x in db if x.get('rob_status') == 'excluded')
rob_unrated = sum(1 for x in db if x.get('rob_status') == 'unrated')

ana_favs = sum(1 for x in db if x.get('ana_status') == 'favorites')
ana_unrated = sum(1 for x in db if x.get('ana_status') == 'unrated')

print(f"Rob stats -> Favs: {rob_favs}, Poss: {rob_poss}, Excl: {rob_excl}, Unrated: {rob_unrated}")
print(f"Ana stats -> Favs: {ana_favs}, Unrated: {ana_unrated}")

with open('names_db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

with open('names_db_backup.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("Saved updated database to names_db.json and names_db_backup.json.")
