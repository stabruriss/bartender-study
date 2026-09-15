# Manuscript source package

`arxiv/arxiv-source.tar.gz` contains twelve flat files: `main.tex`,
`main.bbl`, `references.bib`, the unmodified Springer Nature class and
bibliography style, and `Fig1.pdf` through `Fig7.pdf`. The editable source is
also present in `arxiv/source/`. `arxiv/MANIFEST.json` records every checksum.
Only listed files enter the archive; build PDFs, logs, auxiliary state and
editor files are excluded.

The package contains the complete text and appendix, seven figures, seven
numbered tables and fourteen references. Nan Wu is the author, with the
Independent Researcher affiliation, contact email and ORCID. The confirmed
funding, competing-interests and data-availability statements are included.
The author submitted the paper to arXiv on 15 September 2026 UTC and reported
a matching 34-page service-generated preview. The public identifier is pending.
The web-form abstract uses ASCII punctuation; the supplied manuscript source
and figures are unchanged.

## Compile and inspect

As checked on 15 September 2026 UTC, arXiv offers TeX Live 2025 by default, using
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

Select **TeX Live 2025 / pdflatex** in arXiv and inspect the service-generated
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

The repository-root `CITATION.cff` passes the CFF 1.2.0 schema and identifies
Nan Wu. The root `LICENSE` separates original code (MIT) from data and
generated figures (CC BY 4.0), preserving third-party template and whitepaper
notices. These terms do not relicense the manuscript prose. An arXiv identifier
will be added to the citation metadata after announcement.

The source repository includes raw archive hashes, not the archive volumes.
`RAW_ARCHIVES.json` records the four public download URLs and immutable hashes.
`RAW_DOWNLOAD_VERIFICATION.json` records independent anonymous downloads of all
four parts and a matching concatenated archive hash. Archive identity follows
the approved execution-machine verification; this download check did not rerun
the simulation or replace scientific acceptance. Aggregate-to-figure reproduction
is available from the included data and analysis scripts.
