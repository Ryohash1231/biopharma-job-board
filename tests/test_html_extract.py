import json
from pathlib import Path
from unittest.mock import MagicMock

from scraper.html_extract import fetch_html_jobs, _clean_html, _extract_json_array

SAMPLE_HTML = Path(__file__).parent.joinpath(
    "fixtures", "sample_careers_page.html"
).read_text()

CLAUDE_RESPONSE_TEXT = json.dumps([
    {
        "title": "Scientist II, Cell Line Engineering",
        "location": "San Mateo, CA",
        "url": "https://example.com/en/jobs/527616",
    },
    {
        "title": "Director/Senior Director, Antibody Discovery",
        "location": "San Mateo, CA",
        "url": "https://example.com/en/jobs/484931",
    },
])


def test_clean_html_removes_script_tags():
    cleaned = _clean_html(SAMPLE_HTML)
    assert "<script>" not in cleaned
    assert "Scientist II" in cleaned


def test_extract_json_array_handles_markdown_fences():
    text = f"```json\n{CLAUDE_RESPONSE_TEXT}\n```"
    result = _extract_json_array(text)
    assert result[0]["title"] == "Scientist II, Cell Line Engineering"


def test_fetch_html_jobs(requests_mock):
    requests_mock.get("https://example.com/careers", text=SAMPLE_HTML)

    mock_block = MagicMock()
    mock_block.text = CLAUDE_RESPONSE_TEXT
    mock_message = MagicMock()
    mock_message.content = [mock_block]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    jobs = fetch_html_jobs("BigHat Biosciences", "https://example.com/careers", client=mock_client)

    assert jobs == [
        {
            "company": "BigHat Biosciences",
            "title": "Scientist II, Cell Line Engineering",
            "location": "San Mateo, CA",
            "url": "https://example.com/en/jobs/527616",
        },
        {
            "company": "BigHat Biosciences",
            "title": "Director/Senior Director, Antibody Discovery",
            "location": "San Mateo, CA",
            "url": "https://example.com/en/jobs/484931",
        },
    ]
