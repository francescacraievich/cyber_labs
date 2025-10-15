
# CVE Prioritization Using the Albanese et al. (2023) Vulnerability Metrics Framework

<div align="center">

![Security Research](https://img.shields.io/badge/Security-Vulnerability%20Analysis-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

</div>

<div align="center">

**Framework & Data Sources**

![CVSS](https://img.shields.io/badge/Framework-CVSS-informational?logo=security)
![EPSS](https://img.shields.io/badge/Scoring-EPSS-orange)
![NVD](https://img.shields.io/badge/Data-NVD%20API-blue)
![CVE](https://img.shields.io/badge/Focus-CVE%20Analysis-red)
![Paper](https://img.shields.io/badge/Based%20on-Albanese%20et%20al.%202023-blueviolet)

**Technologies**

![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas)
![NumPy](https://img.shields.io/badge/NumPy-Scientific-013243?logo=numpy)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-3F4F75?logo=plotly)

</div>

---

## Overview
...resto del README...

# CVE Prioritization Using the Albanese et al. (2023) Vulnerability Metrics Framework

## Overview

This project implements a principled methodology for vulnerability prioritization based on the framework proposed by Albanese et al. (2023). The goal is to identify CVEs with low current exploitation probability (EPSS < 1%) that are most likely to become high-priority threats in the near future. The approach combines multiple technical and contextual metrics to produce a severity ranking that goes beyond traditional CVSS scoring.

## Methodology

### 1. Data Collection & Preparation

- **NVD Data**: CVEs published between 2025-09-01 and 2025-10-01 are collected from the NVD API.
- **EPSS Data**: Latest Exploit Prediction Scoring System (EPSS) scores are merged with the NVD dataset.
- **Filtering**: Only CVEs with EPSS < 1% are considered for further analysis.

### 2. Feature Engineering

For each CVE, the following features are extracted or derived:
- **CVSS Base Score**: Technical severity (0-10 scale).
- **Number of References**: Proxy for public visibility and research interest.
- **Attack Vector, Complexity, Privileges**: Key CVSS submetrics.
- **Vendor**: Extracted from CPEs; flagged if a "popular vendor".
- **CWE List**: Used to flag "dangerous" weakness types (e.g., SQLi, XSS).
- **Other fields**: Description, publication date, etc.

### 3. Metric Calculation

#### a. Exploitation Likelihood ($\rho(v)$, Equation 14)

Probability that an attacker will exploit the vulnerability, modeled as a product of exponential factors:

$$
\rho(v) = \prod_{X \in X^\uparrow_l} \left(1 - e^{-\alpha_X f_X(X(v))}\right)
$$

Where $X^\uparrow_l$ are variables that increase likelihood, such as:
- CVSS base score (normalized)
- Number of references (normalized)
- Network attack vector
- Low attack complexity
- No privileges required
- Dangerous CWE present

#### b. Exposure Factor ($ef(v)$, Equation 17)

Relative loss of utility if the vulnerability is exploited:

$$
ef(v) = \prod_{X \in X^\uparrow_e} \left(1 - e^{-\alpha_X f_X(X(v))}\right)
$$

Where $X^\uparrow_e$ are variables that increase exposure, such as:
- CVSS impact (proxied by base score)
- Popular vendor

#### c. Severity Score ($s(v)$, Equation 18)

Overall prioritization metric, combining likelihood and exposure:

$$
s(v) = \rho(v) \times ef(v)
$$

### 4. Parameter Tuning

- $\alpha$ values for each factor are set as recommended in the paper (e.g., cvss=2.0, refs=1.5, network=3.0, etc.).
- These control the influence of each variable and can be tuned for different scenarios.

### 5. Candidate Selection

- **Ranking**: All low-EPSS CVEs are ranked by their computed severity score $s(v)$.
- **Selection**: The top 10 CVEs with the highest $s(v)$ are selected as candidates most likely to see an increase in exploitation probability.
- **Justification**: These CVEs typically have high technical severity, are remotely exploitable, affect popular vendors, have dangerous CWEs, and/or high public visibility.

### 6. Submission & Tracking

- The selected 10 CVEs are exported to a CSV file for tracking.
- Their EPSS scores will be monitored over time to validate the predictive power of the framework.


## Files

- `LAB_EPSS.ipynb`: Main notebook implementing the methodology.
- `data/`: Contains input datasets and output submission file.
- `preprocessing_utils.py`: Utility functions for data extraction and normalization.

## References

- Albanese et al. (2023), "A framework for designing vulnerability metrics"
- [EPSS API](https://www.first.org/epss/api)
- NVD (National Vulnerability Database)


