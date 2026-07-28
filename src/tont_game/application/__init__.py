"""Application layer: use cases that orchestrate the domain.

Use cases coordinate the operational state (GameState) with the factual
history (GameRecord). The rule is: validate/execute the action in the domain
first; only then record the corresponding fact. They contain no presentation
logic and know nothing about infrastructure details beyond injected ports.
"""
