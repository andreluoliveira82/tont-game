"""Interface adapters: convert between the outside world and the application.

This layer contains no business rules. It orchestrates the existing use cases
and formats/reads data for presentation. Only this layer (and above) performs
I/O and localization (PT-BR); the domain and application never print or read.
"""
