import logging
from typing import Type, TypeVar, Generic, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Generic base repository class providing common asynchronous CRUD operations for SQLAlchemy models.

    This repository handles asynchronous database operations using SQLAlchemy's AsyncSession.

    Attributes:
        model (Type[T]): The SQLAlchemy model class associated with this repository.
        db (AsyncSession): The async database session used to perform operations.
    """

    model: Type[T]

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a given async database session.

        Args:
            db (AsyncSession): The asynchronous SQLAlchemy session for database operations.
        """
        self.db = db

    async def get_all(self) -> list[T]:
        """
        Retrieve all records of the model type from the database.

        Returns:
            list[T]: A list of all instances of the model.

        Raises:
            SQLAlchemyError: If a database error occurs during retrieval.
        """
        try:
            result = await self.db.execute(select(self.model))
            return result.scalars().all()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error getting all for {self.model.__name__}: {e}")
            raise e

    async def get_all_by_field(self, field_name: str, field_value: Any) -> list[T]:
        """
        Retrieve all records where a given model field matches a specified value.

        Args:
            field_name (str): The name of the model field to filter on.
            field_value (Any): The value that the field must match.

        Returns:
            list[T]: A list of model instances matching the filter.

        Raises:
            SQLAlchemyError: If a database error occurs during retrieval.
        """
        try:
            result = await self.db.execute(
                select(self.model).filter(getattr(self.model, field_name) == field_value)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error getting all for {self.model.__name__} by {field_name} == {field_value}: {e}")
            raise e

    async def get_first_by_field(self, field_name: str, field_value: Any) -> Optional[T]:
        """
        Retrieve the first record where a given model field matches a specified value.

        Args:
            field_name (str): The name of the model field to filter on.
            field_value (Any): The value that the field must match.

        Returns:
            Optional[T]: The first matching model instance or None if no match is found.

        Raises:
            SQLAlchemyError: If a database error occurs during retrieval.
        """
        try:
            result = await self.db.execute(
                select(self.model).filter(getattr(self.model, field_name) == field_value)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error getting first {self.model.__name__} by {field_name} == {field_value}: {e}")
            raise e

    async def create(self, instance: T) -> T:
        """
        Add a new record to the database.

        Args:
            instance (T): The model instance to add.

        Returns:
            T: The created and refreshed model instance.

        Raises:
            SQLAlchemyError: If a database error occurs during creation.
        """
        try:
            self.db.add(instance)
            await self.db.commit()
            await self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise e

    async def update(self, instance: T, fields: dict[str, Any]) -> T:
        """
        Update fields of an existing model instance and commit changes.

        Args:
            instance (T): The model instance to update.
            fields (dict[str, Any]): A dictionary of fields and their new values.

        Returns:
            T: The updated and refreshed model instance.

        Raises:
            SQLAlchemyError: If a database error occurs during update.
        """
        try:
            for field, value in fields.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)

            await self.db.commit()
            await self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise e

    async def delete(self, instance: T) -> None:
        """
        Delete a model instance from the database.

        Args:
            instance (T): The model instance to delete.

        Raises:
            SQLAlchemyError: If a database error occurs during deletion.
        """
        try:
            await self.db.delete(instance)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {e}")
            raise e
