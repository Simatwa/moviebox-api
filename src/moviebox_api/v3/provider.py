

from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable

import httpx
from pydantic import ValidationError

from moviebox_api.v3.constants import (
    SUBJECT_TYPE_SERIES,
    USER_AGENT,
)
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models import (
    Episode,
    ExtractorLink,
    LoadResponse,
    ResourceDetector,
    SearchResult,
    Season,
    SeasonData,
    Stream,
    StreamData,
    SubjectData,
)
from moviebox_api.v3.urls import HOST_POOL
from moviebox_api.v3.utils import (
    collect_urls_from_json,
    extract_subject_id,
    first_text,
    is_likely_playable,
    is_series_trailer,
    is_trailer_content,
    movie_candidate_score,
    series_candidate_score,
)
from moviebox_api.v3.web_scraper import fetch_web_candidates

logger = logging.getLogger(__name__)

LinkCallback = Callable[[ExtractorLink], Awaitable[None] | None]


class MovieBoxProvider:
    """
    Async provider that surfaces search, detail, season, and playback
    data from the MovieBox / OneRoom API.
    """

    NAME = "MovieBox"

    def __init__(
        self,
        host_pool: list[str] = HOST_POOL,
        timeout: float = 20.0,
        lang: str = "ta",
    ) -> None:
        self._lang = lang
        self._http = MovieBoxHttpClient(host_pool=host_pool, timeout=timeout)

    async def __aenter__(self) -> MovieBoxProvider:
        await self._http.__aenter__()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self._http.__aexit__(*args)

    def _cover_url(self, data: dict) -> str | None:
        """Extract the best available cover image URL from a raw subject dict."""

        def _url(node: object) -> str | None:
            if isinstance(node, dict):
                return node.get("url")
            if isinstance(node, str):
                return node
            return None

        return first_text(
            _url(data.get("cover")),
            _url(data.get("poster")),
            _url(data.get("stills")),
            (data.get("trailer") or {}).get("cover", {}).get("url")
            if isinstance(data.get("trailer"), dict)
            else None,
            _url(data.get("coverVertical")),
            _url(data.get("coverHorizontal")),
            _url(data.get("landscape")),
        )

    def _default_stream_headers(
        self, cookie: str | None = None
    ) -> dict[str, str]:
        headers: dict[str, str] = {
            "User-Agent": USER_AGENT,
            "Referer": self._http.active_base,
            "Origin": self._http.active_base,
            "Accept": "*/*",
        }
        if cookie:
            headers["Cookie"] = cookie
        return headers

    async def get_main_page(self, page: int = 1, tab_id: int = 0) -> list[dict]:
        """
        Return home-page sections as ``[{"title": str, "items": [SearchResult]}]``.
        """
        path = f"/wefeed-mobile-bff/tab-operating?page={page}&tabId={tab_id}&version="
        _, response = await self._http.get(path, include_play_mode=True)

        def _parse_subject(s: dict) -> SearchResult | None:
            sid = s.get("subjectId")
            title = s.get("title")
            if not sid or not title:
                return None
            cover_node = s.get("cover")
            cover_url = (
                cover_node.get("url") if isinstance(cover_node, dict) else None
            )
            stype = s.get("subjectType", 1)
            return SearchResult(
                title=title,
                subject_id=sid,
                subject_type=stype,
                cover_url=cover_url,
            )

        sections: list[dict] = []
        try:
            root = json.loads(response.text)
            for section in root.get("data", {}).get("items", []):
                raw_title = section.get("title", "")
                title = (
                    "🔥Top Picks" if raw_title.lower() == "banner" else raw_title
                )
                stype = section.get("type", "")
                media_list: list[SearchResult] = []

                if stype == "BANNER":
                    for b in (section.get("banner") or {}).get("banners", []):
                        r = _parse_subject(b.get("subject") or {})
                        if r:
                            media_list.append(r)
                elif stype == "SUBJECTS_MOVIE":
                    for sub in section.get("subjects") or []:
                        r = _parse_subject(sub)
                        if r:
                            media_list.append(r)
                elif stype == "CUSTOM":
                    for item in (section.get("customData") or {}).get(
                        "items", []
                    ):
                        r = _parse_subject(item.get("subject") or {})
                        if r:
                            media_list.append(r)

                if title and media_list:
                    sections.append({"title": title, "items": media_list})
        except Exception:
            logger.exception("Failed to parse main page response")

        return sections

    async def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        subject_type: int = 0,
    ) -> list[SearchResult]:
        body = json.dumps(
            {
                "page": page,
                "perPage": per_page,
                "keyword": query,
                "subjectType": subject_type,
            }
        )
        _, response = await self._http.post(
            "/wefeed-mobile-bff/subject-api/search/v2", body
        )

        results: list[SearchResult] = []
        try:
            root = json.loads(response.text)
            """
            with open("search_results.json", "w") as fh:
                json.dump(root, fh, indent=4)
            """
            for result in root.get("data", {}).get("results", []):
                for subject in result.get("subjects", []):
                    sid = subject.get("subjectId")
                    title = subject.get("title")
                    if not sid or not title:
                        continue
                    cover_node = subject.get("cover")
                    cover_url = (
                        cover_node.get("url")
                        if isinstance(cover_node, dict)
                        else None
                    )
                    stype = subject.get("subjectType", 1)
                    results.append(
                        SearchResult(
                            title=title,
                            subject_id=sid,
                            subject_type=stype,
                            cover_url=cover_url,
                        )
                    )
        except Exception:
            logger.exception("Failed to parse search response")

        return results

    async def load(self, url_or_id: str) -> LoadResponse | None:
        subject_id = extract_subject_id(url_or_id)
        _, response = await self._http.get(
            f"/wefeed-mobile-bff/subject-api/get?subjectId={subject_id}"
        )

        if not response.text:
            logger.error("Empty response for subject %s", subject_id)
            return None

        try:
            root = json.loads(response.text)
            """
            with open("movie_details.json", "w") as fh:
                json.dump(
                    root, fh, indent=4
                )
            """
        except json.JSONDecodeError:
            logger.exception("Bad JSON for subject %s", subject_id)
            return None

        raw_data: dict = root.get("data") or {}
        if not raw_data:
            return None

        # Validate with Pydantic – unknown fields are silently ignored
        try:
            subject = SubjectData.model_validate(raw_data)
        except ValidationError:
            logger.exception(
                "Pydantic validation failed for subject %s", subject_id
            )
            return None

        cover = self._cover_url(raw_data)
        episodes: list[Episode] = []

        if subject.subject_type == SUBJECT_TYPE_SERIES:
            episodes = await self._load_episodes(subject_id, cover)

        return LoadResponse(
            title=subject.title or "Unknown",
            subject_id=subject_id,
            subject_type=subject.subject_type or 1,
            cover_url=cover,
            description=subject.description,
            year=subject.release_year,
            tags=subject.tag_list,
            episodes=episodes,
        )

    async def _load_episodes(
        self, subject_id: str, fallback_cover: str | None
    ) -> list[Episode]:
        episodes: list[Episode] = []
        try:
            _, resp = await self._http.get(
                f"/wefeed-mobile-bff/subject-api/season-info?subjectId={subject_id}"
            )
            if resp.status_code != 200 or not resp.text:
                raise ValueError("Bad season response")

            root = json.loads(resp.text)
            season_data = SeasonData.model_validate(root.get("data") or {})

            for season in season_data.seasons:
                se = season.se or 1
                max_ep = season.max_ep or 1
                season_cover = (
                    season.cover.url if season.cover else None
                ) or fallback_cover

                for ep in range(1, max_ep + 1):
                    episodes.append(
                        Episode(
                            subject_id=subject_id,
                            season=se,
                            episode=ep,
                            name=f"S{se:02d}E{ep:02d}",
                            poster_url=season_cover,
                        )
                    )
        except Exception:
            logger.exception("Failed to load seasons for %s", subject_id)

        if not episodes:
            episodes.append(
                Episode(
                    subject_id=subject_id,
                    season=1,
                    episode=1,
                    name="Episode 1",
                    poster_url=fallback_cover,
                )
            )

        return episodes

    async def load_links(
        self,
        data: str,
        callback: LinkCallback | None = None,
    ) -> list[ExtractorLink]:
        """
        Resolve playback links for a movie or episode.

        *data* format:
        * Movie:   ``"<subject_id>"``
        * Episode: ``"<subject_id>|<season>|<episode>"``

        Mirrors the Kotlin fallback chain:
        1. Resource detectors from subject detail
        2. play-info streams
        3. /resource endpoint
        4. Web-API scraping (last resort)
        """
        parts = data.split("|")
        is_series = len(parts) > 1
        subject_id = extract_subject_id(parts[0])
        season = (
            max(int(parts[1]), 1) if len(parts) > 1 and parts[1].isdigit() else 0
        )
        episode = (
            max(int(parts[2]), 1) if len(parts) > 2 and parts[2].isdigit() else 0
        )

        emitted: set[str] = set()
        collected: list[ExtractorLink] = []

        async def emit(
            url: str, display_res: str = "Unknown", cookie: str | None = None
        ) -> bool:
            if not url or url in emitted:
                return False
            if url.startswith("magnet:") or url.endswith(".torrent"):
                return False
            if is_series and is_series_trailer(url):
                return False

            clean = url.strip().replace(" ", "%20")
            emitted.add(clean)

            if not is_likely_playable(clean):
                return False

            is_m3u8 = ".m3u8" in clean.lower()
            link = ExtractorLink(
                source=self.NAME,
                name=f"{self.NAME} ({display_res})",
                url=clean,
                is_m3u8=is_m3u8,
                headers=self._default_stream_headers(cookie),
                cookie=cookie,
            )
            collected.append(link)
            if callback:
                result = callback(link)
                if hasattr(result, "__await__"):
                    await result  # type: ignore[union-attr]
            return True

        # Seed runtime bearer token
        try:
            await self._http.get(
                f"/wefeed-mobile-bff/subject-api/get?subjectId={subject_id}",
                include_play_mode=True,
            )
        except Exception:
            pass

        has_links = False

        # 1. Resource detectors
        has_links = await self._links_from_detail(
            subject_id, season, episode, is_series, emit
        )
        if has_links:
            return collected

        # 2. play-info streams
        has_links = await self._links_from_play_info(
            subject_id, season, episode, emit
        )
        if has_links:
            return collected

        # 3. /resource endpoint
        has_links = await self._links_from_resource(
            subject_id, season, episode, emit
        )
        if has_links:
            return collected

        # 4. Web scraping fallback
        await self._links_from_web(subject_id, season, episode, is_series, emit)
        return collected

    async def _links_from_detail(
        self,
        subject_id: str,
        season: int,
        episode: int,
        is_series: bool,
        emit: LinkCallback,
    ) -> bool:
        has = False
        try:
            _, resp = await self._http.get(
                f"/wefeed-mobile-bff/subject-api/get?subjectId={subject_id}",
                include_play_mode=True,
            )

            if not resp.text:
                return False

            root = json.loads(resp.text)
            raw_data: dict = root.get("data") or {}
            subject = SubjectData.model_validate(raw_data)

            for det in subject.resource_detectors:
                # Detector-level direct link
                if det.direct_link:
                    ok = await emit(det.direct_link, "Resource")
                    if ok:
                        has = True

                # Per-resolution links filtered by season/episode
                for item in det.resolution_list:
                    if item.se and item.se > 0 and item.se != season:
                        continue
                    if item.ep and item.ep > 0 and item.ep != episode:
                        continue
                    link = item.playback_url
                    if link:
                        res = str(item.resolution or item.title or "Resource")
                        ok = await emit(link, res)
                        if ok:
                            has = True

            # Detail page URL through extractor routing
            detail_page = raw_data.get("detailUrl")
            if detail_page:
                ok = await emit(detail_page, "Page")
                if ok:
                    has = True

            # Trailer fallback – movies only
            if not is_series:
                trailer_url = raw_data.get("trailer") or {}
                if isinstance(trailer_url, dict):
                    trailer_url = (trailer_url.get("VideoAddress") or {}).get(
                        "url"
                    )
                else:
                    trailer_url = None
                if trailer_url:
                    ok = await emit(trailer_url, "Trailer")
                    if ok:
                        has = True

        except Exception:
            logger.exception("_links_from_detail failed for %s", subject_id)

        return has

    async def _links_from_play_info(
        self,
        subject_id: str,
        season: int,
        episode: int,
        emit: LinkCallback,
    ) -> bool:
        has = False
        try:
            _, resp = await self._http.get(
                f"/wefeed-mobile-bff/subject-api/play-info?subjectId={subject_id}&se={season}&ep={episode}",
                include_play_mode=True,
            )
            if not resp.text:
                return False

            root = json.loads(resp.text)
            stream_data = StreamData.model_validate(root.get("data") or {})

            for stream in stream_data.streams:
                if not stream.url:
                    continue
                ok = await emit(stream.url, stream.label, stream.sign_cookie)
                if ok:
                    has = True
        except Exception:
            logger.exception("_links_from_play_info failed for %s", subject_id)

        return has

    async def _links_from_resource(
        self,
        subject_id: str,
        season: int,
        episode: int,
        emit: LinkCallback,
    ) -> bool:
        has = False
        try:
            _, resp = await self._http.get(
                f"/wefeed-mobile-bff/subject-api/resource?subjectId={subject_id}&se={season}&ep={episode}",
                include_play_mode=True,
            )
            if not resp.text:
                return False

            root = json.loads(resp.text)
            data: dict = root.get("data") or {}

            direct = data.get("resourceLink") or data.get("downloadUrl")
            if direct:
                ok = await emit(direct, "Resource")
                if ok:
                    has = True

            for item in data.get("resources") or []:
                link = (
                    item.get("downloadUrl")
                    or item.get("resourceLink")
                    or item.get("url")
                )
                if link:
                    res = (
                        item.get("resolution")
                        or item.get("resolutions")
                        or item.get("title")
                        or "Resource"
                    )
                    ok = await emit(link, str(res))
                    if ok:
                        has = True
        except Exception:
            logger.exception("_links_from_resource failed for %s", subject_id)

        return has

    async def _links_from_web(
        self,
        subject_id: str,
        season: int,
        episode: int,
        is_series: bool,
        emit: LinkCallback,
    ) -> bool:
        has = False
        try:
            assert self._http._client is not None
            candidates = await fetch_web_candidates(
                subject_id, self._http._client
            )

            if is_series:
                candidates.sort(
                    key=lambda u: series_candidate_score(u, season, episode),
                    reverse=True,
                )
            else:
                candidates.sort(key=movie_candidate_score, reverse=True)

            for candidate in candidates[:40]:
                if is_series and is_trailer_content(candidate):
                    continue
                ok = await emit(candidate, "WebFallback")
                if ok:
                    has = True
        except Exception:
            logger.exception("_links_from_web failed for %s", subject_id)

        return has
