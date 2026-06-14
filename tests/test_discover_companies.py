import pytest

from scraper.discover_companies import extract_ats_token


@pytest.mark.parametrize(
    "html, expected",
    [
        (
            '<a href="https://job-boards.greenhouse.io/examplebio">Careers</a>',
            ("greenhouse", "examplebio"),
        ),
        (
            '<a href="https://boards.greenhouse.io/examplebio">Careers</a>',
            ("greenhouse", "examplebio"),
        ),
        (
            '<iframe src="https://www.greenhouse.io/embed/job_board?for=examplebio"></iframe>',
            ("greenhouse", "examplebio"),
        ),
        (
            '<a href="https://jobs.lever.co/examplebio">Careers</a>',
            ("lever", "examplebio"),
        ),
        (
            "<html><body>No jobs here</body></html>",
            None,
        ),
        (
            '<a href="https://jobs.lever.co/examplebio">Careers</a>'
            '<a href="https://job-boards.greenhouse.io/examplebio2">Careers</a>',
            ("greenhouse", "examplebio2"),
        ),
    ],
)
def test_extract_ats_token(html, expected):
    assert extract_ats_token(html) == expected
