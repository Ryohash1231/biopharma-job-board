import pytest

from scraper.location_filter import is_bay_area_or_remote


@pytest.mark.parametrize(
    "location",
    [
        "South San Francisco",
        "Redwood City, CA",
        "San Francisco (UCSF)",
        "Emeryville, California; Remote, United States",
        "USA - Carlsbad, CA; USA - South San Francisco, CA",
        "Hybrid, Berkeley, California, United States, Remote",
        "Remote",
        "USA - Remote",
        "Remote (United States)",
        "Remote, United States",
    ],
)
def test_keeps_bay_area_or_us_remote_jobs(location):
    assert is_bay_area_or_remote(location) is True


@pytest.mark.parametrize(
    "location",
    [
        "Boston, Massachusetts, United States",
        "Northern California, United States",
        "Sacramento, California, United States",
        "Los Angeles, California, United States",
        "Various Locations",
        "Remote (Japan)",
        "Remote (UK)",
        "APAC - Remote",
        "",
    ],
)
def test_drops_jobs_outside_bay_area_and_non_us_remote(location):
    assert is_bay_area_or_remote(location) is False
