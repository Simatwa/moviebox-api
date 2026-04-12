
# moviebox-api

**Unofficial Python wrapper for moviebox.ph**  
Search, discover, download, and stream movies & TV series with subtitles

[![PyPI version](https://badge.fury.io/py/moviebox-api.svg)](https://pypi.org/project/moviebox-api)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/moviebox-api)](https://pypi.org/project/moviebox-api)
![Coverage](https://raw.githubusercontent.com/Simatwa/moviebox-api/refs/heads/main/assets/coverage.svg)
[![PyPI - License](https://img.shields.io/pypi/l/moviebox-api)](https://pypi.org/project/moviebox-api)
[![Downloads](https://pepy.tech/badge/moviebox-api)](https://pepy.tech/project/moviebox-api)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


## Features

* **Multi-Version Support** : Access multiple API versions (`v1`, `v2`, `v3`) for different provider services
* **Download Movies & TV Series** : High-quality downloads with multiple resolution options
* **Subtitle Support** : Download subtitles in multiple languages
* **Direct Streaming** : Stream via MPV or VLC without downloading (CLI only)
* **Faster Downloads** : Up to 5× faster than standard downloads
* **Async & Sync Support** : Fully asynchronous with synchronous fallback
* **Search & Discovery** : Find movies, trending content, and popular searches
* **Developer-Friendly** : Python API with Pydantic models



## Versions Available

There are 3 versions currently supported, each targeting a distinct API surface of the **Moviebox** provider. They differ in protocol approach, backend endpoint, authentication requirements, and data fidelity.

---

### v1 — Web Scraper + Partial REST-API Client
**Endpoint:** `h5.aoneroom.com`

Operates against the H5 (mobile web) frontend of Moviebox. Combines HTML scraping with partial REST-API interaction, making it suitable for content discovery where structured API access is limited or inconsistent. Scraping logic handles page-rendered data not exposed via JSON endpoints.

- Approach: Hybrid (DOM scraping + REST)
- Target surface: H5 mobile web interface
- Use case: Content listing, metadata extraction from web-rendered pages
- Limitations: Susceptible to markup changes; partial API coverage only

---

### v2 — Pure REST-API Client
**Endpoint:** `h5-api.aoneroom.com`

Targets the dedicated REST-API backend powering the H5 web interface. Eliminates scraping entirely in favor of structured JSON request/response cycles. Provides more stable and predictable data access compared to v1.

- Approach: Pure REST-API
- Target surface: H5 API backend
- Use case: Structured content queries, metadata retrieval, stream resolution
- Advantages over v1: No markup dependency; cleaner response parsing; more reliable

---

### v3 — Android App REST-API Client
**Endpoints:** `api3.aoneroom.com` through `api6.aoneroom.com`

Targets the API cluster used by the native Moviebox Android application. Operates against multiple rotating API subdomains (`api3`–`api6`), reflecting the app's load-balanced backend. Typically exposes higher data fidelity, broader content coverage, and app-exclusive endpoints not available via the H5 surfaces.

- Approach: Pure REST-API
- Target surface: Android app backend (multi-host)
- Use case: Full content catalog access, app-tier stream quality, extended metadata
- Advantages over v1/v2: Wider endpoint coverage; app-grade API access; multi-host failover support


## [Get started](./installation.md)

!!! quote "Disclaimer"
    All videos and pictures on MovieBox are from the Internet, and their copyrights belong to the original creators. We only provide webpage services and do not store, record, or upload any content.

    *moviebox.ph*

<div align=center>

**Long live Moviebox spirit.**
</div>