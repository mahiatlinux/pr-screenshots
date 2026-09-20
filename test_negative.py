import pytest
from pathlib import Path
def test_validate_resolves_the_hf_seed_endpoint_like_jobs(monkeypatch):
    pytest.importorskip("fastapi")
    backend_root = Path.cwd() / "studio/backend"
    monkeypatch.syspath_prepend(str(backend_root))
    monkeypatch.setenv("HF_ENDPOINT", "http://127.0.0.1:9700")

    from models.data_recipe import RecipePayload
    from routes.data_recipe import validate as validate_module

    seen = {}
    monkeypatch.setattr(validate_module, "validate_recipe", lambda recipe: seen.update(recipe))

    response = validate_module.validate(
        RecipePayload(
            recipe = {
                "seed_config": {
                    "source": {
                        "seed_type": "hf",
                        "path": "datasets/a/b/**/*.parquet",
                        "endpoint": None,
                    }
                },
                "columns": [{"column_type": "expression", "name": "x", "expr": "{{ q }}"}],
            }
        )
    )

    assert response.valid is True
    assert seen["seed_config"]["source"]["endpoint"] == "http://127.0.0.1:9700"
