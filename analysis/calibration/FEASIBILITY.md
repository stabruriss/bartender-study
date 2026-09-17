# Feasibility check for exact-sample hunk derivation

Date: 2026-09-16. Status: **bounded read-only extraction complete; result
review pending**.

The Zenodo replication package for Xu et al. (record
`10.5281/zenodo.21186464`) was downloaded and its `rq3_merge_replay_full.csv`
was inspected. It has 747 rows and includes `stratum`, `repo`, `prA`, `prB`,
agent labels and replay labels. The package README documents 716 evaluable
pairs and 31 unavailable pairs. It does not include head OIDs, merge-base OIDs,
or final-diff hunk counts.

The authenticated GitHub API was queried read-only for three representative
rows (one clean and one content-conflict pair among them). Each available PR
returned a head OID, base OID, changed-file count and commit count. The API
rate-limit endpoint reported 5,000 core requests remaining at the check. This
establishes that the planned roughly 1,500 metadata requests are technically
possible with the current credentials. It does not establish that every
historical PR ref remains fetchable.

The completed extraction did the following for every one of the 747 rows:

1. record the row key (`repo`, `prA`, `prB`, `stratum`, `label`);
2. query and record the current head OIDs and base OIDs for both PRs;
3. fetch the two PR heads and compute their merge base with a pinned Git/diff
   version and documented rename, binary and whitespace rules;
4. count final-diff hunks for both clean and conflict rows, while retaining
   unavailable rows separately;
5. record whether the OIDs are historical or only currently retrievable.

The package does not contain the frozen replay OIDs, so the output is called
current-retrievable-subset sensitivity positioning. It is not an exact
reproduction or an empirical calibration. The approved extractor was
read-only, retained only pair keys, conflict-scope flags, OIDs and hunk/file
counts, and did not run the Bartender simulation. It produced 715 count rows,
preserved 31 source-unavailable rows, and recorded one new current 404. The
747-key mapping is complete, and no API/fetched-head OID drift was observed.
Scientific use remains on hold until the row mapping, failures, distributions
and inversion table receive second-eye review.
