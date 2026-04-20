# Super Mario Structure Annotation Dataset

Structural annotations and section-pair dataset for 554 Super Mario video game music transcriptions, used in the paper:

> **Structure-Aware Game Music Generation with Similarity-Bucket Conditioning**  
> *[Authors redacted for review]* · ISMIR 2026  
> [Paper link — to be added after review]

Training and evaluation code: [`ShxLuo-Saxon/structure-llama`](https://github.com/ShxLuo-Saxon/structure-llama)

This release has two independent parts. **Part 1** (annotations only) is self-contained and requires no additional data. **Part 2** (section-pair dataset) provides pre-computed similarity scores and section identifiers; sections can be reconstructed from the annotation JSONs and the source transcriptions.

---

## Part 1 — Structural Annotations

### What's included

```
annotations/   554 JSON files, one per piece
pipeline/
├── mxl_to_abc.py       MXL → ABC conversion (uses bundled xml2abc.py)
├── reformat_abc.py     ABC layout normalisation for LLM readability
├── single_api.py       Annotation script (Gemini API)
├── shared_config.py    Model ID, prompt path, response schema
├── external/
│   └── xml2abc.py      Bundled MusicXML → ABC converter (pure Python)
└── prompts/
    └── prompt_v1.2.md  System prompt used for all 554 annotations
validation/
├── evaluation_result.md   Human validation study results (N=50)
└── human_ratings.xlsx     Raw per-piece ratings from the validation study
```

### Annotation schema

Each JSON file in `annotations/` covers one piece and has the following top-level fields:

| Field | Type | Description |
|---|---|---|
| `Tile` | string | Piece title |
| `IsAdaptive` | bool | True if the piece is designed for adaptive/looping playback |
| `IsStinger` | bool | True if the piece is a short one-shot cue |
| `Function` | array | Function-level segmentation (coarser) |
| `Section` | array | Section-level segmentation (finer) |

Each `Function` entry: `{ "BarRange": [start, end], "Function": "<tag>", "Inference": "<rationale>" }`  
Each `Section` entry: `{ "BarRange": [start, end], "Function": "<tag>", "Section": "<letter>", "Inference": "<rationale>" }`

**Function tags:** `In` (Intro), `Lp` (Loop), `Tr` (Transition), `Br` (Bridge), `Ou` (Outro), `St` (Stinger)  

### Human validation

Independent expert annotation of 50 randomly sampled pieces, scored against the primary annotations:

| Metric | Agreement |
|---|---|
| Function WQS | 95.77% |
| Section WQS | 97.68% |

WQS = Weighted Quality Score (partial-credit boundary agreement). See `validation/evaluation_result.md` for full methodology.

### Reproducing the annotations from source

Raw transcriptions are © NinSheetMusic contributors and are not redistributed. To reproduce the annotations:

1. Download the MUS files from [NinSheetMusic](https://www.ninsheetmusic.org) using the `url_mus` links in `dataset/pieces.csv`. Convert MUS → MXL using **Finale's built-in File → Export → MusicXML batch conversion** (Finale 26+).
2. Convert MXL → normalised ABC: `python pipeline/mxl_to_abc.py <MXL_DIR> -o <ABC_DIR>` then `python pipeline/reformat_abc.py <ABC_DIR> -o <RABC_DIR>` (`xml2abc.py` is bundled in `pipeline/external/`; no additional tools required).
3. Run the annotation pipeline: `python pipeline/single_api.py --abc_dir <RABC_DIR> --output_dir annotations/` (requires `GOOGLE_API_KEY` env var with Gemini API access).  
   **Note:** `shared_config.py` uses `gemini-3.1-pro-preview`, which is a versioned preview model and may be retired. Check the [Google AI model list](https://ai.google.dev/gemini-api/docs/models) for the current equivalent and update `MODEL_ID` in `pipeline/shared_config.py` if needed.

---

## Part 2 — Section-Pair Dataset

### What's included

```
dataset/
├── pieces.csv          554 pieces with NinSheetMusic IDs and download URLs
└── pairs.csv           3,304 within-piece section pairs with similarity scores
pipeline/
└── compound_metric.py  compound_sim metric (standalone, CLI-runnable)
```

### pieces.csv

| Column | Description |
|---|---|
| `piece_id` | Five-digit ID matching annotation filename (e.g. `00001`) |
| `title` | Piece title |
| `ninsheetmusic_id` | NinSheetMusic numeric ID |
| `url_pdf` | PDF download link |
| `url_mid` | MIDI download link |
| `url_mus` | MUS (Finale) download link |

### pairs.csv

| Column            | Description                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------- |
| `pair_id`         | Unique pair index                                                                            |
| `piece_id`        | Five-digit piece ID matching annotation filename (e.g. `00001`)                              |
| `split`           | `train` / `val` / `test` (70/15/15 piece-level stratified split)                             |
| `context_section` | Section identifier for the context (e.g. `00001_s0_A_11-28`)                                 |
| `target_section`  | Section identifier for the target (e.g. `00001_s1_B_29-39`)                                  |
| `context_ntokens` | Token count of the context section                                                           |
| `target_ntokens`  | Token count of the target section                                                            |
| `compound_sim`     | `compound_sim` between context and target (0–1, higher = more similar); pre-computed from MIDI token arrays, provided as-is |
| `sim_bucket`      | Similarity bucket: `sim:high` / `sim:mid` / `sim:low` (tertile of within-piece distribution) |

**3,304 pairs** from **334 pieces** (39 excluded: 27 double-piano, 12 mixed-instrument).  
Pairs are within-piece only (same piece, different sections).

Section identifiers follow the pattern `{piece_id}_s{index}_{label}_{start}-{end}`, where `start`–`end` are bar numbers matching the `BarRange` fields in `annotations/`. You can reconstruct any section directly from the corresponding annotation JSON and the source transcription.

### compound_sim metric

`compound_sim = 0.4·chroma + 0.3·duration + 0.1·register + 0.1·density`

All components are normalised to [0, 1]. Chroma similarity is transposition-invariant (best key shift over 12 semitones). The `.npy` files use Moonbeam compound-token format (480 TPQ, normalised to 120 BPM); token columns are `[time, duration, octave, pitch_class, ...]`. See `pipeline/compound_metric.py` for the standalone implementation.

### Pairing logic

All directed within-piece section pairs are included (i.e. A→B and B→A are separate rows). Sections with fewer than 4 tokens and pieces with double-piano or mixed-instrument arrangements are excluded. `compound_sim` is computed from Moonbeam compound-token arrays; see `pipeline/compound_metric.py` for the full implementation. Similarity buckets are tertiles of the within-piece `compound_sim` distribution (thresholds: `sim:high` ≥ 0.78, `sim:mid` 0.60–0.78, `sim:low` < 0.60). The train/val/test split (70/15/15) is stratified by section count at the version-group level to prevent data leakage across arrangement variants.

---

## Contact

Shangxuan Luo — s.luo@qmul.ac.uk

---

## Licence

Annotations and pipeline code: **CC BY 4.0**  
Source transcriptions (MXL/MUS): © NinSheetMusic contributors — not included in this repo.

If you use this dataset, please cite:

```bibtex
@inproceedings{structurellama2026,
  title     = {Structure-Aware Game Music Generation with Similarity-Bucket Conditioning},
  author    = {[to be added after review]},
  booktitle = {Proceedings of the 27th International Society for Music Information Retrieval Conference (ISMIR)},
  year      = {2026},
  note      = {Paper and code links to be added after review}
}
```