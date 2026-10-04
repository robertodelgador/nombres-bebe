#!/usr/bin/env python3
"""
Bebe Names Studio - Local Backend Server
Handles static file serving and persistent JSON API for names_db.json.
Uses Python standard library (http.server) - zero external dependencies required.
"""

import http.server
import socketserver
import json
import os
import sys
import urllib.parse
import shutil
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'names_db.json')
BACKUP_FILE = os.path.join(BASE_DIR, 'names_db_backup.json')

# Ensure backup exists
if os.path.exists(DB_FILE) and not os.path.exists(BACKUP_FILE):
    shutil.copyfile(DB_FILE, BACKUP_FILE)


def load_db():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading DB: {e}", file=sys.stderr)
        return []


def save_db(data):
    # Atomically write to temp file then replace
    temp_file = DB_FILE + '.tmp'
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp_file, DB_FILE)


class BebeRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_json(self, status_code, data):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/names':
            db = load_db()
            self.send_json(200, {'success': True, 'count': len(db), 'data': db})
            return

        if path == '/api/stats':
            db = load_db()
            favs = sum(1 for x in db if x.get('status') == 'favorites')
            poss = sum(1 for x in db if x.get('status') == 'possible')
            excl = sum(1 for x in db if x.get('status') == 'excluded')
            pdf_count = sum(1 for x in db if 'PDF' in x.get('source', ''))
            new_count = sum(1 for x in db if '500' in x.get('source', '') or x.get('is_new'))
            user_count = sum(1 for x in db if x.get('source') == 'User Added')
            self.send_json(200, {
                'success': True,
                'total': len(db),
                'favorites': favs,
                'possible': poss,
                'excluded': excl,
                'pdf_count': pdf_count,
                'new_count': new_count,
                'user_count': user_count
            })
            return

        # Serve static files (index.html, etc.)
        if path == '/':
            self.path = '/index.html'
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body)
        except Exception as e:
            self.send_json(400, {'success': False, 'error': f'Invalid JSON payload: {e}'})
            return

        if path == '/api/names':
            name_val = data.get('name', '').strip()
            if not name_val:
                self.send_json(400, {'success': False, 'error': 'Name is required'})
                return

            db = load_db()
            new_id = f"custom-{int(datetime.now().timestamp() * 1000)}"
            new_item = {
                'id': new_id,
                'name': name_val,
                'origin': data.get('origin', 'Spanish/Latin').strip(),
                'meaning': data.get('meaning', '').strip(),
                'letter': name_val[0].upper() if name_val else 'A',
                'status': data.get('status', 'possible'),
                'notes': data.get('notes', '').strip(),
                'source': 'User Added',
                'gender': data.get('gender', 'Female'),
                'created_at': datetime.now().isoformat()
            }
            db.append(new_item)
            save_db(db)
            self.send_json(201, {'success': True, 'data': new_item})
            return

        if path == '/api/batch':
            # Batch update e.g. [{"id": "...", "status": "favorites"}, ...]
            updates = data.get('updates', [])
            if not isinstance(updates, list):
                self.send_json(400, {'success': False, 'error': 'Expected "updates" array'})
                return

            db = load_db()
            update_map = {item['id']: item for item in updates if 'id' in item}
            modified = 0
            for item in db:
                if item['id'] in update_map:
                    u = update_map[item['id']]
                    for key in ['status', 'notes', 'origin', 'meaning']:
                        if key in u:
                            item[key] = u[key]
                    modified += 1

            save_db(db)
            self.send_json(200, {'success': True, 'modified': modified})
            return

        if path == '/api/reset':
            if os.path.exists(BACKUP_FILE):
                shutil.copyfile(BACKUP_FILE, DB_FILE)
                db = load_db()
                self.send_json(200, {'success': True, 'message': 'Database restored from original backup', 'count': len(db)})
            else:
                self.send_json(404, {'success': False, 'error': 'Backup file not found'})
            return

        self.send_json(404, {'success': False, 'error': 'Endpoint not found'})

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith('/api/names/'):
            item_id = path.split('/')[-1]
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
                patch = json.loads(body)
            except Exception as e:
                self.send_json(400, {'success': False, 'error': f'Invalid JSON payload: {e}'})
                return

            db = load_db()
            found = False
            updated_item = None
            for item in db:
                if item['id'] == item_id:
                    for key in ['status', 'notes', 'origin', 'meaning', 'name']:
                        if key in patch:
                            item[key] = patch[key]
                    found = True
                    updated_item = item
                    break

            if found:
                save_db(db)
                self.send_json(200, {'success': True, 'data': updated_item})
            else:
                self.send_json(404, {'success': False, 'error': f'Item {item_id} not found'})
            return

        self.send_json(404, {'success': False, 'error': 'Endpoint not found'})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith('/api/names/'):
            item_id = path.split('/')[-1]
            db = load_db()
            new_db = [x for x in db if x['id'] != item_id]
            if len(new_db) < len(db):
                save_db(new_db)
                self.send_json(200, {'success': True, 'deleted': item_id})
            else:
                self.send_json(404, {'success': False, 'error': f'Item {item_id} not found'})
            return

        self.send_json(404, {'success': False, 'error': 'Endpoint not found'})


def run(port=PORT):
    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), BebeRequestHandler) as httpd:
        print("======================================================")
        print(f"  * Bebe Names Studio Server running on port {port}")
        print(f"  * Open your browser at: http://localhost:{port}")
        print(f"  * Database: {DB_FILE}")
        print("  Press Ctrl+C to stop.")
        print("======================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully...")
            httpd.shutdown()


if __name__ == '__main__':
    p = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else PORT
    run(p)
