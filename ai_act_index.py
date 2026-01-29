"""
AI Act 2024 - Indicizzatore BM25
Crea un indice leggero per ricerca keyword nel documento normativo.
"""

import re
import json
import os
from rank_bm25 import BM25Okapi
import pickle

# Configurazione
INPUT_FILE = "AI_ACT_2024.txt"
INDEX_FILE = "ai_act_index.pkl"

def tokenize_italian(text: str) -> list[str]:
    """Tokenizzazione semplice per italiano."""
    text = text.lower()
    # Rimuovi punteggiatura e dividi in parole
    words = re.findall(r'\b[a-zA-Zàèéìòù]+\b', text)
    # Stopwords italiane minimali
    stopwords = {'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una', 'di', 'a',
                 'da', 'in', 'con', 'su', 'per', 'tra', 'fra', 'e', 'o', 'ma', 'che',
                 'se', 'come', 'quando', 'dove', 'perché', 'non', 'più', 'anche',
                 'essere', 'sono', 'è', 'del', 'della', 'dei', 'degli', 'delle',
                 'al', 'alla', 'ai', 'agli', 'alle', 'nel', 'nella', 'nei', 'negli',
                 'nelle', 'sul', 'sulla', 'sui', 'sugli', 'sulle', 'questo', 'questa',
                 'questi', 'queste', 'quello', 'quella', 'quelli', 'quelle', 'tale',
                 'tali', 'cui', 'quale', 'quali', 'quanto', 'quanta', 'quanti', 'quante'}
    return [w for w in words if w not in stopwords and len(w) > 2]


def extract_articles(text: str) -> list[dict]:
    """Estrae articoli e allegati dal documento AI Act."""

    # Trova dove inizia la parte normativa
    start_marker = "HANNO ADOTTATO IL PRESENTE REGOLAMENTO"
    if start_marker in text:
        text = text.split(start_marker)[-1]

    articles = []

    # Pattern per articoli
    article_pattern = r'(Articolo\s+(\d+))\s*(.*?)(?=Articolo\s+\d+|ALLEGATO\s+[IVX]+|$)'

    for match in re.finditer(article_pattern, text, re.IGNORECASE | re.DOTALL):
        article_num = match.group(2)
        content = match.group(3).strip()

        if len(content) > 100:  # Solo articoli con contenuto sostanziale
            # Pulisci il contenuto
            content = ' '.join(content.split())

            articles.append({
                'id': f'art_{article_num}',
                'type': 'articolo',
                'number': int(article_num),
                'title': f'Articolo {article_num}',
                'content': content[:5000],  # Limita lunghezza per performance
                'tokens': tokenize_italian(content[:5000])
            })

    # Pattern per allegati
    allegato_pattern = r'(ALLEGATO\s+([IVX]+))\s*(.*?)(?=ALLEGATO\s+[IVX]+|$)'

    for match in re.finditer(allegato_pattern, text, re.IGNORECASE | re.DOTALL):
        allegato_num = match.group(2)
        content = match.group(3).strip()

        if len(content) > 100:
            content = ' '.join(content.split())

            articles.append({
                'id': f'allegato_{allegato_num}',
                'type': 'allegato',
                'number': allegato_num,
                'title': f'Allegato {allegato_num}',
                'content': content[:5000],
                'tokens': tokenize_italian(content[:5000])
            })

    return articles


