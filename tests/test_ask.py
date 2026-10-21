from types import SimpleNamespace

from app import ask as ask_module


def _install_fake_client(monkeypatch, response):
    class FakeModels:
        def generate_content(self, *, model, contents):
            assert model == ask_module.MODEL
            assert contents == "question"
            return response

    class FakeClient:
        def __init__(self, *, api_key):
            assert api_key == "test-key"
            self.models = FakeModels()

    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        text="answer",
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=7),
    )
    _install_fake_client(monkeypatch, response)

    assert ask_module.ask("question") == "answer"
    assert capsys.readouterr().out == "[tokens] input: 12, output: 7\n"


def test_ask_reports_unavailable_usage_metadata(monkeypatch, capsys):
    response = SimpleNamespace(text="answer", usage_metadata=None)
    _install_fake_client(monkeypatch, response)

    assert ask_module.ask("question") == "answer"
    assert capsys.readouterr().out == "[tokens] usage metadata unavailable\n"
