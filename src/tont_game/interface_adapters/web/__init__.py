"""Web interface adapter: drives the existing use cases for a browser client.

It contains no business rules. It orchestrates the same use cases the CLI uses,
holds a game session per player in memory, and serializes the game **facts** as
plain data (the contract) for a front-end to dramatize. All truth stays in the
domain/application layers.
"""
