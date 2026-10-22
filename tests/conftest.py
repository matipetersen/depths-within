"""Most tests exercise what a step does, not the sailing to it, so unless a test is marked `real_nav` the
ship counts as being at the site of every step."""
import pytest


@pytest.fixture(autouse=True)
def _boat_is_at_the_site(request, monkeypatch):
    if request.node.get_closest_marker("real_nav"):
        return
    from dread import nav
    monkeypatch.setattr(nav, "at_site", lambda w: True)
