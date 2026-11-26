"""One installation-selected budget factory for all runtime AI entry points."""
def budget_types(config):
    from .reasoning_budget import TicketBudget, RateCard
    from .nvidia_free_budget import FreeBudget, FreeRateCard
    if config.get('provider')=='nvidia':return FreeBudget,FreeRateCard
    if config.get('provider')=='openrouter':
        from .openrouter_budget import FreeBudget as RouterFree, PaidBudget
        return (RouterFree,FreeRateCard) if config['model'].endswith(':free') else (PaidBudget,RateCard)
    return TicketBudget,RateCard
