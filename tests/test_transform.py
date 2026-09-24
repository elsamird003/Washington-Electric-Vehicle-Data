import pandas as pd
import pytest

from src.transform import quality_metrics, top_models


def test_top_models_returns_highest_counts():
    data = pd.DataFrame(
        {
            "Model": [
                "MODEL Y",
                "MODEL Y",
                "MODEL Y",
                "MODEL 3",
                "MODEL 3",
                "LEAF",
                "  ",
                None,
            ]
        }
    )

    result = top_models(data, top_n=2)

    assert list(result["Model"]) == ["MODEL Y", "MODEL 3"]
    assert list(result["count"]) == [3, 2]


def test_top_models_rejects_invalid_n():
    with pytest.raises(ValueError, match="top_n must be at least 1"):
        top_models(pd.DataFrame({"Model": ["MODEL Y"]}), top_n=0)


def test_quality_metrics_include_share():
    data = pd.DataFrame({"Model": ["MODEL Y", "MODEL Y", "LEAF"]})
    counts = top_models(data, top_n=1)
    metrics = quality_metrics(data, counts)

    assert metrics["row_count"] == 3
    assert metrics["distinct_models"] == 2
    assert metrics["top_n"] == 1
    assert metrics["top_n_share"] == pytest.approx(2 / 3)
