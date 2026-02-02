"""
AI Act Compliance Checker - Backend Flask
Sistema leggero per verifica conformità AI Act 2024
"""

import os
from flask import Flask, render_template, request, jsonify
from ai_act_index import AIActIndex, classify_risk_keywords, INDEX_FILE
from article_mapping import (
    get_mandatory_articles,
    format_mandatory_context,
    ARTICLE_TITLES
)

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


def query_llama(system_prompt: str, user_prompt: str, model: str = "phi3:mini") -> str:
    """Query a Ollama/Llama locale con temperature=0."""
    try:
        import ollama
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            options={
                'temperature': 0,
                'num_predict': 1500  # Ridotto per velocità
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"ERRORE OLLAMA: {str(e)}"


def generate_structured_analysis(project_desc: str, skip_llm: bool = False) -> dict:
    """
    Genera analisi strutturata con ZERO allucinazioni sugli articoli.
    Gli articoli obbligatori sono determinati da regole hardcoded, non dall'LLM.
    """

    # 1. CLASSIFICAZIONE KEYWORD (deterministico)
    keyword_matches = classify_risk_keywords(project_desc)

    risk_level = "minimo"
    risk_reason = "Nessuna keyword critica rilevata."

    if keyword_matches['inaccettabile']:
        risk_level = "inaccettabile"
        risk_reason = f"Pratiche potenzialmente VIETATE: {', '.join(keyword_matches['inaccettabile'])}"
    elif keyword_matches['alto_rischio']:
        risk_level = "alto"
        risk_reason = f"Sistema ad ALTO RISCHIO: {', '.join(keyword_matches['alto_rischio'])}"
    elif keyword_matches['trasparenza']:
        risk_level = "limitato"
        risk_reason = f"Obblighi di TRASPARENZA: {', '.join(keyword_matches['trasparenza'])}"

    # 2. ARTICOLI OBBLIGATORI (deterministico - da mapping hardcoded)
    mandatory = get_mandatory_articles(project_desc)

    # 3. RICERCA BM25 per contesto aggiuntivo (ma NON per decidere gli articoli)
    search_results = index.search(project_desc, top_k=4)

    # 4. COSTRUISCI OUTPUT DETERMINISTICO (senza LLM)
    deterministic_output = build_deterministic_report(
        risk_level, risk_reason, mandatory, keyword_matches
    )

    # 5. SE richiesto, usa LLM solo per ESPANDERE (non per decidere articoli)
    if skip_llm:
        llm_analysis = deterministic_output
    else:
        llm_analysis = generate_llm_expansion(
            project_desc, risk_level, mandatory, deterministic_output
        )

    # 6. STRUTTURA OUTPUT FINALE
    return {
        'project_description': project_desc,
        'fast_mode': skip_llm,
        'risk_classification': {
            'level': risk_level,
            'reason': risk_reason,
            'keyword_matches': keyword_matches
        },
        'detected_categories': mandatory['categories'],
        'mandatory_articles': mandatory['mandatory_articles'],
        'detailed_analysis': llm_analysis,
        'disclaimer': "Analisi automatica basata su Reg. UE 2024/1689. NON costituisce parere legale."
    }


def build_deterministic_report(risk_level: str, risk_reason: str, mandatory: dict, keywords: dict) -> str:
    """
    Costruisce un report COMPLETAMENTE deterministico.
    Questo è il cuore anti-allucinazioni: tutto è hardcoded.
    """
    lines = []

    # Sezione 1: Classificazione
    lines.append("## 1. CLASSIFICAZIONE AI ACT")
    lines.append(f"**Livello di rischio: {risk_level.upper()}**")
    lines.append(f"{risk_reason}")
    lines.append("")

    if mandatory['categories']:
        lines.append(f"**Categorie rilevate:** {', '.join(mandatory['categories'])}")
        if mandatory['allegato_iii_punti']:
            lines.append("")
            lines.append("**Riferimento Allegato III:**")
            for punto in mandatory['allegato_iii_punti']:
                lines.append(f"- {punto}")
    lines.append("")

    # Sezione 2: Articoli applicabili (VERIFICATI)
    lines.append("## 2. ARTICOLI APPLICABILI (Reg. UE 2024/1689)")
    lines.append("*I seguenti articoli sono stati identificati automaticamente in base alla categoria del sistema.*")
    lines.append("")

    if mandatory['mandatory_articles']:
        for art in mandatory['mandatory_articles']:
            art_num = art['number']
            art_title = art['title']
            lines.append(f"### Articolo {art_num}: {art_title}")
            if art_num in mandatory['rationale']:
                lines.append(f"**Rilevanza:** {mandatory['rationale'][art_num]}")
            lines.append("")
    else:
        lines.append("Nessun articolo specifico identificato. Sistema a rischio minimo.")
        lines.append("")

    # Sezione 3: Requisiti chiave
    lines.append("## 3. REQUISITI DI CONFORMITÀ")
    if risk_level in ['alto', 'inaccettabile']:
        lines.append("Per sistemi ad alto rischio, i requisiti principali sono:")
        lines.append("")
        lines.append("| Articolo | Requisito | Descrizione |")
        lines.append("|----------|-----------|-------------|")
        lines.append("| Art. 9 | Gestione rischi | Sistema documentato di identificazione e mitigazione rischi |")
        lines.append("| Art. 10 | Governance dati | Dati di training privi di bias, accurati, rappresentativi |")
        lines.append("| Art. 11 | Documentazione | Documentazione tecnica completa (vedi Allegato IV) |")
        lines.append("| Art. 12 | Logging | Registrazione automatica eventi per tracciabilità |")
        lines.append("| Art. 13 | Trasparenza | Informazioni chiare ai deployer su capacità/limiti |")
        lines.append("| Art. 14 | Sorveglianza umana | Possibilità di override umano delle decisioni |")
        lines.append("| Art. 15 | Robustezza | Accuratezza, resilienza, cybersecurity |")
    elif risk_level == 'limitato':
        lines.append("Per sistemi con obblighi di trasparenza:")
        lines.append("")
        lines.append("| Articolo | Requisito |")
        lines.append("|----------|-----------|")
        lines.append("| Art. 50 | Informare l'utente che sta interagendo con un sistema AI |")
        lines.append("| Art. 50 | Etichettare contenuti generati artificialmente (deepfake) |")
    else:
        lines.append("Sistema a rischio minimo: nessun requisito specifico obbligatorio.")
        lines.append("Si consiglia comunque di seguire le best practice di trasparenza.")
    lines.append("")

    # Sezione 4: Piano d'azione
    lines.append("## 4. PIANO D'AZIONE")
    if risk_level in ['alto', 'inaccettabile']:
        lines.append("1. **Valutazione impatto diritti fondamentali** (Art. 27)")
        lines.append("2. **Audit dei dati di training** per bias (Art. 10)")
        lines.append("3. **Implementare logging automatico** (Art. 12)")
        lines.append("4. **Definire procedure di sorveglianza umana** (Art. 14)")
        lines.append("5. **Redigere documentazione tecnica** secondo Allegato IV")
        lines.append("6. **Registrazione nella banca dati UE** (Art. 71)")
        lines.append("7. **Piano di monitoraggio post-market** (Art. 72)")
    elif risk_level == 'limitato':
        lines.append("1. Implementare avviso di interazione con AI")
        lines.append("2. Se genera contenuti: etichettare come artificiali")
        lines.append("3. Documentare le misure di trasparenza adottate")
    else:
        lines.append("1. Monitorare eventuali aggiornamenti normativi")
        lines.append("2. Documentare volontariamente le caratteristiche del sistema")
    lines.append("")

    # Sezione 5: Documentazione
    lines.append("## 5. STRUTTURA DOCUMENTAZIONE (Allegato IV)")
    if risk_level in ['alto', 'inaccettabile']:
        lines.append("```")
        lines.append("DOCUMENTAZIONE TECNICA - AI ACT")
        lines.append("================================")
        lines.append("I.   Descrizione generale del sistema")
        lines.append("II.  Informazioni sui componenti e processo di sviluppo")
        lines.append("III. Funzionamento del sistema")
        lines.append("IV.  Monitoraggio e funzionamento")
        lines.append("V.   Sistema di gestione dei rischi (Art. 9)")
        lines.append("VI.  Governance dei dati (Art. 10)")
        lines.append("VII. Valutazione conformità e certificazioni")
        lines.append("VIII.Piano di monitoraggio post-commercializzazione")
        lines.append("```")
    else:
        lines.append("Documentazione non obbligatoria ma consigliata per trasparenza.")

    return "\n".join(lines)


def generate_llm_expansion(project_desc: str, risk_level: str, mandatory: dict, base_report: str) -> str:
    """
    Usa LLM SOLO per espandere il report con consigli pratici.
    Gli articoli sono GIÀ DECISI - l'LLM non può cambiarli.
    """
    # Contesto minimo per LLM - velocità!
    mandatory_context = format_mandatory_context(mandatory)

    system_prompt = f"""Sei un consulente per la conformità AI Act (Reg. UE 2024/1689).

REGOLE FERREE:
1. Gli articoli applicabili sono GIÀ STATI DETERMINATI e sono elencati sotto. NON aggiungerne altri.
2. Il tuo compito è SOLO dare consigli PRATICI di implementazione.
3. NON citare articoli diversi da quelli forniti.
4. Rispondi in italiano, max 500 parole.

{mandatory_context}

LIVELLO DI RISCHIO DETERMINATO: {risk_level.upper()}"""

    user_prompt = f"""SISTEMA DA ANALIZZARE:
{project_desc}

Basandoti ESCLUSIVAMENTE sugli articoli già identificati sopra, fornisci:
1. Consigli pratici specifici per questo caso d'uso
2. Potenziali criticità da affrontare
3. Suggerimenti per l'implementazione della sorveglianza umana (se applicabile)

NON aggiungere altri articoli. Usa SOLO quelli già elencati."""

    llm_response = query_llama(system_prompt, user_prompt)

    # Combina report deterministico + espansione LLM
    return base_report + "\n\n## 6. CONSIGLI PRATICI (Generati da AI)\n" + llm_response


# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()

    if not data or 'description' not in data:
        return jsonify({'error': 'Campo "description" richiesto'}), 400

    description = data['description'].strip()
    fast_mode = data.get('fast', False)

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
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Campo "query" richiesto'}), 400

    query = data['query'].strip()
    top_k = data.get('top_k', 5)
    results = index.search(query, top_k=min(top_k, 20))
    return jsonify({'results': results})


@app.route('/api/article/<article_id>')
def get_article(article_id):
    article = index.get_article(article_id)
    if article:
        return jsonify(article)
    return jsonify({'error': 'Articolo non trovato'}), 404


@app.route('/api/status')
def status():
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
    print("AI ACT COMPLIANCE CHECKER v2.0")
    print("(Anti-allucinazioni: articoli hardcoded)")
    print("=" * 50)

    n_articles = init_index()
    print(f"Indice BM25: {n_articles} documenti")

    try:
        import ollama
        models = ollama.list()
        print(f"Ollama: {len(models.get('models', []))} modelli")
    except Exception as e:
        print(f"Ollama: non disponibile ({e})")

    print("-" * 50)
    print("Server: http://localhost:5000")
    print("-" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