class AIActIndex:
    """Indice BM25 per ricerca nel AI Act."""

    def __init__(self):
        self.articles = []
        self.bm25 = None
        self.loaded = False

    def build(self, input_file: str = INPUT_FILE):
        """Costruisce l'indice dal file."""
        print(f"Lettura {input_file}...")

        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        print("Estrazione articoli...")
        self.articles = extract_articles(text)

        print(f"Trovati {len(self.articles)} articoli/allegati")

        # Costruisci indice BM25
        corpus = [art['tokens'] for art in self.articles]
        self.bm25 = BM25Okapi(corpus)
        self.loaded = True

        print("Indice BM25 costruito!")
        return len(self.articles)

    def save(self, path: str = INDEX_FILE):
        """Salva l'indice su disco."""
        with open(path, 'wb') as f:
            pickle.dump({
                'articles': self.articles,
                'bm25': self.bm25
            }, f)
        print(f"Indice salvato in {path}")

    def load(self, path: str = INDEX_FILE):
        """Carica l'indice da disco."""
        if not os.path.exists(path):
            return False

        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.articles = data['articles']
            self.bm25 = data['bm25']
            self.loaded = True

        print(f"Indice caricato: {len(self.articles)} documenti")
        return True

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Cerca articoli rilevanti per la query."""
        if not self.loaded:
            raise RuntimeError("Indice non caricato. Esegui build() o load() prima.")

        query_tokens = tokenize_italian(query)
        scores = self.bm25.get_scores(query_tokens)

        # Ordina per score decrescente
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in ranked[:top_k]:
            if score > 0:  # Solo risultati con match
                art = self.articles[idx]
                results.append({
                    'id': art['id'],
                    'type': art['type'],
                    'title': art['title'],
                    'number': art['number'],
                    'content': art['content'],
                    'relevance_score': round(score, 3)
                })

        return results

    def get_article(self, article_id: str) -> dict | None:
        """Recupera un articolo specifico per ID."""
        for art in self.articles:
            if art['id'] == article_id:
                return art
        return None


# Keywords critiche per categorie di rischio
RISK_KEYWORDS = {
    'inaccettabile': [
        'social scoring', 'punteggio sociale', 'manipolazione', 'subliminale',
        'sfruttamento', 'vulnerabilità', 'identificazione biometrica remota',
        'tempo reale', 'spazi pubblici', 'categorizzazione biometrica',
        'riconoscimento emozioni', 'profilazione', 'polizia predittiva',
        'scraping facciale', 'scraping biometrico', 'sorveglianza di massa'
    ],
    'alto_rischio': [
        'alto rischio', 'high risk', 'sistemi critici', 'infrastrutture',
        'istruzione', 'occupazione', 'servizi essenziali', 'forze dell\'ordine',
        'migrazione', 'giustizia', 'biometrico', 'creditworthiness',
        'assunzione', 'licenziamento', 'valutazione studenti',
        'credito', 'scoring', 'prestito', 'prestiti', 'mutuo', 'mutui', 'affidabilità creditizia',
        'selezione personale', 'curriculum', 'cv', 'recruiting', 'hr',
        'risorse umane', 'valutazione candidati', 'screening candidati',
        'accesso istruzione', 'ammissione', 'esami', 'voti automatici',
        'dispositivi medici', 'diagnostica', 'diagnosi automatica',
        'infrastrutture critiche', 'energia', 'acqua', 'trasporti',
        'frontiera', 'asilo', 'visto', 'immigrazione', 'riconoscimento documenti'
    ],
    'trasparenza': [
        'deepfake', 'chatbot', 'generazione contenuti', 'synthetic media',
        'interazione umana', 'emozioni', 'categorizzazione', 'manipolazione immagini',
        'contenuti generati', 'testo generato', 'immagini generate', 'video generato',
        'assistente virtuale', 'bot', 'conversazione automatica'
    ]
}


def classify_risk_keywords(query: str) -> dict:
    """Classifica basandosi su keywords note (deterministico, no bias)."""
    query_lower = query.lower()

    matches = {
        'inaccettabile': [],
        'alto_rischio': [],
        'trasparenza': []
    }

    for category, keywords in RISK_KEYWORDS.items():
        for kw in keywords:
            if kw in query_lower:
                matches[category].append(kw)

    return matches


if __name__ == '__main__':
    # Test
    index = AIActIndex()

    if os.path.exists(INDEX_FILE):
        print("Caricamento indice esistente...")
        index.load()
    else:
        print("Costruzione nuovo indice...")
        index.build()
        index.save()

    # Test di ricerca
    test_queries = [
        "sistema di riconoscimento facciale per sicurezza aeroportuale",
        "algoritmo per valutazione credito bancario",
        "chatbot per assistenza clienti"
    ]

    for query in test_queries:
        print(f"\n--- Query: {query} ---")
        results = index.search(query, top_k=3)
        for r in results:
            print(f"  [{r['relevance_score']}] {r['title']}")
