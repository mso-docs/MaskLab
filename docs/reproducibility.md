# Reproducibility

A study export records dataset/split/protocol hashes, rendered prompts, model ID and available serving revision (or unknown), endpoint identity, timestamps, supported sampling settings, schedule/analysis seeds, attempts, usage/error/cost states and software/scorer versions. Exact reproducibility of the serving backend is not guaranteed; a seed or temperature zero does not establish determinism.

Analysis on frozen stored records should reproduce with the same software/analysis seed. Provider re-execution creates new evidence and may differ. Retain raw final responses separately from extraction/scoring and allow reanalysis only as a new linked version. Never export credentials or private machine configuration.
