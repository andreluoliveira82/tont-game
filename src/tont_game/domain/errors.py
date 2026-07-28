"""Domain-level exceptions.

These represent violations of the game's business rules. Messages are
developer-facing (English); user-facing PT-BR messages belong to the
presentation layer.
"""


class DomainError(Exception):
    """Base class for all domain rule violations."""


class GameConfigurationError(DomainError):
    """Raised when a game is built with an invalid set of briefcases."""


class InvalidBriefcaseNumberError(DomainError):
    """Raised when referencing a briefcase number that does not exist."""


class BriefcaseAlreadyOpenedError(DomainError):
    """Raised when trying to open a briefcase that is already opened."""


class PlayerBriefcaseProtectedError(DomainError):
    """Raised when trying to open the player's briefcase during rounds."""


class RoundLimitExceededError(DomainError):
    """Raised when trying to open more briefcases than the round allows."""


class RoundNotCompleteError(DomainError):
    """Raised when advancing a round before its openings are complete."""


class NoMoreRoundsError(DomainError):
    """Raised when advancing past the last round."""


class InvalidGameStateError(DomainError):
    """Raised when an operation is not allowed in the current game status."""


class BankerStrategyError(DomainError):
    """Raised when the banker strategy receives invalid input or configuration.

    Covers invalid strategy inputs (unknown round, empty remaining values) and
    invalid percentage configuration. It does NOT cover game-flow conditions
    such as an unfinished round or a finished game — those are the concern of
    the ProcessBankerOffer use case (Phase 5).
    """
