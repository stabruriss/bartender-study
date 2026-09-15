# Reproduction package release inventory

Preparation only; the repository remains private. This checklist does not
authorize publication, a new repository, a new study run, or data changes.
The existing study and its fixed application observations have been accepted.
The final manuscript and publication metadata are being prepared separately.

| Component | Repository-relative location | State |
|---|---|---|
| Model and aggregation code | `bartender_sim/`, `handoff.py`, `tests/` | Present; original execution and revised verification versions are retained in history. |
| Pinned execution environment | `.python-version`, `requirements.lock`, `RUNBOOK.md` | CPython 3.12.4; standard-library study runtime. |
| Approved parameters and seeds | `configs/study-draft.json`; execution copies in `deliverables/study-01/config.json` and `cells.json` | 990 cells; seeds 1000–1029; parameter digest below. |
| All cell aggregates and paired contrasts | `deliverables/study-01/summary.csv`, `paired-differences.csv` | Original 34,650 metric rows and 11,010 paired rows, unchanged. |
| Analysis code, exact plotting dependencies and all result figures | `analysis/` | Four manuscript result figures, complete tables, 41 supplementary figure pages, coordinate provenance, independent verification and the analysis adjustment record. |
| Two explanatory diagrams and editable sources | `release/figures/` | Original scripts, shared style, dependency list, PDF and SVG copies. |
| Execution and verification provenance | `RUN_APPROVAL.json`, `REVALIDATION_APPROVAL.json`, `deliverables/study-01/`, `validation/` | Original HOLD preserved; separately approved verify-02 PASS and independent maintainer acceptance retained. |
| Application conformance | `RUNBOOK-CONFORMANCE.md`, `CONFORMANCE_APPROVAL.json`, `deliverables/conformance-01/` | Eight fixed fixtures, sixteen requests; v0.1.10 and explicit scope limits. |
| Raw archive index, checksums and downloads | `deliverables/study-01/artifact-index.json`; `release/RAW_ARCHIVES.json` | Four public archive parts downloaded independently on a second machine; all part hashes and the concatenated archive hash match. See `release/RAW_DOWNLOAD_VERIFICATION.json`. |
| Deployment dataset and methods | `release/deployment/deployment-records.json`, `METHODS.md` | Unchanged upstream delivery, exact hashes below. Descriptive, incomplete retained record; no overall reliability estimate. |
| Public source audit | `release/SOURCE_AUDIT.md` | Present; integration, automatic trigger and explicit routes anchored to v0.1.10, with tree comparison to the original audit commit. |
| Manuscript source, bibliography and appendix | `release/arxiv/` | Complete text, seven figures and seven tables; twelve-file source draft with compiled `.bbl`. Author, affiliation and declarations remain placeholders. TeX Live 2025 snapshot check is recorded alongside the package. |
| Citation metadata and reuse license | `release/drafts/CITATION.cff`, `release/drafts/LICENSE` | Reviewable drafts: code MIT; data and figures CC BY 4.0. Author/rights-holder fields pending; third-party template notices preserved. Drafts do not activate a repository license. |

## Immutable data bindings

- Parameters: `92dc23981ddd5628761f9c88967a408836c68185110469f7fe82f463155145c0`.
- Original execution protocol: `f7e0530b35d4aae962a2a60cf7c2e3f329aaa06d455871d994b51bbd2c0c5215`.
- Revised verification protocol: `fce2615ee240633100a05d5c3c9f69eeff1c4f4a275668c5abf0081dc5bafc2d`.
- Deployment JSON: `741c98776abfc216beff11f3004a78bb6337f1777c798b365b9d824dee61caec`.
- Deployment methods: `875a678380fe74a37f4cc9dccf4432f357c8387b9db07ba08da84043a3b06f70`.
- Concatenated raw tar: 4,200,591,360 bytes; SHA-256 `2256b0bf734992aa37d1a59f176832f08cce8946fc514dee4f8b87d37e625beb`.

| Archive part | Bytes | SHA-256 |
|---|---:|---|
| `raw.tar.part000` | 1,073,741,824 | `f24ef43b154f961742220d9bdfd871189eb58bce20025cc85505153a5b468b8b` |
| `raw.tar.part001` | 1,073,741,824 | `8610d1edd07731f3cfad36edabf2da848f7d7f20741b844e62a8ed75eff1b199` |
| `raw.tar.part002` | 1,073,741,824 | `6894e702900e389706bc325a517dd0a954071ec04b95f92568710c1c15e9502c` |
| `raw.tar.part003` | 979,365,888 | `ada383eff4ebbb5c8ee521ce09ff796fed6d97fed9381d3696486144612ee8c7` |

Verify the individual parts, concatenate in numeric order, verify the whole tar,
then extract into a new directory. Raw attachments are not in Git. The public
download URLs are in `release/RAW_ARCHIVES.json`. On 15 September 2026 UTC,
the maintainer independently downloaded all fourteen files from the public
folder without authentication, checked every hash and size, and verified the
concatenated raw archive. File-by-file identity within the archive remains
bound to the approved execution-machine collect-only verification. The frozen
research snapshot in that folder predates the upload; current availability is
recorded in this repository, without changing the archived snapshot.

## Remaining release tasks

- Fill final author/affiliation and factual declarations in the manuscript,
  complete the citation and license drafts, and regenerate the seven-figure,
  seven-table source package. Review the arXiv-generated preview before submission.
- Preserve the deployment methods' limits. The frozen deployment source is
  labeled `source-snapshot-01`; its exact relation to a public commit and
  upstream retention of the extraction program remain to be documented.
  The public dataset supports aggregate recomputation, not raw-log extraction.
- Public archive upload and independent download verification are complete.
  Keep `release/RAW_ARCHIVES.json` current if hosting changes; preserve the
  content hashes and the dated download-verification record.
- The three figure/provenance commits after the initial audit were reviewed on
  2026-09-12; see `release/CONTENT_AUDIT.md`. Recheck any subsequent additions.
  No history rewrite or replacement repository is required for the reviewed
  content. The repository remains private; its visibility change is an owner action.
- Replace the repository's old short description at publication with:
  `Reproducible synthetic study of continuous worktree integration and author repair`.
  The old project shorthand is unnecessary for readers; it is not a data issue.

## Reproduction entry points

`RUNBOOK.md` records the original execution. Use `analysis/README.md` to
regenerate figures and tables from the accepted aggregate files without a new
simulation. `validation/review_delivery.py` independently rechecks transferred
delivery evidence. Each procedure states its scope; application observations,
synthetic experiments and deployment records are separate evidence sources.

`release/manifest.json` records the hashes of the additional release documents,
deployment files and explanatory figures. Existing delivery and analysis
manifests continue to identify their respective outputs; raw archive hashes are
listed above and in the original artifact index.
