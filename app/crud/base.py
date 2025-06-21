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