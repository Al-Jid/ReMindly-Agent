from app.core.config import settings


def test_short_budget_less_than_medium():
    short_budget = settings.output_token_budget(
        "short",
        "fast",
    )

    medium_budget = settings.output_token_budget(
        "medium",
        "fast",
    )

    assert short_budget < medium_budget


def test_medium_budget_less_than_detailed():
    medium_budget = settings.output_token_budget(
        "medium",
        "fast",
    )

    detailed_budget = settings.output_token_budget(
        "detailed",
        "fast",
    )

    assert medium_budget < detailed_budget


def test_fast_short_budget_is_capped():
    budget = settings.output_token_budget(
        "short",
        "fast",
    )

    assert budget <= 2400


def test_chunk_budget_does_not_exceed_final_budget():
    for detail_level in [
        "short",
        "medium",
        "detailed",
        "preserve",
    ]:
        chunk_budget = settings.chunk_output_token_budget(
            detail_level,
            "fast",
        )

        final_budget = settings.output_token_budget(
            detail_level,
            "fast",
        )

        assert chunk_budget <= final_budget


def test_parallel_chunks_positive():
    assert settings.MAX_PARALLEL_CHUNKS > 0


def test_fast_single_pass_limit_positive():
    assert settings.FAST_SINGLE_PASS_MAX_CHARS > 0
