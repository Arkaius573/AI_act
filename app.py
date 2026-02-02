"""
AI Act HR Auditor - App Flask
Specializzato per sistemi HR/Recruiting
Analisi multi-step per performance ottimale
"""

import os
from flask import Flask, render_template, request, jsonify
from hr_auditor import (
    get_hr_classification,
    get_hr_articles_list,
    get_documentation_checklist,
    get_analysis_steps,
    format_deterministic_report,
    HR_ARTICLES,
    ANALYSIS_STEPS
)

app = Flask(__name__)


def query_llama_short(prompt: str, model: str = "phi3:mini") -> str:
    """Query LLM con prompt corto per risposta veloce."""
    try:
        import ollama
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': 0,
                'num_predict': 300  # Risposta corta = veloce
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"[Errore LLM: {str(e)}]"


def run_single_step(step_id: str, description: str) -> dict:
    """Esegue un singolo step di analisi."""
    step = next((s for s in ANALYSIS_STEPS if s['id'] == step_id), None)
    if not step:
        return {'error': 'Step non trovato'}

    prompt = step['prompt'].format(description=description)
    result = query_llama_short(prompt)

    return {
        'step_id': step_id,
        'title': step['title'],
        'analysis': result
    }


def run_all_steps(description: str) -> list:
    """Esegue tutti gli step in sequenza."""
    results = []
    for step in ANALYSIS_STEPS:
        prompt = step['prompt'].format(description=description)
        result = query_llama_short(prompt)
        results.append({
            'step_id': step['id'],
            'title': step['title'],
            'analysis': result
        })
    return results


# --- ROUTES ---

@app.route('/')
def home():
    return render_template('hr_index.html')


@app.route('/api/classify', methods=['POST'])
def classify():
    """Step 0: Classificazione (istantanea, no LLM)."""
    data = request.get_json()
    description = data.get('description', '').strip()

    if len(description) < 20:
        return jsonify({'error': 'Descrizione troppo breve'}), 400

    return jsonify({
        'classification': get_hr_classification(),
        'articles': get_hr_articles_list(),
        'base_report': format_deterministic_report()
    })


@app.route('/api/analyze/step', methods=['POST'])
def analyze_step():
    """Esegue un singolo step di analisi LLM."""
    data = request.get_json()
    description = data.get('description', '').strip()
    step_id = data.get('step_id', '')

    if not description or not step_id:
        return jsonify({'error': 'description e step_id richiesti'}), 400

    result = run_single_step(step_id, description)
    return jsonify(result)


@app.route('/api/analyze/all', methods=['POST'])
def analyze_all():
    """Esegue tutti gli step (più lento ma completo)."""
    data = request.get_json()
    description = data.get('description', '').strip()

    if len(description) < 20:
        return jsonify({'error': 'Descrizione troppo breve'}), 400

    results = run_all_steps(description)
    return jsonify({
        'classification': get_hr_classification(),
        'articles': get_hr_articles_list(),
        'base_report': format_deterministic_report(),
        'detailed_analysis': results
    })


@app.route('/api/checklist')
def checklist():
    """Restituisce la checklist documentazione."""
    return jsonify({
        'checklist': get_documentation_checklist()
    })


@app.route('/api/steps')
def steps():
    """Lista degli step disponibili."""
    return jsonify({
        'steps': [{'id': s['id'], 'title': s['title']} for s in ANALYSIS_STEPS]
    })


@app.route('/api/status')
def status():
    """Stato del sistema."""
    ollama_ok = False
    model_name = "phi3:mini"
    try:
        import ollama
        models = ollama.list()
        ollama_ok = True
        available = [m['name'] for m in models.get('models', [])]
        if model_name not in available and available:
            model_name = available[0]
    except:
        pass

    return jsonify({
        'ollama_available': ollama_ok,
        'model': model_name,
        'specialization': 'HR/Recruiting'
    })


# --- MAIN ---

if __name__ == '__main__':
    print("=" * 50)
    print("AI ACT HR AUDITOR")
    print("Specializzato per sistemi HR/Recruiting")
    print("=" * 50)

    try:
        import ollama
        models = ollama.list()
        available = [m['name'] for m in models.get('models', [])]
        print(f"Ollama: {len(available)} modelli disponibili")
        if available:
            print(f"  → {', '.join(available[:3])}")
    except Exception as e:
        print(f"Ollama: non disponibile")
        print(f"  → Esegui: ollama serve && ollama pull phi3:mini")

    print("-" * 50)
    print("Server: http://localhost:5000")
    print("-" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
