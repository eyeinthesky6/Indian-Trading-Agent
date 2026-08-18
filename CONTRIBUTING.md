# Contributing

Contributions are welcome, especially from Indian traders, quant researchers, market-data engineers and risk practitioners.

Good contributions improve one of four things:
- freshness/provenance,
- deterministic calculation quality,
- setup/risk discipline,
- reproducible evaluation.

Before opening a PR:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src
```

For a new indicator/setup:
- explain what decision it changes;
- state required data and lookback;
- include failure modes;
- avoid magic thresholds presented as universal truths;
- add tests for deterministic arithmetic.

Do not add broker credentials, live order placement or a fake market-data scraper.
