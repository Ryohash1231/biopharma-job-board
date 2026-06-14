import re

GREENHOUSE_PATTERNS = [
    re.compile(r"(?:boards|job-boards)\.greenhouse\.io/([a-zA-Z0-9_-]+)"),
    re.compile(r"greenhouse\.io/embed/job_board\?for=([a-zA-Z0-9_-]+)"),
]
LEVER_PATTERN = re.compile(r"jobs\.lever\.co/([a-zA-Z0-9_-]+)")


def extract_ats_token(html):
    for pattern in GREENHOUSE_PATTERNS:
        match = pattern.search(html)
        if match:
            return ("greenhouse", match.group(1))

    match = LEVER_PATTERN.search(html)
    if match:
        return ("lever", match.group(1))

    return None
