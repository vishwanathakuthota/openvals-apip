def ai_reality_label(score: float) -> str:
    if score >= 90:
        return "Elite"
    if score >= 70:
        return "Strong"
    if score >= 50:
        return "Emerging"
    if score >= 30:
        return "Speculative"
    return "Cash Burn Zone"


def calculate_ai_reality_index(
    roi: float,
    revenue_growth: float,
    margin: float,
    adoption: float,
) -> dict[str, float | str]:
    score = roi * 0.4 + revenue_growth * 0.3 + margin * 0.2 + adoption * 0.1
    return {"score": round(score, 2), "label": ai_reality_label(score)}
