"""
Mapping ESATTO degli articoli AI Act 2024/1689 (Gazzetta Ufficiale 12.7.2024)
Questo file contiene i riferimenti VERIFICATI per evitare allucinazioni LLM.
"""

# Titoli UFFICIALI degli articoli chiave (verificati sul testo finale)
ARTICLE_TITLES = {
    # TITOLO I - DISPOSIZIONI GENERALI
    1: "Oggetto",
    2: "Ambito di applicazione",
    3: "Definizioni",
    4: "Alfabetizzazione in materia di IA",

    # TITOLO II - PRATICHE VIETATE
    5: "Pratiche di IA vietate",

    # TITOLO III - SISTEMI AD ALTO RISCHIO
    6: "Regole di classificazione per i sistemi di IA ad alto rischio",
    7: "Modifiche dell'allegato III",
    8: "Conformità ai requisiti",
    9: "Sistema di gestione dei rischi",
    10: "Dati e governance dei dati",  # CRUCIALE per bias
    11: "Documentazione tecnica",
    12: "Tenuta delle registrazioni (logging)",  # LOG automatici
    13: "Trasparenza e fornitura di informazioni ai deployer",
    14: "Sorveglianza umana",  # CRUCIALE per HR
    15: "Accuratezza, robustezza e cibersicurezza",

    # TITOLO III CAPO 3 - OBBLIGHI FORNITORI/DEPLOYER
    16: "Obblighi dei fornitori di sistemi di IA ad alto rischio",
    17: "Sistema di gestione della qualità",
    26: "Obblighi dei deployer di sistemi di IA ad alto rischio",
    27: "Valutazione d'impatto sui diritti fondamentali",

    # TITOLO IV - TRASPARENZA
    50: "Obblighi di trasparenza per determinati sistemi di IA",

    # TITOLO VIII - BANCHE DATI
    71: "Banca dati dell'UE per i sistemi di IA ad alto rischio",

    # TITOLO IX - MONITORAGGIO POST-COMMERCIALIZZAZIONE
    72: "Monitoraggio successivo all'immissione sul mercato",
    73: "Segnalazione di incidenti gravi",

    # ALLEGATI
    "III": "Sistemi di IA ad alto rischio (elenco)",
    "IV": "Documentazione tecnica",
}

