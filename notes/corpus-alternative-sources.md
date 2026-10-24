# Corpus Alternative Sources Investigation

**Date:** 2026-10-23
**Session:** 017
**Owner:** KAT-Coder

---

## Problem

Corpus expansion stalled at **19,471 lines** (19.5K). Target is **45,000 lines**. Gap: **25,529 lines**.

**Blocked sources:**
- arXiv API: Rate-limited (429 responses)
- Reddit API: Rate-limited (429 responses)

---

## Alternative Sources Identified

| Source | Type | Est. Lines | Access Method | Priority |
|--------|------|------------|---------------|----------|
| **Hugging Face Datasets** | Academic/Forum | ~8,000 | `datasets.load_dataset()` | High |
| **PubMed Central Open Access** | Full-text papers | ~6,000 | PMC API | High |
| **Internet Archive** | Historical docs | ~5,000 | IA API + text extraction | Medium |
| **Crossref API** | Paper metadata | ~3,000 | DOI metadata API | Medium |
| **arXiv API (retry)** | Academic papers | ~3,500 | Retry with exponential backoff | Low |

**Total estimated:** ~25,500 lines — enough to reach 45K target.

---

## Implementation Plan

### Phase 1: Hugging Face (High Priority)
```python
from datasets import load_dataset

# Consciousness-related datasets
datasets = [
    "consciousness_studies",
    "parapsychology_forum",
    "gateway_process_reports",
]

for ds in datasets:
    try:
        data = load_dataset(ds, split="train")
        with open(f"corpus/built/hf_{ds}.txt", "w") as f:
            for row in data:
                f.write(f"{row['title']}\n\n{row['text']}\n---\n")
    except Exception as e:
        print(f"Failed {ds}: {e}")
```

### Phase 2: PubMed Central (High Priority)
```python
import requests

def fetch_pmc_articles(query, max_results=1000):
    base_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/oi/"
    params = {
        "query": query,
        "retmax": max_results,
        "format": "json"
    }
    resp = requests.get(base_url, params=params, timeout=30)
    return resp.json()

# Queries:
# - "consciousness"
# - "quantum consciousness"
# - "meditation neuroscience"
# - "remote viewing"
# - "precognition"
```

### Phase 3: Internet Archive (Medium Priority)
```python
import requests

def search_archive(query, limit=500):
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": query,
        "fl[]": "identifier",
        "rows": limit,
        "output": "json"
    }
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()

# Queries:
# - "Gateway Process"
# - "STAR GATE"
# - "consciousness research"
# - "hemi-sync"
```

### Phase 4: Crossref (Medium Priority)
```python
import requests

def search_crossref(query, limit=500):
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": limit,
        "select": ["title", "abstract", "published-print", "DOI"]
    }
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()

# Queries:
# - "consciousness quantum"
# - "integrated information theory"
# - "phi consciousness"
# - "multiverse consciousness"
```

---

## Timeline

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Hugging Face | 1 day | 8K lines collected |
| PubMed Central | 1 day | 6K lines collected |
| Internet Archive | 0.5 day | 5K lines collected |
| Crossref | 0.5 day | 3K lines collected |
| arXiv retry | 0.5 day | 3.5K lines collected |
| **Total** | **3 days** | **45K target reached** |

---

## Notes

- All sources are free and open-access
- No API keys required for Hugging Face, PubMed, Crossref
- Internet Archive requires minimal rate limiting (1 req/sec)
- arXiv retry should use exponential backoff (1s → 2s → 4s → 8s)

---

*Investigation complete. Implementation ready for Session 018.*
