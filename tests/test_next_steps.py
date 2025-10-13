import base64

from services import next_steps


def _encode(content: str) -> dict:
    return {"content": base64.b64encode(content.encode("utf-8")).decode("utf-8")}


def test_fetch_next_steps_prefers_comms_location(mocker):
    mock_get = mocker.patch(
        "services.next_steps.get_file_contents",
        side_effect=[_encode("# comms\n- [ ] task from comms")],
    )

    result = next_steps.fetch_next_steps("owner", "repo", "token")

    assert result == "# comms\n- [ ] task from comms"
    mock_get.assert_called_with("owner", "repo", "comms/NEXT_STEPS.md", "token")
    assert mock_get.call_count == 1


def test_fetch_next_steps_falls_back_to_root_when_comms_missing(mocker):
    mock_get = mocker.patch(
        "services.next_steps.get_file_contents",
        side_effect=[
            None,
            _encode("# root\n- [x] legacy task"),
        ],
    )

    result = next_steps.fetch_next_steps("owner", "repo", "token")

    assert result == "# root\n- [x] legacy task"
    assert mock_get.call_count == 2
    mock_get.assert_called_with("owner", "repo", "NEXT_STEPS.md", "token")


def test_fetch_next_steps_returns_none_when_not_found(mocker):
    mocker.patch(
        "services.next_steps.get_file_contents",
        side_effect=[None, None],
    )

    assert next_steps.fetch_next_steps("owner", "repo", "token") is None