# Articoli OBBLIGATORI per categoria di sistema
# Quando rilevi una categoria, DEVI includere questi articoli
MANDATORY_ARTICLES = {
    'hr_recruiting': {
        'articles': [6, 9, 10, 11, 12, 13, 14, 26, 27],
        'allegati': ['III', 'IV'],
        'description': 'Sistemi per occupazione, gestione lavoratori, accesso al lavoro autonomo',
        'allegato_iii_punto': '4. Occupazione, gestione dei lavoratori e accesso al lavoro autonomo',
        'rationale': {
            10: "Governance dati: verifica assenza bias nei dati di training (genere, età, etnia)",
            14: "Sorveglianza umana: decisioni finali devono essere revisionate da umani",
            27: "Valutazione impatto diritti fondamentali prima del deployment",
            12: "Logging: tracciare ogni decisione per audit e contestazioni",
        }
    },
    'credito_scoring': {
        'articles': [6, 9, 10, 11, 12, 13, 14, 26, 27],
        'allegati': ['III', 'IV'],
        'description': 'Valutazione affidabilità creditizia, credit scoring',
        'allegato_iii_punto': '5(b). Valutazione dell\'affidabilità creditizia delle persone fisiche',
        'rationale': {
            10: "Governance dati: dati finanziari devono essere accurati e non discriminatori",
            14: "Sorveglianza umana: rifiuti di credito devono poter essere contestati",
            27: "Valutazione impatto: rischio esclusione finanziaria",
        }
    },
    'istruzione': {
        'articles': [6, 9, 10, 11, 12, 13, 14, 26],
        'allegati': ['III', 'IV'],
        'description': 'Accesso istruzione, valutazione studenti, esami',
        'allegato_iii_punto': '3. Istruzione e formazione professionale',
        'rationale': {
            10: "Governance dati: evitare bias socioeconomici nei dati",
            14: "Sorveglianza umana: docenti devono poter override le decisioni AI",
        }
    },
    'biometrico': {
        'articles': [5, 6, 9, 10, 11, 12, 13, 14, 26],
        'allegati': ['III', 'IV'],
        'description': 'Identificazione biometrica, riconoscimento facciale',
        'allegato_iii_punto': '1. Biometria',
        'rationale': {
            5: "Verificare che non rientri nelle pratiche VIETATE (Art.5)",
            10: "Governance dati: consenso, minimizzazione, accuratezza",
            14: "Sorveglianza umana: nessuna decisione automatica senza review",
        }
    },
    'giustizia': {
        'articles': [5, 6, 9, 10, 11, 12, 13, 14, 26, 27],
        'allegati': ['III', 'IV'],
        'description': 'Amministrazione giustizia, polizia, law enforcement',
        'allegato_iii_punto': '6-8. Attività di contrasto, migrazione, giustizia',
        'rationale': {
            5: "Verificare pratiche vietate (profilazione predittiva, social scoring)",
            27: "Valutazione impatto diritti fondamentali OBBLIGATORIA",
        }
    },
    'infrastrutture_critiche': {
        'articles': [6, 9, 10, 11, 12, 13, 14, 15, 26],
        'allegati': ['III', 'IV'],
        'description': 'Gestione infrastrutture critiche (energia, acqua, trasporti)',
        'allegato_iii_punto': '2. Gestione e funzionamento delle infrastrutture critiche',
        'rationale': {
            15: "Accuratezza e cibersicurezza: rischio safety-critical",
            9: "Sistema gestione rischi: analisi failure modes",
        }
    },
    'chatbot_trasparenza': {
        'articles': [50],
        'allegati': [],
        'description': 'Chatbot, assistenti virtuali, generazione contenuti',
        'rationale': {
            50: "Obbligo informare utente che interagisce con AI",
        }
    },
    'deepfake': {
        'articles': [50],
        'allegati': [],
        'description': 'Contenuti audio/video/immagini generati o manipolati',
        'rationale': {
            50: "Obbligo etichettare contenuti come generati artificialmente",
        }
    },
}

# Keywords per rilevare automaticamente la categoria
CATEGORY_KEYWORDS = {
    'hr_recruiting': [
        'curriculum', 'cv', 'recruiting', 'assunzione', 'selezione personale',
        'risorse umane', 'hr', 'candidati', 'colloquio', 'screening cv',
        'valutazione candidati', 'job matching', 'talent', 'hiring',
        'licenziamento', 'promozione', 'valutazione dipendenti', 'performance review'
    ],
    'credito_scoring': [
        'credito', 'credit', 'scoring', 'prestito', 'mutuo', 'finanziamento',
        'affidabilità creditizia', 'banca', 'rating', 'merito creditizio',
        'rischio credito', 'default', 'solvibilità'
    ],
    'istruzione': [
        'studenti', 'esami', 'voti', 'ammissione', 'università', 'scuola',
        'formazione', 'apprendimento', 'valutazione studenti', 'accesso istruzione',
        'test', 'certificazione', 'diploma', 'laurea'
    ],
    'biometrico': [
        'biometrico', 'riconoscimento facciale', 'facial recognition', 'impronta',
        'iride', 'voce', 'identificazione', 'autenticazione biometrica',
        'face detection', 'fingerprint'
    ],
    'giustizia': [
        'polizia', 'giustizia', 'tribunale', 'reato', 'criminalità',
        'law enforcement', 'forze dell\'ordine', 'indagine', 'sorveglianza',
        'frontiera', 'migrazione', 'asilo', 'detenzione', 'recidiva'
    ],
    'infrastrutture_critiche': [
        'infrastruttura', 'energia', 'elettricità', 'acqua', 'gas',
        'trasporti', 'traffico', 'rete', 'smart grid', 'utility',
        'centrale', 'distribuzione'
    ],
    'chatbot_trasparenza': [
        'chatbot', 'assistente virtuale', 'conversazione', 'chat',
        'customer service', 'supporto clienti', 'bot'
    ],
    'deepfake': [
        'deepfake', 'generazione immagini', 'generazione video', 'synthetic',
        'manipolazione', 'fake', 'generativo', 'text-to-image', 'text-to-video'
    ],
}


