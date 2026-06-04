PROVIDER_COST_PER_MILLION_TOKENS = {
    "openai": 3.50,
    "anthropic": 4.00,
    "google": 2.75,
    "default": 3.25,
}

MONTHLY_EMPLOYEE_COST = 12_000


def calculate_roi(
    users: int,
    tokens_per_user: int,
    provider: str,
    infrastructure_cost: float,
    employees: int,
    subscription_price: float,
) -> dict[str, float | int]:
    revenue = users * subscription_price
    token_volume_millions = (users * tokens_per_user) / 1_000_000
    provider_rate = PROVIDER_COST_PER_MILLION_TOKENS.get(
        provider.lower(), PROVIDER_COST_PER_MILLION_TOKENS["default"]
    )
    inference_cost = token_volume_millions * provider_rate
    labor_cost = employees * MONTHLY_EMPLOYEE_COST
    cost = infrastructure_cost + inference_cost + labor_cost
    gross_margin = 0.0 if revenue == 0 else (revenue - inference_cost) / revenue
    net_margin = 0.0 if revenue == 0 else (revenue - cost) / revenue
    per_user_variable_cost = (tokens_per_user / 1_000_000) * provider_rate
    contribution_margin = max(subscription_price - per_user_variable_cost, 0.01)
    break_even_users = int((infrastructure_cost + labor_cost) / contribution_margin)
    return {
        "revenue": round(revenue, 2),
        "cost": round(cost, 2),
        "gross_margin": round(gross_margin, 4),
        "net_margin": round(net_margin, 4),
        "break_even_users": break_even_users,
    }
