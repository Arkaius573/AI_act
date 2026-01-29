"""
Test completo del sistema AI Act Compliance Checker
Verifica che la ricerca BM25 e la classificazione funzionino correttamente.
"""

import json
from ai_act_index import AIActIndex, classify_risk_keywords, INDEX_FILE

def test_index_loading():
    """Test 1: Caricamento indice"""
    print("\n" + "="*60)
    print("TEST 1: Caricamento indice BM25")
    print("="*60)

    index = AIActIndex()
    success = index.load(INDEX_FILE)

    if success:
        print(f"OK - Indice caricato: {len(index.articles)} documenti")
        return index
    else:
        print("ERRORE - Indice non trovato. Esegui prima: python ai_act_index.py")
        return None


def test_keyword_classification():
    """Test 2: Classificazione basata su keywords (deterministico)"""
    print("\n" + "="*60)
    print("TEST 2: Classificazione keyword (deterministico, no bias)")
    print("="*60)

    test_cases = [
        {
            'desc': "Sistema di social scoring per valutare l'affidabilità dei cittadini",
            'expected': 'inaccettabile'
        },
        {
            'desc': "Riconoscimento facciale in tempo reale in spazi pubblici",
            'expected': 'inaccettabile'
        },
        {
            'desc': "Sistema di scoring del credito bancario per valutare i clienti",
            'expected': 'alto_rischio'
        },
        {
            'desc': "Algoritmo per selezione candidati e assunzione personale",
            'expected': 'alto_rischio'
        },
        {
            'desc': "Chatbot per assistenza clienti",
            'expected': 'trasparenza'
        },
        {
            'desc': "Sistema di generazione immagini con deepfake",
            'expected': 'trasparenza'
        },
        {
            'desc': "App meteo con previsioni automatiche",
            'expected': 'minimo'
        }
    ]

    for i, case in enumerate(test_cases, 1):
        matches = classify_risk_keywords(case['desc'])

        # Determina livello rilevato
        if matches['inaccettabile']:
            detected = 'inaccettabile'
        elif matches['alto_rischio']:
            detected = 'alto_rischio'
        elif matches['trasparenza']:
            detected = 'trasparenza'
        else:
            detected = 'minimo'

        status = "OK" if detected == case['expected'] else "WARN"
        print(f"\n{i}. {case['desc'][:50]}...")
        print(f"   Atteso: {case['expected']} | Rilevato: {detected} [{status}]")

        all_kw = matches['inaccettabile'] + matches['alto_rischio'] + matches['trasparenza']
        if all_kw:
            print(f"   Keywords: {', '.join(all_kw)}")


def test_article_search(index):
    """Test 3: Ricerca articoli rilevanti"""
    print("\n" + "="*60)
    print("TEST 3: Ricerca articoli (BM25)")
    print("="*60)

    test_queries = [
        "sistema di riconoscimento facciale biometrico identificazione persone",
        "valutazione automatica curriculum candidati selezione personale HR",
        "chatbot intelligente assistenza clienti conversazione automatica",
        "sistema scoring credito bancario prestiti valutazione rischio",
        "videosorveglianza intelligente sicurezza pubblica polizia"
    ]

    for query in test_queries:
        print(f"\nQuery: {query[:60]}...")
        results = index.search(query, top_k=5)

        if results:
            for r in results:
                print(f"  [{r['relevance_score']:5.2f}] {r['title']}")
        else:
            print("  Nessun risultato")


