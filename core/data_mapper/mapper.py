from abc import ABC, abstractmethod


class Mapper[TDomain, TModel, TPydantic](ABC):
    """
    Strict mapper with type safety guarantees
    All child classes must implement all three methods with proper types
    """

    @abstractmethod
    def to_model(self, domain_obj: TDomain) -> TModel:
        """Convert domain object to database model"""
        pass

    @abstractmethod
    def to_domain(self, model_obj: TModel) -> TDomain:
        """Convert database model to domain object"""
        pass

    @abstractmethod
    def to_pydantic(self, obj: TDomain | TModel) -> TPydantic:
        """Convert either domain or db model to Pydantic model"""
        pass


class StaticMapper[TDomain, TModel, TPydantic](ABC):
    """
    Static version with type safety
    """

    @staticmethod
    @abstractmethod
    def to_model(domain_obj: TDomain) -> TModel:
        """Convert domain object to database model"""
        pass

    @staticmethod
    @abstractmethod
    def to_domain(model_obj: TModel) -> TDomain:
        """Convert database model to domain object"""
        pass

    @staticmethod
    @abstractmethod
    def to_pydantic(obj: TDomain | TModel) -> TPydantic:
        """Convert either domain or db model to Pydantic model"""
        pass
