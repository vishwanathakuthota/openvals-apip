def confidence_label(score: float) -> str:
    if score >= 90:
        return "Verified"
    if score >= 75:
        return "High Confidence"
    if score >= 60:
        return "Medium Confidence"
    if score >= 40:
        return "Low Confidence"
    return "Speculative"


def calculate_confidence(
    source_reliability: float,
    data_freshness: float,
    cross_verification: float,
    methodology_transparency: float,
) -> dict[str, float | str]:
    score = (
        source_reliability * 0.40
        + data_freshness * 0.20
        + cross_verification * 0.25
        + methodology_transparency * 0.15
    )
    return {"score": round(score, 2), "label": confidence_label(score)}
