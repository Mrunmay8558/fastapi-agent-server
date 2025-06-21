from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from odmantic import AIOEngine, Model, ObjectId
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: An ODMantic model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, engine: AIOEngine, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        try:
            return await engine.find_one(self.model, self.model.id == ObjectId(id))
        except Exception:
            return None

    async def get_multi(
        self, engine: AIOEngine, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination"""
        return await engine.find(self.model, skip=skip, limit=limit)

    async def create(self, engine: AIOEngine, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        return await engine.save(db_obj)

    async def update(
        self,
        engine: AIOEngine,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record"""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        return await engine.save(db_obj)

    async def remove(self, engine: AIOEngine, *, id: Any) -> Optional[ModelType]:
        """Remove a record by ID"""
        obj = await self.get(engine, id)
        if obj:
            await engine.delete(obj)
        return obj

    async def count(self, engine: AIOEngine) -> int:
        """Count total records"""
        results = await engine.find(self.model)
        return len(results)

    async def exists(self, engine: AIOEngine, *, id: Any) -> bool:
        """Check if a record exists"""
        obj = await self.get(engine, id)
        return obj is not None

    async def populate(
        self,
        engine: AIOEngine,
        *,
        obj: ModelType,
        populate_fields: Dict[str, Type[Model]],
        populate_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Populate referenced ObjectIds with actual model data (similar to Mongoose populate)

        Args:
            obj: The model instance to populate
            populate_fields: Dict mapping field names to their model types
                             e.g., {"agent_ids": Agent, "category_id": Category}
            populate_name: Optional name for the populated field
                          (e.g., "agents" for "agent_ids")

        Returns:
            Dictionary with populated fields
        """
        result = obj.dict()

        for field_name, model_class in populate_fields.items():
            if hasattr(obj, field_name):
                field_value = getattr(obj, field_name)

                if field_value is None:
                    continue

                # Handle List[ObjectId] fields
                if isinstance(field_value, list):
                    if field_value:  # Only query if list is not empty
                        populated_data = await engine.find(
                            model_class, model_class.id.in_(field_value)
                        )
                        populated_field_name = populate_name or field_name.replace(
                            "_ids", "s"
                        )
                        result[populated_field_name] = [
                            item.dict() for item in populated_data
                        ]

                # Handle single ObjectId fields
                elif isinstance(field_value, ObjectId):
                    populated_data = await engine.find_one(
                        model_class, model_class.id == field_value
                    )
                    if populated_data:
                        populated_field_name = populate_name or field_name.replace(
                            "_id", ""
                        )
                        result[populated_field_name] = populated_data.dict()

        return result

    async def find_with_populate(
        self,
        engine: AIOEngine,
        *,
        filter_query=None,
        populate_fields: Dict[str, Type[Model]],
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find documents and populate specified fields (like Mongoose find().populate())

        Args:
            filter_query: MongoDB filter query
            populate_fields: Dict mapping field names to their model types
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of populated documents
        """
        # Find the base documents
        if filter_query is not None:
            documents = await engine.find(
                self.model, filter_query, skip=skip, limit=limit
            )
        else:
            documents = await engine.find(self.model, skip=skip, limit=limit)

        # Populate each document
        populated_docs = []
        for doc in documents:
            populated_doc = await self.populate(
                engine, obj=doc, populate_fields=populate_fields
            )
            populated_docs.append(populated_doc)

        return populated_docs

    async def find_one_with_populate(
        self,
        engine: AIOEngine,
        *,
        filter_query,
        populate_fields: Dict[str, Type[Model]]
    ) -> Optional[Dict[str, Any]]:
        """
        Find one document and populate specified fields
        """
        document = await engine.find_one(self.model, filter_query)
        if not document:
            return None

        return await self.populate(
            engine, obj=document, populate_fields=populate_fields
        )
