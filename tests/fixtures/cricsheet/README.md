# Cricsheet test excerpts

These two JSON files come from the official Cricsheet archives downloaded on
2026-10-03. `provenance.json` records the archive URLs and SHA-256 hashes of the
original, untrimmed JSON files.

The original `info` and `meta` objects are unchanged. Only the first over of the
first innings is retained. These are test excerpts, **not complete match scores**
and must never be included in the production data directory.

- `1043989.json`: women's T20I; retained over = 3 runs, 6 legal deliveries.
- `1000887.json`: men's ODI; retained over = 1 run, 7 delivery events, 6 legal deliveries.

Source: [Cricsheet](https://cricsheet.org/),
[JSON format](https://cricsheet.org/format/json/),
[downloads](https://cricsheet.org/downloads/).
The downloaded match archives contained README notices but no explicit licence
file. The Cricsheet **Register** explicitly uses ODC-BY 1.0; do not assume this
establishes the licence of all match archives. Full raw archives are not committed.
