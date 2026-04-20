# Human Evaluation Results — Annotation v1.2

> **Dataset:** 50 stratified files, Gemini single-API
> **Evaluator:** human 
> **Properties scored:** Function, Section  
> **IsAdaptive / IsStinger:** label collected but not scored in this report  
> **Boundary rule:** first section of each song (bar start = 1) has no boundary score  
> **WQS alpha:** 0.6 (boundary), 0.4 (label)  

---

## Function Tag

Total entries: **203**  
_(first section of each song has no boundary score)_

### Boundary

| Metric | Value |
|--------|-------|
| Evaluated (n-1 per song) | 153 |
| Correct (1.0) | 147 |
| Partial (0.5) | 3 |
| Incorrect (0.0) | 3 |
| Accuracy (with partial) | **97.06%** |
| Structural Yield (B=1.0) | **96.08%** |

### Label

| Metric | Value |
|--------|-------|
| Evaluated | 203 |
| Correct (1.0) | 193 |
| Partial (0.5) | 5 |
| Incorrect (0.0) | 5 |
| Label Accuracy (with partial) | **96.31%** |
| Semantic Accuracy (L=1.0) | **95.07%** |

### Weighted Quality Score (WQS)

Formula: `Score_j = (1/N_j) * sum(0.6*B_jk + 0.4*L_jk)`  
_(only entries with both B and L contribute; first sections excluded)_

| Metric | Value |
|--------|-------|
| Global WQS | **95.77%** |
| Songs scored | 38 |
| Segments used | 153 |

#### Per-StratifiedType WQS

| StratifiedType       |  Score (seg) | Score (song) |  Segments |  Songs |
|----------------------|--------------|--------------|-----------|--------|
| 2ndEnding            |       93.94% |       95.83% |        33 |      6 |
| Coda                 |       97.39% |       96.00% |        23 |      5 |
| DC                   |      100.00% |      100.00% |         5 |      4 |
| DS                   |      100.00% |      100.00% |        27 |      5 |
| Linear               |       95.56% |       96.67% |         9 |      3 |
| MaxBars              |       98.18% |       97.50% |        22 |      4 |
| MaxRepeats           |       95.24% |       83.57% |        21 |      4 |
| Random               |       97.69% |       95.71% |        13 |      7 |
| MinBars              | _label-only (single-section, no boundary scored)_ |||


---

## Section Tag

Total entries: **276**  
_(first section of each song has no boundary score)_

### Boundary

| Metric | Value |
|--------|-------|
| Evaluated (n-1 per song) | 230 |
| Correct (1.0) | 227 |
| Partial (0.5) | 1 |
| Incorrect (0.0) | 2 |
| Accuracy (with partial) | **98.91%** |
| Structural Yield (B=1.0) | **98.70%** |

### Label

| Metric | Value |
|--------|-------|
| Evaluated | 276 |
| Correct (1.0) | 258 |
| Partial (0.5) | 6 |
| Incorrect (0.0) | 12 |
| Label Accuracy (with partial) | **94.57%** |
| Semantic Accuracy (L=1.0) | **93.48%** |

### Weighted Quality Score (WQS)

Formula: `Score_j = (1/N_j) * sum(0.6*B_jk + 0.4*L_jk)`  
_(only entries with both B and L contribute; first sections excluded)_

| Metric | Value |
|--------|-------|
| Global WQS | **97.68%** |
| Songs scored | 41 |
| Segments used | 230 |

#### Per-StratifiedType WQS

| StratifiedType       |  Score (seg) | Score (song) |  Segments |  Songs |
|----------------------|--------------|--------------|-----------|--------|
| 2ndEnding            |       93.33% |       94.07% |        39 |      6 |
| Coda                 |      100.00% |      100.00% |        26 |      5 |
| DC                   |      100.00% |      100.00% |        16 |      5 |
| DS                   |      100.00% |      100.00% |        31 |      5 |
| Linear               |       93.85% |       94.67% |        13 |      3 |
| MaxBars              |       95.56% |       96.07% |        45 |      4 |
| MaxRepeats           |       98.06% |       97.65% |        36 |      5 |
| Random               |       96.67% |       98.00% |        24 |      8 |
| MinBars              | _label-only (single-section, no boundary scored)_ |||


