# AI Act Compliance Checker - Guida Setup

## Prerequisiti

- Python 3.10+ installato
- VS Code installato
- Ollama installato (per la generazione LLM)

---

## 1. Setup Ambiente Virtuale

### 1.1 Apri il terminale in VS Code

```bash
# Posizionati nella cartella del progetto
cd /percorso/alla/cartella/AI_act
```

### 1.2 Crea l'ambiente virtuale

```bash
# Windows
python -m venv venv

# Linux/Mac
python3 -m venv venv
```

### 1.3 Attiva l'ambiente virtuale

```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
.\venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

> Quando l'ambiente è attivo, vedrai `(venv)` all'inizio della riga del terminale.

### 1.4 Installa le dipendenze

```bash
pip install --upgrade pip
pip install flask rank-bm25 ollama
```

---

## 2. Configurazione VS Code

### 2.1 Seleziona l'interprete Python

1. Premi `Ctrl+Shift+P` (o `Cmd+Shift+P` su Mac)
2. Digita "Python: Select Interpreter"
3. Seleziona `./venv/bin/python` (o `.\venv\Scripts\python.exe` su Windows)

### 2.2 Estensioni consigliate

Installa queste estensioni VS Code:
- **Python** (Microsoft)
- **Pylance** (Microsoft) - per autocompletamento

---

## 3. Costruzione Indice AI Act

La prima volta devi costruire l'indice BM25 dal documento:

```bash
# Assicurati che venv sia attivo!
python ai_act_index.py
```

Output atteso:
```
Lettura AI_ACT_2024.txt...
Estrazione articoli...
Trovati 498 articoli/allegati
Indice BM25 costruito!
Indice salvato in ai_act_index.pkl
```

> L'indice viene salvato in `ai_act_index.pkl` e ricaricato automaticamente.

---

## 4. Setup Ollama (LLM Locale)

### 4.1 Installa Ollama

- **Windows/Mac**: Scarica da https://ollama.ai
- **Linux**:
  ```bash
  curl -fsSL https://ollama.ai/install.sh | sh
  ```

### 4.2 Scarica il modello Llama3

```bash
ollama pull llama3
```

> Per PC meno potenti, usa `llama3:8b` o `llama3.2:3b`:
> ```bash
> ollama pull llama3.2:3b
> ```

### 4.3 Verifica che Ollama funzioni

```bash
ollama list
```

---

## 5. Avvio dell'Applicazione

### 5.1 Avvia Ollama (in un terminale separato)

```bash
ollama serve
```

> Ollama deve rimanere attivo in background.

### 5.2 Avvia il server Flask

```bash
# Nel terminale VS Code (con venv attivo)
python app.py
```

Output atteso:
```
==================================================
AI ACT COMPLIANCE CHECKER
==================================================
Indice caricato: 498 articoli
Ollama disponibile con X modelli
--------------------------------------------------
Avvio server su http://localhost:5000
--------------------------------------------------
```

### 5.3 Apri l'applicazione

Apri il browser e vai a: **http://localhost:5000**

---

## 6. Struttura Progetto

```
AI_act/
├── venv/                    # Ambiente virtuale (non committare)
├── templates/
│   └── index.html           # Frontend
├── app.py                   # Backend Flask
├── ai_act_index.py          # Indicizzatore BM25
├── ai_act_index.pkl         # Indice pre-costruito (generato)
├── AI_ACT_2024.txt          # Testo normativo EU
├── test_system.py           # Test suite
├── requirements.txt         # Dipendenze
└── SETUP_GUIDE.md           # Questa guida
```

---

## 7. Comandi Rapidi

| Azione | Comando |
|--------|---------|
| Attiva venv (Windows) | `.\venv\Scripts\activate` |
| Attiva venv (Linux/Mac) | `source venv/bin/activate` |
| Installa dipendenze | `pip install -r requirements.txt` |
| Costruisci indice | `python ai_act_index.py` |
| Avvia server | `python app.py` |
| Esegui test | `python test_system.py` |
| Disattiva venv | `deactivate` |

---

## 8. Risoluzione Problemi

### "Ollama non disponibile"

```bash
# Verifica che Ollama sia attivo
ollama list

# Se non funziona, avvialo manualmente
ollama serve
```

### "Indice non trovato"

```bash
# Ricostruisci l'indice
python ai_act_index.py
```

### "ModuleNotFoundError"

```bash
# Assicurati che venv sia attivo
# Poi reinstalla le dipendenze
pip install -r requirements.txt
```

### Errore porta 5000 già in uso

```bash
# Cambia porta in app.py, ultima riga:
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## 9. Modelli Ollama Consigliati

| Modello | RAM Richiesta | Qualità | Comando |
|---------|---------------|---------|---------|
| llama3.2:3b | ~4 GB | Buona | `ollama pull llama3.2:3b` |
| llama3:8b | ~8 GB | Ottima | `ollama pull llama3` |
| mistral:7b | ~6 GB | Ottima | `ollama pull mistral` |

Per PC con poca RAM, usa modelli più piccoli. Modifica `app.py` linea 48:

```python
def query_llama(system_prompt: str, user_prompt: str, model: str = "llama3.2:3b"):
```

---

## 10. Sviluppo e Debug

### Debug in VS Code

1. Crea file `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask App",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/app.py",
            "console": "integratedTerminal",
            "env": {
                "FLASK_DEBUG": "1"
            }
        }
    ]
}
```

2. Premi `F5` per avviare in modalità debug

### Hot Reload

Flask ha già il reload automatico attivo (`debug=True`). Quando modifichi i file Python, il server si riavvia automaticamente.

---

## Note Finali

- L'indice BM25 (`ai_act_index.pkl`) è leggero (~2 MB)
- Il sistema funziona anche SENZA Ollama (solo classificazione + ricerca articoli)
- La classificazione di rischio è deterministica (basata su keywords)
- L'LLM genera solo il report dettagliato, non la classificazione
