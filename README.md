# GenAI Python Downloads Tracking

This repository tracks PyPI download statistics and adoption trends for OpenTelemetry Generative AI Python instrumentation packages across different repository sources.

## Repository Contents

*   **[`adoption_charts.md`](adoption_charts.md)**: Main user-facing dashboard displaying adoption and comparison charts.
*   **[`pypi_downloads.json`](pypi_downloads.json)**: The JSON database storing the historical and weekly download statistics.
*   **[`scripts/`](scripts/)**:
    *   [`generate_pypi_downloads.py`](scripts/generate_pypi_downloads.py): Python script that queries PyPI Stats APIs with a robust self-seeding fallback cache to prevent rate-limiting failures.
    *   [`generate_svg_charts.py`](scripts/generate_svg_charts.py): Dynamic chart generator that renders custom SVG visualizations and writes the markdown dashboard.
*   **[`.github/workflows/update_downloads.yml`](.github/workflows/update_downloads.yml)**: The GitHub Actions workflow automating the execution.

## Automated Updates

The data collection and chart rendering are fully automated via a GitHub Actions workflow that runs **weekly on Mondays at 00:00 UTC**.

When executed:
1. It downloads PyPI recent download statistics for all monitored packages.
2. If the API rate limits the execution, it safely falls back to the last recorded value in `pypi_downloads.json`.
3. It updates all SVG charts with precise value labels and updates the run date on the dashboard.
4. It automatically commits and pushes all updated files back to this repository.

## Local Execution

To run the data collection and chart generation locally:

```bash
# Fetch latest PyPI downloads
python3 scripts/generate_pypi_downloads.py

# Update the charts and markdown dashboard
python3 scripts/generate_svg_charts.py
```

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
