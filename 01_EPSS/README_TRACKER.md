cd# EPSS Tracker Dashboard

Dashboard Streamlit per monitorare l'evoluzione dei punteggi EPSS delle CVE selezionate.

## 🚀 Quick Start

### 1. Installa le dipendenze

```bash
pip install streamlit plotly requests pandas
```

### 2. Avvia la dashboard

```bash
cd 01_EPSS
streamlit run epss_tracker.py
```

La dashboard si aprirà automaticamente nel browser all'indirizzo `http://localhost:8501`

## 📊 Funzionalità

### Metriche principali
- **Avg Initial EPSS**: Media EPSS al 01/10/2025 (baseline)
- **Avg Current EPSS**: Media EPSS corrente (aggiornata via API)
- **Avg Change**: Variazione media EPSS
- **CVEs Increased**: Numero di CVE con EPSS aumentato

### Tabella dettagliata
Mostra per ogni CVE:
- CVE ID
- CVSS Base Score
- Severity
- Initial EPSS (01/10/2025)
- Current EPSS (live da API)
- Change (assoluta e percentuale)
- Percentile
- Last Updated

### Visualizzazioni

1. **EPSS Evolution**: Confronto bar chart tra EPSS iniziale e corrente
2. **EPSS Change Heatmap**: Variazioni percentuali con scala colori
3. **CVSS vs Current EPSS**: Scatter plot con bubble size = change

### Export
- Download CSV con tutti i dati di tracking
- Nome file: `epss_tracking_YYYYMMDD.csv`

## 🔄 Aggiornamento Dati

La dashboard recupera automaticamente i dati EPSS più recenti dall'API FIRST.org:
- **Cache**: 1 ora (per non sovraccaricare l'API)
- **Refresh**: Ricarica la pagina per forzare l'aggiornamento
- **Fallback**: Se l'API non risponde, mostra i dati iniziali dal CSV

## 📁 File Richiesti

La dashboard richiede:
```
01_EPSS/
├── epss_tracker.py              # Dashboard Streamlit
├── data/
│   └── francesca_craievich_submission.csv  # CVE selezionate
```

## 🔍 CVE Monitorate

10 CVE selezionate con:
- ✅ EPSS < 1% al 01/10/2025
- ✅ CVSS score 7.0-9.1 (HIGH/CRITICAL)
- ✅ Framework-based selection (Albanese et al. 2023)
- ✅ Dangerous CWEs (SQLi, XSS, RCE, Privilege Escalation)
- ✅ Network exploitability

### Lista CVE
1. CVE-2025-9760 - Portabilis i-Educar (CVSS 8.8)
2. CVE-2025-9778 - Tenda W12 (CVSS 7.0)
3. CVE-2025-9566 - Podman (CVSS 8.1)
4. CVE-2025-10608 - Portabilis i-Educar (CVSS 8.8)
5. CVE-2025-9900 - Libtiff (CVSS 8.8)
6. CVE-2025-11029 - Vvveb (CVSS 8.8)
7. CVE-2025-11047 - Portabilis i-Educar (CVSS 8.8)
8. CVE-2025-11048 - Portabilis i-Educar (CVSS 8.8)
9. CVE-2025-11083 - GNU Binutils (CVSS 7.8)
10. CVE-2025-7493 - FreeIPA (CVSS 9.1)

## 🎯 Obiettivo

Validare l'ipotesi che queste CVE vedranno un aumento significativo dell'EPSS nei prossimi mesi a causa di:
- Severità tecnica elevata
- Facilità di exploit (Network/Low/None o Low privileges)
- CWE storicamente sfruttati
- Visibilità pubblica (6-13 riferimenti)

## 📅 Timeline

- **Baseline**: 01/10/2025
- **Tracking period**: Ottobre 2025 - Fine corso
- **Expected**: Almeno 50% delle CVE raggiungeranno EPSS > 5%

## 🛠️ Troubleshooting

### Errore: ModuleNotFoundError
```bash
pip install streamlit plotly requests pandas
```

### Errore: API timeout
L'API FIRST potrebbe essere lenta. La dashboard usa un timeout di 10 secondi e cache di 1 ora.

### Errore: File not found
Assicurati di essere nella cartella `01_EPSS` quando avvii Streamlit:
```bash
cd c:\Users\franc\Documents\cyber_labs\01_EPSS
streamlit run epss_tracker.py
```

## 📚 Riferimenti

- **EPSS API**: https://www.first.org/epss/api
- **Paper**: Albanese et al. (2023) - "A framework for designing vulnerability metrics"
- **Dataset**: NVD (01/09/2025 - 30/09/2025)
