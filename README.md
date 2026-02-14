---
license: apache-2.0
datasets:
- issdandavis/scbe-aethermoore-knowledge-base
language:
- en
tags:
- embeddings
- hyperbolic-geometry
- poincare-ball
- 21-dimensional
- ai-safety
---

# PHDM 21D Embedding Model

Custom embedding model for the SCBE-AETHERMOORE framework. Maps text inputs into a 21-dimensional Poincare Ball manifold for hyperbolic AI safety governance.

## Architecture

- **Embedding Dimension**: 21D (6D hyperbolic + 6D phase + 3D flux + 6D audit)
- **Geometry**: Poincare Ball B^n with Harmonic Wall containment
- **Polyhedral Lattice**: 16 cognitive polyhedra (5 Platonic + 3 Archimedean + 2 Kepler-Poinsot + 2 Toroidal + 4 Johnson/Rhombic)
- **Neurotransmitter Weights**: Six Sacred Tongues (KO=1.0, AV=1.62, RU=2.62, CA=4.24, UM=6.85, DR=11.09)

## Training Data

- Notion knowledge base exports (SCBE technical docs, PHDM specs)
- Perplexity interaction logs (filtered via GeoSeal privacy layer)
- Sacred Tongue tokenized corpora

## Deployment

- **GCP**: Vertex AI Model Registry + GKE Autopilot (test-scbecluser)
- **AWS**: Lambda functions for intent classification
- **HuggingFace**: Model weights and inference API

## Usage

```python
from phdm_embedding import PHDMEmbedder

embedder = PHDMEmbedder.from_pretrained("issdandavis/phdm-21d-embedding")
vector = embedder.encode("Book a flight from SFO to NYC")
# Returns: 21D numpy array in Poincare Ball coordinates
```

## Dataset Setup (PowerShell)

Use this repo as a working directory for Hugging Face datasets:

```powershell
cd C:\Users\issda\hf-repos\phdm-21d-embedding
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-datasets.txt
```

Set your token in the current shell session:

```powershell
$env:HF_TOKEN="hf_your_token_here"
```

Load and preview a dataset split:

```powershell
python scripts/load_hf_dataset.py --dataset-id issdandavis/scbe-aethermoore-knowledge-base --split train --limit 3
```

Push local JSONL files to a dataset repo:

```powershell
python scripts/push_jsonl_dataset.py --dataset-id issdandavis/scbe-aethermoore-knowledge-base --train .\data\train.jsonl --validation .\data\validation.jsonl
```

Convert Perplexity/Markdown exports into JSONL splits:

```powershell
python scripts/markdown_to_jsonl.py --input-dir C:\path\to\perplexity-export --output-dir .\data --train-ratio 0.9 --validation-ratio 0.1
```

One-shot flow (convert then push):

```powershell
python scripts/markdown_to_jsonl.py --input-dir C:\path\to\perplexity-export --output-dir .\data
python scripts/push_jsonl_dataset.py --dataset-id issdandavis/your-central-knowledge-base --train .\data\train.jsonl --validation .\data\validation.jsonl --test .\data\test.jsonl
```

Expected JSONL row format example:

```json
{"id":"6e4fcd3f34f5b021","source":"perplexity_space_export","space":"SCBE GitHub Deployment","relative_path":"SCBE GitHub Deployment/notes.md","title":"Deployment Notes","text":"Example source content","meta":{"author":"issdandavis"}}
```

## Related

- [SCBE-AETHERMOORE GitHub](https://github.com/issdandavis/SCBE-AETHERMOORE)
- [Knowledge Base Dataset](https://huggingface.co/datasets/issdandavis/scbe-aethermoore-knowledge-base)
- [Interaction Logs Dataset](https://huggingface.co/datasets/issdandavis/scbe-interaction-logs)
