"""Google Docs fetcher.

Fetches document content via the Google Docs export URL (public/shared docs).
For public documents, we use the export endpoint that doesn't require API keys.
"""

import httpx

EXPORT_URL = "https://docs.google.com/document/d/{doc_id}/export?format=txt"
EXPORT_URL_WITH_TAB = "https://docs.google.com/document/d/{doc_id}/export?format=txt&tab={tab}"


async def fetch_doc_text(doc_id: str, section: str = "") -> str:
    """Fetch plain text content of a Google Doc.

    Uses the public export endpoint. The document must be shared
    with "Anyone with the link" permission.
    """
    if section:
        url = EXPORT_URL_WITH_TAB.format(doc_id=doc_id, tab=section)
    else:
        url = EXPORT_URL.format(doc_id=doc_id)

    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
