"""
AI Act HR Auditor - Specializzato per sistemi HR/Recruiting
Analisi multi-step per performance ottimale su CPU
"""

# Articoli FISSI per HR (Allegato III, punto 4)
HR_ARTICLES = {
    6: {
        'title': 'Regole di classificazione per i sistemi di IA ad alto rischio',
        'summary': 'Definisce quando un sistema è ad alto rischio'
    },
    9: {
        'title': 'Sistema di gestione dei rischi',
        'summary': 'Obbligo di identificare e mitigare rischi durante tutto il ciclo di vita'
    },
    10: {
        'title': 'Dati e governance dei dati',
        'summary': 'I dati di training devono essere privi di bias, accurati, rappresentativi',
        'critical': True,
        'hr_focus': 'Verificare assenza di discriminazioni per genere, età, etnia, disabilità nei dati storici'
    },
    11: {
        'title': 'Documentazione tecnica',
        'summary': 'Documentazione completa secondo Allegato IV'
    },
    12: {
        'title': 'Tenuta delle registrazioni (logging)',
        'summary': 'Log automatici di ogni decisione per audit e contestazioni',
        'hr_focus': 'Ogni candidato deve poter richiedere spiegazione del punteggio ricevuto'
    },
    13: {
        'title': 'Trasparenza e fornitura di informazioni ai deployer',
        'summary': 'Informazioni chiare su capacità e limiti del sistema'
    },
    14: {
        'title': 'Sorveglianza umana',
        'summary': 'Le decisioni finali devono poter essere revisionate da umani',
        'critical': True,
        'hr_focus': 'Nessun candidato può essere scartato SOLO dall\'AI senza review HR'
    },
    15: {
        'title': 'Accuratezza, robustezza e cibersicurezza',
        'summary': 'Il sistema deve essere accurato e resistente a manipolazioni'
    },
    26: {
        'title': 'Obblighi dei deployer di sistemi di IA ad alto rischio',
        'summary': 'Chi usa il sistema deve garantire uso conforme'
    },
    27: {
        'title': 'Valutazione d\'impatto sui diritti fondamentali',
        'summary': 'Obbligatoria PRIMA del deployment',
        'critical': True,
        'hr_focus': 'Valutare impatto su diritto al lavoro, non discriminazione, privacy'
    },
}

# Checklist documentazione HR-specific
HR_DOCUMENTATION_CHECKLIST = [
    {
        'section': 'I. Descrizione Sistema',
        'items': [
            'Nome e versione del sistema',
            'Fornitore e contatti',
            'Scopo: screening CV / ranking candidati / matching',
            'Tipologia di posizioni valutate',
        ]
    },
    {
        'section': 'II. Dati di Training (Art. 10)',
        'items': [
            'Fonte dei dati storici (CV passati, assunzioni, performance)',
            'Periodo temporale dei dati',
            'Distribuzione demografica (genere, età, nazionalità)',
            'Processo di pulizia e anonimizzazione',
            'Analisi bias effettuata (sì/no, metodologia)',
        ]
    },
    {
        'section': 'III. Funzionamento Algoritmo',
        'items': [
            'Tipo di modello (ML, rules-based, ibrido)',
            'Features utilizzate per la valutazione',
            'Features ESCLUSE (es. foto, nome, indirizzo)',
            'Output: punteggio numerico / ranking / classificazione',
            'Soglie decisionali configurate',
        ]
    },
    {
        'section': 'IV. Sorveglianza Umana (Art. 14)',
        'items': [
            'Ruolo HR responsabile della supervisione',
            'Procedura di review delle decisioni AI',
            'Possibilità di override manuale',
            'Formazione HR sull\'uso del sistema',
        ]
    },
    {
        'section': 'V. Logging e Tracciabilità (Art. 12)',
        'items': [
            'Dati registrati per ogni valutazione',
            'Periodo di retention dei log',
            'Procedura per richieste di accesso candidati',
            'Formato export per audit',
        ]
    },
    {
        'section': 'VI. Gestione Rischi (Art. 9)',
        'items': [
            'Rischi identificati (bias, errori, manipolazione)',
            'Misure di mitigazione implementate',
            'Piano di monitoraggio continuo',
            'Procedura aggiornamento modello',
        ]
    },
    {
        'section': 'VII. Valutazione Impatto (Art. 27)',
        'items': [
            'Data esecuzione FRIA',
            'Diritti fondamentali valutati',
            'Stakeholder consultati',
            'Esito e azioni correttive',
        ]
    },
]