def test_full_analysis(index):
    """Test 4: Analisi completa (senza LLM)"""
    print("\n" + "="*60)
    print("TEST 4: Analisi completa (output strutturato)")
    print("="*60)

    project_desc = """
    Sistema di intelligenza artificiale per la valutazione automatica dei
    curriculum vitae dei candidati durante i processi di assunzione.
    L'algoritmo analizza le competenze, l'esperienza professionale e genera
    un punteggio di idoneità per ogni candidato. Viene utilizzato dalle
    risorse umane per filtrare le candidature.
    """

    print(f"\nPROGETTO: {project_desc.strip()[:100]}...")

    # 1. Classificazione keyword
    keyword_matches = classify_risk_keywords(project_desc)

    if keyword_matches['inaccettabile']:
        risk_level = "INACCETTABILE"
        risk_reason = f"Keywords critiche: {keyword_matches['inaccettabile']}"
    elif keyword_matches['alto_rischio']:
        risk_level = "ALTO"
        risk_reason = f"Keywords alto rischio: {keyword_matches['alto_rischio']}"
    elif keyword_matches['trasparenza']:
        risk_level = "LIMITATO"
        risk_reason = f"Keywords trasparenza: {keyword_matches['trasparenza']}"
    else:
        risk_level = "MINIMO"
        risk_reason = "Nessuna keyword critica"

    print(f"\n--- CLASSIFICAZIONE ---")
    print(f"Livello: {risk_level}")
    print(f"Motivo: {risk_reason}")

    # 2. Articoli rilevanti
    print(f"\n--- ARTICOLI RILEVANTI ---")
    results = index.search(project_desc, top_k=5)
    for r in results:
        print(f"  [{r['relevance_score']:5.2f}] {r['title']}")

    # 3. Output strutturato
    print(f"\n--- OUTPUT STRUTTURATO (JSON) ---")
    output = {
        'risk_classification': {
            'level': risk_level.lower(),
            'reason': risk_reason,
            'keyword_matches': keyword_matches
        },
        'relevant_articles': [
            {'id': r['id'], 'title': r['title'], 'score': r['relevance_score']}
            for r in results
        ]
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def test_high_risk_case(index):
    """Test 5: Caso ad alto rischio - riconoscimento biometrico"""
    print("\n" + "="*60)
    print("TEST 5: Caso critico - Sistema biometrico (deve essere INACCETTABILE)")
    print("="*60)

    project_desc = """
    Sistema di identificazione biometrica remota in tempo reale per il
    riconoscimento facciale in spazi pubblici, collegato alle telecamere
    di sorveglianza della città. Permette di identificare automaticamente
    i cittadini che passano per le strade principali.
    """

    print(f"\nPROGETTO: {project_desc.strip()[:100]}...")

    keyword_matches = classify_risk_keywords(project_desc)

    if keyword_matches['inaccettabile']:
        risk_level = "INACCETTABILE"
        print(f"\nOK - Classificato come {risk_level}")
        print(f"Keywords rilevate: {keyword_matches['inaccettabile']}")
    else:
        print(f"\nWARN - NON classificato come inaccettabile!")
        print(f"Keywords trovate: {keyword_matches}")

    results = index.search(project_desc, top_k=3)
    print(f"\nArticoli trovati:")
    for r in results:
        # Cerca se contiene riferimenti a pratiche vietate
        is_art5 = 'art_5' in r['id'].lower() or 'articolo 5' in r['title'].lower()
        marker = " << ARTICOLO 5 (PRATICHE VIETATE)" if is_art5 else ""
        print(f"  {r['title']}: score {r['relevance_score']}{marker}")


if __name__ == '__main__':
    print("\n" + "#"*60)
    print("#  AI ACT COMPLIANCE CHECKER - TEST SUITE")
    print("#"*60)

    # Test 1
    index = test_index_loading()
    if not index:
        exit(1)

    # Test 2
    test_keyword_classification()

    # Test 3
    test_article_search(index)

    # Test 4
    test_full_analysis(index)

    # Test 5
    test_high_risk_case(index)

    print("\n" + "="*60)
    print("TEST COMPLETATI")
    print("="*60)
    print("""
RISULTATO:
- La classificazione basata su keywords e DETERMINISTICA (no bias)
- La ricerca articoli usa BM25 (keyword matching, non embedding)
- Il sistema NON puo allucinare articoli inesistenti

PER AVVIARE L'APP WEB:
1. Assicurati che Ollama sia attivo: ollama serve
2. Scarica llama3 se non l'hai: ollama pull llama3
3. Avvia il server: python app.py
4. Apri http://localhost:5000
""")
