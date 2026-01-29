# test_db.py
"""Test completo del database vettoriale"""

import os
import sys

print("=" * 70)
print("🧪 TEST DATABASE CHROMADB")
print("=" * 70)

# --- TEST 1: FILE FISICI ---
print("\n[TEST 1] Verifica file fisici...")

db_path = "./compliance_db"

if not os.path.exists(db_path):
    print(f"❌ FALLITO: Cartella {db_path} non esiste!")
    print(f"💡 Soluzione: Esegui 'python setup_db.py'")
    sys.exit(1)

files = os.listdir(db_path)
db_files = [f for f in files if 'chroma' in f or '.bin' in f]

if not db_files:
    print(f"❌ FALLITO: Nessun file DB trovato in {db_path}")
    print(f"💡 Soluzione: Esegui 'python setup_db.py'")
    sys.exit(1)

print(f"✅ PASSATO: Trovati {len(db_files)} file DB")
for f in db_files:
    size = os.path.getsize(os.path.join(db_path, f))
    print(f"   - {f} ({size/1024:.1f} KB)")

# --- TEST 2: IMPORT MODULO ---
print("\n[TEST 2] Import modulo ComplianceEngine...")

try:
    from compliance_db.backend import ComplianceEngine
    print("✅ PASSATO: Import riuscito")
except ImportError as e:
    print(f"❌ FALLITO: {e}")
    print("💡 Soluzioni:")
    print("   1. Verifica che compliance_db/__init__.py esista")
    print("   2. Sei nella cartella giusta? (pwd)")
    sys.exit(1)

# --- TEST 3: INIZIALIZZAZIONE ---
print("\n[TEST 3] Inizializzazione database...")

try:
    engine = ComplianceEngine(debug=True)
    # ↑ debug=True stampa info dettagliate
    
    if not engine.collection:
        print("❌ FALLITO: Collection è None")
        sys.exit(1)
    
    count = engine.collection.count()
    print(f"✅ PASSATO: Database caricato con {count} documenti")
    
    if count == 0:
        print("⚠️ ATTENZIONE: Database vuoto!")
        print("💡 Ri-esegui: python setup_db.py")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ FALLITO: {type(e).__name__}: {e}")
    sys.exit(1)

# --- TEST 4: QUERY SEMPLICE ---
print("\n[TEST 4] Query di ricerca...")

test_queries = [
    ("riconoscimento facciale", 1.0),
    ("sistemi ad alto rischio", 1.0),
    ("GDPR privacy", 1.5)
]

for query, threshold in test_queries:
    print(f"\n   Query: '{query}' (threshold={threshold})")
    
    try:
        results = engine.search_relevant_rules(query, n_results=3, threshold=threshold)
        
        if "Errore" in results or "Nessun" in results:
            print(f"   ⚠️ {results}")
        else:
            print(f"   ✅ Trovati {len(results)} caratteri")
            print(f"   Anteprima: {results[:150]}...")
            
    except Exception as e:
        print(f"   ❌ Errore: {e}")

# --- TEST 5: TEST CONNESSIONE ---
print("\n[TEST 5] Test metodo test_connection()...")

success, msg = engine.test_connection()
if success:
    print(f"✅ PASSATO: {msg}")
else:
    print(f"❌ FALLITO: {msg}")
    sys.exit(1)

# --- RIEPILOGO ---
print("\n" + "=" * 70)
print("🎉 TUTTI I TEST SUPERATI!")
print("=" * 70)
print("\n💡 Prossimi passi:")
print("   1. Testa Ollama: python test_ollama.py")
print("   2. Test completo: python test_full_system.py")
print("   3. Lancia app: reflex run")