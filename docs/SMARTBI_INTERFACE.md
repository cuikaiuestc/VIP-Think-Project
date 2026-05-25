# SmartBI Interface Boundary

This repository does not include SmartBI DATA CLI implementation or private runtime configuration.

Expected upstream workflow:

1. A controlled external job exports raw SmartBI reports.
2. The external job normalizes approved rows into CSV facts that match `docs/DATA_CONTRACT.md`.
3. The external job writes or updates a registry file with local fact paths.
4. This package reads the registry and generates Markdown / Excel / HTML reports.

Allowed inputs for this package:

- A registry JSON file.
- Local normalized facts referenced by the registry.
- Optional manual material supplement CSV.

Not allowed in this package:

- SmartBI login logic.
- SmartBI export implementation.
- Credential loading.
- Private account configuration.
- Automatic report filter mutation.
- Silent data refresh during report generation.

Production integration must happen outside this sanitized package and must be approved by the project owner.