# Domande per analisi multi-step
ANALYSIS_STEPS = [
    {
        'id': 'data_bias',
        'title': 'Analisi Dati e Bias (Art. 10)',
        'prompt': '''Analizza SOLO il rischio di BIAS nei dati per questo sistema HR.

SISTEMA: {description}

Rispondi in MAX 150 parole con:
1. Potenziali bias nei dati storici (genere, età, etnia, università, gap lavorativi)
2. Domande da fare al cliente per verificare
3. Test consigliati (es. disparate impact analysis)

NON parlare di altri articoli. SOLO Art. 10 - Governance Dati.'''
    },
    {
        'id': 'human_oversight',
        'title': 'Sorveglianza Umana (Art. 14)',
        'prompt': '''Analizza SOLO i requisiti di SORVEGLIANZA UMANA per questo sistema HR.

SISTEMA: {description}

Rispondi in MAX 150 parole con:
1. Quando è richiesta review umana (sempre? sopra soglia? campione?)
2. Chi deve supervisionare (HR senior? manager? comitato?)
3. Come documentare le decisioni di override

NON parlare di altri articoli. SOLO Art. 14 - Sorveglianza Umana.'''
    },
    {
        'id': 'logging',
        'title': 'Logging e Spiegabilità (Art. 12)',
        'prompt': '''Analizza SOLO i requisiti di LOGGING per questo sistema HR.

SISTEMA: {description}

Rispondi in MAX 150 parole con:
1. Dati minimi da loggare per ogni candidato valutato
2. Come gestire richieste di spiegazione da candidati respinti
3. Retention period consigliato

NON parlare di altri articoli. SOLO Art. 12 - Tenuta Registrazioni.'''
    },
    {
        'id': 'fria',
        'title': 'Valutazione Impatto Diritti (Art. 27)',
        'prompt': '''Analizza SOLO la VALUTAZIONE D'IMPATTO sui diritti fondamentali per questo sistema HR.

SISTEMA: {description}

Rispondi in MAX 150 parole con:
1. Diritti potenzialmente impattati (lavoro, privacy, non-discriminazione)
2. Categorie di persone a rischio (disabili, over 50, donne, minoranze)
3. Misure di mitigazione suggerite

NON parlare di altri articoli. SOLO Art. 27 - FRIA.'''
    },
]


def get_hr_classification() -> dict:
    """Classificazione fissa per sistemi HR."""
    return {
        'level': 'alto',
        'reason': 'Sistema HR per selezione/valutazione personale - Allegato III, punto 4(a)',
        'allegato_iii': '4. Occupazione, gestione dei lavoratori e accesso al lavoro autonomo: (a) sistemi di IA destinati a essere utilizzati per l\'assunzione o la selezione di persone fisiche, in particolare per pubblicare annunci di lavoro mirati, analizzare o filtrare le candidature e valutare i candidati',
    }


def get_hr_articles_list() -> list:
    """Lista articoli formattata."""
    return [
        {
            'number': num,
            'title': info['title'],
            'summary': info['summary'],
            'critical': info.get('critical', False),
            'hr_focus': info.get('hr_focus', '')
        }
        for num, info in HR_ARTICLES.items()
    ]


def get_documentation_checklist() -> list:
    """Checklist documentazione."""
    return HR_DOCUMENTATION_CHECKLIST


def get_analysis_steps() -> list:
    """Step di analisi."""
    return ANALYSIS_STEPS


def format_deterministic_report() -> str:
    """Report base deterministico (senza LLM)."""
    lines = []

    # Classificazione
    classification = get_hr_classification()
    lines.append("## 1. CLASSIFICAZIONE")
    lines.append(f"**Livello: {classification['level'].upper()}**")
    lines.append(f"")
    lines.append(f"*{classification['allegato_iii']}*")
    lines.append("")

    # Articoli applicabili
    lines.append("## 2. ARTICOLI APPLICABILI")
    lines.append("")
    for num, info in HR_ARTICLES.items():
        critical = " ⚠️ CRITICO" if info.get('critical') else ""
        lines.append(f"### Art. {num}: {info['title']}{critical}")
        lines.append(f"{info['summary']}")
        if info.get('hr_focus'):
            lines.append(f"")
            lines.append(f"**Focus HR:** {info['hr_focus']}")
        lines.append("")

    # Requisiti tabella
    lines.append("## 3. REQUISITI CHIAVE")
    lines.append("")
    lines.append("| Priorità | Articolo | Azione |")
    lines.append("|----------|----------|--------|")
    lines.append("| 🔴 Alta | Art. 10 | Audit bias dati di training |")
    lines.append("| 🔴 Alta | Art. 14 | Definire processo review umana |")
    lines.append("| 🔴 Alta | Art. 27 | Eseguire FRIA prima del go-live |")
    lines.append("| 🟡 Media | Art. 12 | Implementare logging decisioni |")
    lines.append("| 🟡 Media | Art. 9 | Documentare gestione rischi |")
    lines.append("| 🟢 Base | Art. 11 | Completare documentazione tecnica |")
    lines.append("")

    return "\n".join(lines)


if __name__ == '__main__':
    # Test
    print(format_deterministic_report())
    print("\n" + "="*50)
    print("CHECKLIST DOCUMENTAZIONE:")
    for section in HR_DOCUMENTATION_CHECKLIST:
        print(f"\n{section['section']}")
        for item in section['items']:
            print(f"  [ ] {item}")
