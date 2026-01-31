import base64

from services import features


def _encode(content: str) -> dict:
    return {"content": base64.b64encode(content.encode("utf-8")).decode("utf-8")}


def test_fetch_features_loads_from_comms_location(mocker):
    mock_get = mocker.patch(
        "services.features.get_file_contents",
        return_value=_encode("# Features\n- [ ] feature from comms"),
    )

    result = features.fetch_features("owner", "repo", "token")

    assert result == "# Features\n- [ ] feature from comms"
    mock_get.assert_called_with("owner", "repo", "comms/FEATURES.md", "token")
    assert mock_get.call_count == 1


def test_fetch_features_returns_none_when_not_found(mocker):
    mocker.patch(
        "services.features.get_file_contents",
        return_value=None,
    )

    assert features.fetch_features("owner", "repo", "token") is None


def test_parse_features_extracts_checkboxes():
    md = """# My App

A description here.

## Features
- [x] User authentication
- [ ] Export to CSV
- [x] Dashboard

## Data
- [ ] Offline mode
"""
    doc = features.parse_features(md, "user/repo")

    assert doc.repo_full_name == "user/repo"
    assert len(doc.features) == 4
    assert doc.features[0].text == "User authentication"
    assert doc.features[0].delivered is True
    assert doc.features[0].section == "Features"
    assert doc.features[1].text == "Export to CSV"
    assert doc.features[1].delivered is False
    assert doc.features[3].section == "Data"


def test_parse_features_handles_no_checkboxes():
    md = """# My App

Just a description, no checkboxes.
"""
    doc = features.parse_features(md, "user/repo")

    assert doc.repo_full_name == "user/repo"
    assert len(doc.features) == 0
    assert doc.raw_markdown == md


def test_summarize_features_counts_correctly():
    feature_list = [
        features.FeatureItem(text="A", delivered=True, section=None),
        features.FeatureItem(text="B", delivered=False, section=None),
        features.FeatureItem(text="C", delivered=True, section=None),
        features.FeatureItem(text="D", delivered=False, section=None),
    ]

    not_delivered, delivered = features.summarize_features(feature_list)

    assert not_delivered == 2
    assert delivered == 2


def test_summarize_features_handles_empty_list():
    not_delivered, delivered = features.summarize_features([])

    assert not_delivered == 0
    assert delivered == 0