def detect_categories(description: str) -> list[str]:
    """Rileva automaticamente le categorie dal testo."""
    desc_lower = description.lower()
    detected = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                if category not in detected:
                    detected.append(category)
                break

    return detected


def get_mandatory_articles(description: str) -> dict:
    """
    Restituisce gli articoli OBBLIGATORI per il caso d'uso.
    Questi NON dipendono dall'LLM - sono regole hardcoded.
    """
    categories = detect_categories(description)

    result = {
        'categories': categories,
        'mandatory_articles': [],
        'mandatory_allegati': [],
        'rationale': {},
        'allegato_iii_punti': []
    }

    seen_articles = set()
    seen_allegati = set()

    for cat in categories:
        if cat in MANDATORY_ARTICLES:
            info = MANDATORY_ARTICLES[cat]

            # Aggiungi articoli
            for art_num in info['articles']:
                if art_num not in seen_articles:
                    seen_articles.add(art_num)
                    result['mandatory_articles'].append({
                        'number': art_num,
                        'title': ARTICLE_TITLES.get(art_num, f"Articolo {art_num}"),
                    })

            # Aggiungi allegati
            for all_num in info['allegati']:
                if all_num not in seen_allegati:
                    seen_allegati.add(all_num)
                    result['mandatory_allegati'].append({
                        'number': all_num,
                        'title': ARTICLE_TITLES.get(all_num, f"Allegato {all_num}"),
                    })

            # Aggiungi rationale
            for art_num, reason in info.get('rationale', {}).items():
                if art_num not in result['rationale']:
                    result['rationale'][art_num] = reason

            # Aggiungi punto Allegato III
            if 'allegato_iii_punto' in info:
                if info['allegato_iii_punto'] not in result['allegato_iii_punti']:
                    result['allegato_iii_punti'].append(info['allegato_iii_punto'])

    return result


def format_mandatory_context(mandatory: dict) -> str:
    """Formatta il contesto obbligatorio per il prompt LLM."""
    if not mandatory['categories']:
        return ""

    lines = ["ARTICOLI OBBLIGATORI PER QUESTO CASO D'USO (VERIFICATI):"]
    lines.append(f"Categorie rilevate: {', '.join(mandatory['categories'])}")
    lines.append("")

    if mandatory['allegato_iii_punti']:
        lines.append("CLASSIFICAZIONE ALLEGATO III:")
        for punto in mandatory['allegato_iii_punti']:
            lines.append(f"  • {punto}")
        lines.append("")

    lines.append("ARTICOLI DA APPLICARE:")
    for art in mandatory['mandatory_articles']:
        lines.append(f"  • Articolo {art['number']}: {art['title']}")
        if art['number'] in mandatory['rationale']:
            lines.append(f"    → {mandatory['rationale'][art['number']]}")

    if mandatory['mandatory_allegati']:
        lines.append("")
        lines.append("ALLEGATI DA CONSULTARE:")
        for all in mandatory['mandatory_allegati']:
            lines.append(f"  • Allegato {all['number']}: {all['title']}")

    return "\n".join(lines)


if __name__ == '__main__':
    # Test
    test_cases = [
        "Sistema AI per screening automatico dei CV e selezione candidati",
        "Algoritmo di credit scoring per valutare richieste di prestito",
        "Chatbot per assistenza clienti e-commerce",
        "Sistema di riconoscimento facciale per accesso edifici",
    ]

    for desc in test_cases:
        print(f"\n{'='*60}")
        print(f"INPUT: {desc}")
        print('='*60)

        mandatory = get_mandatory_articles(desc)
        print(format_mandatory_context(mandatory))
