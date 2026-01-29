"""
AI Act Compliance Checker - Backend Flask
Sistema leggero per verifica conformità AI Act 2024
"""

import os
import json
from flask import Flask, render_template, request, jsonify, Response
from ai_act_index import AIActIndex, classify_risk_keywords, INDEX_FILE

app = Flask(__name__)

# Inizializza indice all'avvio
index = AIActIndex()

def init_index():
    """Inizializza l'indice BM25."""
    if os.path.exists(INDEX_FILE):
        print("Caricamento indice esistente...")
        index.load()
    else:
        print("Costruzione indice da AI_ACT_2024.txt...")
        index.build()
        index.save()
    return len(index.articles)


# Tenta connessione Ollama
def query_llama(system_prompt: str, user_prompt: str, model: str = "llama3.2:3b") -> str:
    """
    Query a Ollama/Llama locale.
    Usa temperature=0 per output deterministico.
    """
    try:
        import ollama
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            options={
                'temperature': 0,  # Massima determinicità
                'num_predict': 2000  # Limita output
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"ERRORE OLLAMA: {str(e)}\n\nAssicurati che Ollama sia attivo (ollama serve) e che llama3 sia installato (ollama pull llama3)"


def generate_structured_analysis(project_desc: str, skip_llm: bool = False) -> dict:
    """
    Genera analisi strutturata.
    Combina ricerca BM25 deterministica con generazione LLM controllata.
    """

    # 1. RICERCA DETERMINISTICA - Trova articoli rilevanti
    relevant_articles = index.search(project_desc, top_k=8)

    # 2. CLASSIFICAZIONE KEYWORD - Rischio basato su parole chiave note
    keyword_matches = classify_risk_keywords(project_desc)

    # Determina livello di rischio iniziale basato su keywords
    risk_level = "minimo"
    risk_reason = "Nessuna keyword critica rilevata."

    if keyword_matches['inaccettabile']:
        risk_level = "inaccettabile"
        risk_reason = f"Keywords critiche rilevate: {', '.join(keyword_matches['inaccettabile'])}"
    elif keyword_matches['alto_rischio']:
        risk_level = "alto"
        risk_reason = f"Keywords alto rischio rilevate: {', '.join(keyword_matches['alto_rischio'])}"
    elif keyword_matches['trasparenza']:
        risk_level = "limitato"
        risk_reason = f"Keywords trasparenza rilevate: {', '.join(keyword_matches['trasparenza'])}"

    # 3. ESTRAZIONE CONTESTO - Solo articoli trovati (no allucinazioni)
    context_text = ""
    cited_articles = []

    for art in relevant_articles:
        context_text += f"\n\n### {art['title']}\n{art['content'][:1500]}..."
        cited_articles.append({
            'id': art['id'],
            'title': art['title'],
            'relevance': art['relevance_score']
        })

    # 4. PROMPT STRUTTURATO per LLM
    system_prompt = f"""Sei un esperto legale specializzato nel Regolamento EU 2024/1689 (AI Act).

REGOLE FONDAMENTALI:
1. Rispondi SOLO basandoti sugli articoli forniti di seguito
2. NON inventare articoli o requisiti non presenti nel contesto
3. Se non trovi informazioni sufficienti, dichiaralo esplicitamente
4. Cita SEMPRE il numero dell'articolo quando fai affermazioni

ARTICOLI RILEVANTI ESTRATTI DALLA LEGGE:
{context_text}

CLASSIFICAZIONE PRELIMINARE (basata su keyword matching):
- Livello di rischio rilevato: {risk_level.upper()}
- Motivazione: {risk_reason}

COMPITO:
Analizza il progetto descritto dall'utente e genera un report strutturato.
Lingua: Italiano. Tono: formale, tecnico-legale."""

    user_prompt = f"""DESCRIZIONE PROGETTO:
{project_desc}

Genera un'analisi strutturata con queste sezioni:

## 1. CLASSIFICAZIONE AI ACT
Conferma o correggi la classificazione preliminare ({risk_level}), citando gli articoli specifici.

## 2. ARTICOLI POTENZIALMENTE VIOLATI
Elenca SOLO gli articoli dal contesto fornito che potrebbero essere violati, spiegando perché.

## 3. REQUISITI DI CONFORMITA'
Basandoti ESCLUSIVAMENTE sugli articoli forniti, elenca i requisiti obbligatori.

## 4. PIANO D'AZIONE
Azioni concrete per raggiungere la conformità.

## 5. STRUTTURA DOCUMENTAZIONE RICHIESTA
Template per la documentazione conforme all'AI Act."""

    # 5. GENERAZIONE LLM (con contesto controllato) o risposta rapida
    if skip_llm:
        # Modalità veloce: genera report base senza LLM
        llm_analysis = f"""## 1. CLASSIFICAZIONE AI ACT
Livello di rischio: **{risk_level.upper()}**
{risk_reason}

## 2. ARTICOLI POTENZIALMENTE RILEVANTI
{chr(10).join([f"- **{art['title']}** (rilevanza: {art['relevance_score']})" for art in relevant_articles])}

## 3. REQUISITI DI CONFORMITA'
Consultare gli articoli sopra elencati per i requisiti specifici.
Per un'analisi dettagliata, disattivare la modalità veloce.

## 4. PIANO D'AZIONE
1. Verificare la classificazione del sistema AI
2. Consultare gli articoli rilevanti identificati
3. Implementare i requisiti applicabili

## 5. NOTA
Questa è un'analisi rapida basata su keyword matching.
Per un report dettagliato generato da LLM, disattiva "Modalità Veloce"."""
    else:
        llm_analysis = query_llama(system_prompt, user_prompt)

    # 6. STRUTTURA OUTPUT FINALE
    return {
        'project_description': project_desc,
        'fast_mode': skip_llm,
        'risk_classification': {
            'level': risk_level,
            'reason': risk_reason,
            'keyword_matches': keyword_matches
        },
        'relevant_articles': cited_articles,
        'detailed_analysis': llm_analysis,
        'disclaimer': "Questa analisi è generata automaticamente e NON costituisce parere legale. Consultare sempre un esperto per decisioni operative."
    }


# --- ROUTES ---

@app.route('/')
def home():
    """Pagina principale."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Endpoint API per analisi conformità."""
    data = request.get_json()

    if not data or 'description' not in data:
        return jsonify({'error': 'Campo "description" richiesto'}), 400

    description = data['description'].strip()
    fast_mode = data.get('fast', False)  # Modalità veloce senza LLM

    if len(description) < 20:
        return jsonify({'error': 'Descrizione troppo breve (minimo 20 caratteri)'}), 400

    if len(description) > 5000:
        return jsonify({'error': 'Descrizione troppo lunga (massimo 5000 caratteri)'}), 400

    try:
        result = generate_structured_analysis(description, skip_llm=fast_mode)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search_articles():
    """Ricerca articoli senza analisi LLM (veloce)."""
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({'error': 'Campo "query" richiesto'}), 400

    query = data['query'].strip()
    top_k = data.get('top_k', 5)

    results = index.search(query, top_k=min(top_k, 20))
    return jsonify({'results': results})


@app.route('/api/article/<article_id>')
def get_article(article_id):
    """Recupera un articolo specifico."""
    article = index.get_article(article_id)
    if article:
        return jsonify(article)
    return jsonify({'error': 'Articolo non trovato'}), 404


@app.route('/api/status')
def status():
    """Stato del sistema."""
    ollama_ok = False
    try:
        import ollama
        ollama.list()
        ollama_ok = True
    except:
        pass

    return jsonify({
        'index_loaded': index.loaded,
        'articles_count': len(index.articles) if index.loaded else 0,
        'ollama_available': ollama_ok
    })


# --- MAIN ---

if __name__ == '__main__':
    print("=" * 50)
    print("AI ACT COMPLIANCE CHECKER")
    print("=" * 50)

    # Inizializza indice
    n_articles = init_index()
    print(f"Indice caricato: {n_articles} articoli")

    # Verifica Ollama
    try:
        import ollama
        models = ollama.list()
        print(f"Ollama disponibile con {len(models.get('models', []))} modelli")
    except Exception as e:
        print(f"ATTENZIONE: Ollama non disponibile ({e})")
        print("Per generazione LLM, esegui: ollama serve && ollama pull llama3")

    print("-" * 50)
    print("Avvio server su http://localhost:5000")
    print("-" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
