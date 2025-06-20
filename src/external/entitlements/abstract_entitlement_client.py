from abc import ABC, abstractmethod

from src.domain.models.entitlement import Entitlement


class AbstractEntitlementClient(ABC):
    """
    Abstract base class defining the interface for entitlement clients.
    This abstraction allows for easy swapping of entitlement providers.
    """

    @abstractmethod
    def get_entitlement_value(self, subject_id: str, feature_key: str) -> Entitlement:
        """
        Get the entitlement value for a subject and feature.

        Args:
            subject_id: The ID of the subject.
            feature_key: The feature key to check.

        Returns:
            The entitlement value as an Entitlement object.
        """
        pass
