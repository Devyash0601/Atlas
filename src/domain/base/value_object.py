"""Base Value Object abstract class enforcing immutability and structural equality."""


class ValueObject:
    """Base immutable value object identified by its attribute values rather than an identity."""

    def __eq__(self, other: object) -> bool:
        """Value objects are equal if they have the exact same class and attributes."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """Hash value object based on its class and attribute items."""
        items = tuple(sorted((k, v) for k, v in self.__dict__.items()))
        return hash((self.__class__, items))

    def __repr__(self) -> str:
        """Represent value object attributes."""
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
