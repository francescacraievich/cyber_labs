[![Open in Streamlit](https://img.shields.io/badge/Open%20in-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://cyberlabs-epss.streamlit.app/)

# CVE Prioritization — Data-Driven Selection

## Overview

This project implements a data-driven methodology for vulnerability prioritization. The goal is to identify CVEs with low current exploitation probability (EPSS < 1%) that are most likely to become high-priority threats in the near future. The approach combines 9 measurable factors from public data sources (NVD, CISA KEV, MITRE CWE Top 25) to produce a composite severity ranking that goes beyond traditional CVSS scoring.

## Methodology

### 1. Data Collection & Preparation

- **NVD Data**: CVEs published between 2025-09-01 and 2025-10-01 are collected from the NVD API.
- **EPSS Data**: Latest Exploit Prediction Scoring System (EPSS) scores are merged with the NVD dataset.
- **CISA KEV**: The Known Exploited Vulnerabilities catalog is downloaded to compute vendor exploitation frequency.
- **Filtering**: Only CVEs with EPSS < 1% are considered for candidate selection.

### 2. Feature Engineering

For each CVE, 9 factors are extracted or derived:

| # | Factor | Source | Rationale |
|---|--------|--------|-----------|
| 1 | CVSS Base Score | NVD CVSS v3.1 | Higher severity = more attractive target |
| 2 | Network Attack Vector | NVD CVSS v3.1 | Remote exploitability enables automated scanning |
| 3 | Low Attack Complexity | NVD CVSS v3.1 | Easy exploits get weaponized faster |
| 4 | No Privileges Required | NVD CVSS v3.1 | No-auth vulns accessible to any attacker |
| 5 | Exploit References | NVD reference tags | Public PoCs lower exploitation barrier |
| 6 | Vendor KEV Frequency | CISA KEV catalog | Vendors with exploitation history are higher risk |
| 7 | CWE in MITRE Top 25 | MITRE CWE Top 25 (2024) | Authoritative dangerous weakness ranking |
| 8 | No Patch Available | NVD reference tags | Unpatched vulns remain exploitable |
| 9 | Pre-Oct-1 KEV Signal | CISA KEV dateAdded | Confirmed exploitation = strongest signal |

### 3. Scoring

Simple additive score — each factor contributes equally (weight = 1). No exponential transformations, no tunable parameters. The composite score ranges from 0 to 9.

### 4. Candidate Selection

- **Stage 1**: Pre-October-1 CISA KEV CVEs are always selected (confirmed active exploitation).
- **Stage 2**: Remaining slots filled by highest composite score, with max 2 CVEs per vendor (portfolio diversification).
- **Validation**: Current EPSS scores are fetched to track prediction accuracy.

### 5. Submission & Tracking

- The selected 10 CVEs are exported to a CSV file for tracking.
- Their EPSS scores are monitored over time via the Streamlit dashboard.

## Files

- `LAB_EPSS_datadriven.ipynb`: Main notebook implementing the methodology.
- `epss_dashboard.py`: Streamlit dashboard for EPSS evolution tracking.
- `preprocessing_utils.py`: Utility functions for NVD data extraction and normalization.
- `data/`: Contains input datasets and output submission file.

## References

- [EPSS API](https://www.first.org/epss/api)
- [CISA KEV Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [MITRE CWE Top 25 (2024)](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html)
- NVD (National Vulnerability Database)
