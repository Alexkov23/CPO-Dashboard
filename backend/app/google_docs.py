"""Google Docs fetcher.

Supports two modes:
1. Google Docs REST API via httpx (when OAuth2 credentials are available)
2. Public export endpoint (fallback) - for publicly shared docs

When using the API, list items (numbered lists in Google Docs) are
reconstructed with their numbers so the parser can identify tasks.
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


def _extract_text_from_body(body: dict, lists: dict | None = None) -> str:
    """Extract plain text from a document body.

    For list items, reconstructs numbering from the bullet/lists metadata
    so the parser can correctly identify task numbers.
    Uses a single counter per section (resets on non-list paragraphs)
    because Google Docs may assign different list_ids to visually
    continuous numbered lists.
    """
    text_parts: list[str] = []
    section_counter = 0

    content = body.get("content", [])

    for element in content:
        paragraph = element.get("paragraph")
        if not paragraph:
            continue

        bullet = paragraph.get("bullet")
        para_text = ""
        for pe in paragraph.get("elements", []):
            text_run = pe.get("textRun")
            if text_run:
                para_text += text_run.get("content", "")

        if bullet and lists:
            nesting = bullet.get("nestingLevel", 0)

            if nesting == 0:
                section_counter += 1
                text_parts.append(f"{section_counter}. {para_text}")
            else:
                text_parts.append(para_text)
        else:
            section_counter = 0
            text_parts.append(para_text)

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
                    tab_doc = tab.get("documentTab", {})
                    tab_body = tab_doc.get("body", {})
                    tab_lists = tab_doc.get("lists", {})
                    return _extract_text_from_body(tab_body, tab_lists)

            doc_data = doc.get("body", {})
            doc_lists = doc.get("lists", {})
            return _extract_text_from_body(doc_data, doc_lists)
        else:
            url = DOCS_API_URL.format(doc_id=doc_id)
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            doc = response.json()
            body = doc.get("body", {})
            lists = doc.get("lists", {})
            return _extract_text_from_body(body, lists)


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
