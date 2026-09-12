# Manuscript source package

`arxiv/arxiv-source-draft.tar.gz` contains twelve flat files: `main.tex`,
`main.bbl`, `references.bib`, the unmodified Springer Nature class and
bibliography style, and `Fig1.pdf` through `Fig7.pdf`. The editable source is
also present in `arxiv/source/`. `arxiv/MANIFEST.json` records every checksum.
Only listed files enter the archive; build PDFs, logs, auxiliary state and
editor files are excluded.

The package contains the complete text and appendix, seven figures, seven
numbered tables and fourteen references. Author, affiliation and four factual
declarations remain explicit placeholders. This is a reviewable source draft,
not a completed submission.

## Compile and inspect

As checked on 12 September 2026, arXiv offers TeX Live 2025 by default, using
its 3 August 2025 package state; it also offers TeX Live 2023.
[arXiv environment documentation](https://info.arxiv.org/help/faq/texlive.html).

The supplied package was compiled three times with PDFLaTeX from a separate
TeX Live 2025 installation using that dated package archive. The `.bbl` was
supplied; no BibTeX run, network request or shell escape was required during
compilation. See `arxiv/TEXLIVE2025_CHECK.json` for input hashes, versions,
page/reference checks and remaining spacing notices. This is a local native
build, not a run on arXiv's service.

Extract the source archive into a new empty directory, then run three times:

```sh
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -recorder main.tex
```

The class loads `epstopdf`, which reports that shell escape is disabled; all
seven supplied figures are already PDF, so no conversion is needed. Retain
the compiled `.bbl` in the upload. arXiv does not run BibTeX automatically.
[arXiv TeX submission instructions](https://info.arxiv.org/help/submit_tex.html).

After filling metadata and declarations, rebuild and inspect the package,
select **TeX Live 2025 / pdflatex** in arXiv, and inspect the service-generated
preview before final submission. Template files retain their upstream notices.

## Regenerate the package

From the repository root, pass an already compiled flat manuscript directory:

```sh
python3 release/prepare_arxiv.py --source-dir path/to/compiled-flat-manuscript
```

The packager copies source and assets; it computes no scientific result.
Its archive uses fixed member metadata and contains no local filesystem paths.
Re-run the compilation and release-content checks after a source change.

## Citation, reuse and raw data

`drafts/CITATION.cff` passes the CFF 1.2.0 schema but retains an explicit author
placeholder. `drafts/LICENSE` separates original code (MIT) from data and
generated figures (CC BY 4.0); it preserves third-party template and whitepaper
notices. Neither draft is active release metadata. Complete those fields and
place the final versions at repository root before publication.

The source repository includes raw archive hashes, not the archive volumes.
`RAW_ARCHIVES.json` records retained parts and null download URLs until the
execution machine uploads them. Source publication can precede that upload;
full raw-history reproduction from public downloads cannot. Aggregate-to-figure
reproduction is available from the included data and analysis scripts.
