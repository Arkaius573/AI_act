import os
import re
import chromadb
from chromadb.utils import embedding_functions

# --- CONFIGURAZIONE ---
INPUT_FILE = "AI_ACT_2024.txt"
DB_PATH = "./compliance_db"
COLLECTION_NAME = "eu_ai_act_rules"
# Modello ottimizzato per l'italiano e leggero per l'uso locale
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

def clean_text_structure(text):
    """
    Rimuove l'indice e i preamboli, isolando la parte normativa.
    """
    print("🧹 Fase 1: Pulizia del testo e rimozione preamboli...")
    
    # Il testo normativo vero e proprio inizia solitamente dopo questa frase
    start_marker = "HANNO ADOTTATO IL PRESENTE REGOLAMENTO"
    
    if start_marker in text:
        parts = text.split(start_marker)
        return parts[-1]
    
    # Fallback se la frase non viene trovata esattamente
    print("⚠️ Marker standard non trovato. Cerco l'inizio dell'Articolo 1...")
    match = re.search(r"Articolo\s+1", text, re.IGNORECASE)
    if match:
        return text[match.start():]
    
    return text

def split_text_smart(full_text):
    """
    Divide il testo in blocchi basati su Articoli e Allegati.
    """
    print("✂️  Fase 2: Divisione in Articoli e Allegati...")
    
    # Regex per identificare i titoli delle sezioni
    pattern = r"(Articolo\s+\d+|ALLEGATO\s+[IVX]+|ALLEGATO\s+[A-Z]+)"
    
    # Split mantenendo i titoli
    parts = re.split(pattern, full_text, flags=re.IGNORECASE)
    
    chunks = []
    current_header = ""
    
    for part in parts:
        # Se la parte è un titolo (es. Articolo 5)
        if re.match(pattern, part, re.IGNORECASE):
            current_header = part.strip().upper()
        else:
            if current_header:
                content = part.strip()
                # Teniamo solo blocchi con contenuto reale (minimo 50 caratteri)
                if len(content) > 50:
                    # Rimuove spazi e a capo multipli per pulizia vettoriale
                    content = " ".join(content.split())
                    chunks.append(f"{current_header}: {content}")
                current_header = "" 
                
    return chunks

def main():
    # 1. Verifica file input
    if not os.path.exists(INPUT_FILE):
        print(f"❌ ERRORE: Il file {INPUT_FILE} non è stato trovato nella cartella corrente.")
        return

    # 2. Lettura e processamento
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    cleaned_text = clean_text_structure(raw_text)
    chunks = split_text_smart(cleaned_text)
    
    if not chunks:
        print("❌ ERRORE: Non è stato possibile estrarre articoli o allegati dal testo.")
        return

    print(f"✅ Trovati {len(chunks)} blocchi normativi pronti per il database.")

    # 3. Inizializzazione ChromaDB
    print("💾 Inizializzazione Database Vettoriale (ChromaDB)...")
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    
    # Persistiamo i dati in una cartella locale
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Elimina la collezione se esiste già per evitare duplicati
    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass
        
    collection = client.create_collection(
        name=COLLECTION_NAME, 
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"} # Usiamo la similarità coseno
    )

    # 4. Caricamento Dati
    print(f"🚀 Caricamento di {len(chunks)} documenti in corso...")
    
    ids = [f"id_{i}" for i in range(len(chunks))]
    
    # Carichiamo in blocchi da 50 per gestire meglio la memoria
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        end = i + batch_size
        collection.add(
            ids=ids[i:end],
            documents=chunks[i:end]
        )
        print(f"   ...caricati {min(end, len(chunks))}/{len(chunks)}")

    print(f"\n🎉 CONFIGURAZIONE COMPLETATA!")
    print(f"   Database creato con successo nella cartella: {DB_PATH}")

if __name__ == "__main__":
    main()