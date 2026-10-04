import subprocess
import json
import sys
from datetime import datetime

def run_git(args):
    result = subprocess.run(['git'] + args, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"Error executing git {' '.join(args)}: {result.stderr}")
        return False, result.stderr
    return True, result.stdout

def sync():
    print("🔄 Sincronizando votos con GitHub...")
    
    # 1. Pull latest from remote
    print("⬇️ Obteniendo cambios remotos...")
    ok, out = run_git(['pull', '--rebase', 'origin', 'main'])
    if not ok:
        print("⚠️ Advertencia al hacer git pull:", out)
        
    # 2. Touch/update timestamp in votes.json if needed
    try:
        with open('votes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['last_updated'] = datetime.utcnow().isoformat() + 'Z'
        with open('votes.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error actualizando votes.json:", e)

    # 3. Add and commit
    run_git(['add', 'votes.json'])
    ok, status = run_git(['status', '--porcelain'])
    if 'votes.json' in status:
        ok, out = run_git(['commit', '-m', f"Sync votes: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
        if not ok:
            print("No se pudo hacer commit:", out)
            return
        print("⬆️ Subiendo a GitHub...")
        ok, out = run_git(['push', 'origin', 'main'])
        if ok:
            print("✅ ¡Votos sincronizados exitosamente con GitHub!")
        else:
            print("❌ Error al subir a GitHub:", out)
    else:
        print("ℹ️ No hay cambios pendientes en votes.json.")

if __name__ == '__main__':
    sync()
