class LotoUltimeError(Exception):
    """Exception de base du projet."""


class GameNotFoundError(LotoUltimeError):
    """Jeu non trouvé."""


class DrawAlreadyExistsError(LotoUltimeError):
    """Tirage déjà présent en base."""


class InvalidDrawDataError(LotoUltimeError):
    """Données de tirage invalides."""


class InsufficientDataError(LotoUltimeError):
    """Pas assez de données pour le calcul."""


class EngineComputationError(LotoUltimeError):
    """Erreur dans un moteur de calcul."""


class AuthenticationError(LotoUltimeError):
    """Erreur d'authentification."""


class AuthorizationError(LotoUltimeError):
    """Accès non autorisé."""
