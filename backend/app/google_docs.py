"""Google Docs fetcher.

Supports two modes:
1. Google Docs REST API via httpx (when OAuth2 credentials are available)
2. Public export endpoint (fallback) - for publicly shared docs
"""

import httpx

from app.google_auth import get_credentials

EXPORT_URL = "https://docs.google.com/document/d/{doc_id}/export?format=txt"
EXPORT_URL_WITH_TAB = (
    "https://docs.google.com/document/d/{doc_id}/export?format=txt&tab={tab}"
)

DOCS_API_URL = "https://docs.googleapis.com/v1/documents/{doc_id}"
DOCS_API_URL_WITH_TABS = (
    "https://docs.googleapis.com/v1/documents/{doc_id}"
    "?includeTabsContent=true"
)


def _extract_text_from_body(body: dict) -> str:
    """Extract plain text from a document body."""
    text_parts: list[str] = []
    content = body.get("content", [])

    for element in content:
        paragraph = element.get("paragraph")
        if not paragraph:
            continue
        for pe in paragraph.get("elements", []):
            text_run = pe.get("textRun")
            if text_run:
                text_parts.append(text_run.get("content", ""))

    return "".join(text_parts)


async def fetch_doc_text(doc_id: str, section: str = "") -> str:
    """Fetch plain text content of a Google Doc.

    Uses Google Docs REST API if OAuth2 credentials are available,
    otherwise falls back to public export endpoint.
    """
    creds = get_credentials()

    if creds:
        return await _fetch_via_api(doc_id, section, creds)

    return await _fetch_via_export(doc_id, section)


async def _fetch_via_api(doc_id: str, section: str, creds: object) -> str:
    """Fetch document text using Google Docs REST API directly."""
    headers = {"Authorization": f"Bearer {creds.token}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        if section:
            url = DOCS_API_URL_WITH_TABS.format(doc_id=doc_id)
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            doc = response.json()

            tabs = doc.get("tabs", [])
            for tab in tabs:
                tab_props = tab.get("tabProperties", {})
                tab_id = tab_props.get("tabId", "")
                if tab_id == section or section in tab_id:
                    tab_body = tab.get("documentTab", {}).get("body", {})
                    return _extract_text_from_body(tab_body)

            body = doc.get("body", {})
            return _extract_text_from_body(body)
        else:
            url = DOCS_API_URL.format(doc_id=doc_id)
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            doc = response.json()
            body = doc.get("body", {})
            return _extract_text_from_body(body)


async def _fetch_via_export(doc_id: str, section: str) -> str:
    """Fetch document text using public export endpoint (fallback)."""
    if section:
        url = EXPORT_URL_WITH_TAB.format(doc_id=doc_id, tab=section)
    else:
        url = EXPORT_URL.format(doc_id=doc_id)

    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
