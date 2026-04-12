"""
### v3 - Android App REST-API Client

**Endpoints:** `api3.aoneroom.com` through `api6.aoneroom.com`

Targets the API cluster used by the native Moviebox Android application.
Operates against multiple rotating API subdomains (`api3`-`api6`), reflecting the
app's load-balanced backend.

Typically exposes higher data fidelity, broader
content coverage, and app-exclusive endpoints not available via the H5 surfaces.

- Approach: Pure REST-API
- Target surface: Android app backend (multi-host)
- Use case: Full content catalog access, app-tier stream quality, extended
 metadata
- Advantages over v1/v2: Wider endpoint coverage; app-grade API access;
multi-host failover support
"""

import logging

logger = logging.getLogger(__name__)
