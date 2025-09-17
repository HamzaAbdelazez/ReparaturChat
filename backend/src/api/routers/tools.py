from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.config.db import get_db
from api.models import tool as schemas
from api.database.repository import tool as repository
import uuid

router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
)

@router.post("/", response_model=schemas.ToolRead)
def create_tool(tool: schemas.ToolCreate, db: Session = Depends(get_db)):
    db_tool = repository.get_tool_by_name(db, tool.name)
    if db_tool:
        raise HTTPException(status_code=400, detail="Tool already exists")
    return repository.create_tool(db, tool)


@router.get("/{tool_id}", response_model=schemas.ToolRead)
def get_tool(tool_id: uuid.UUID, db: Session = Depends(get_db)):
    tool = repository.get_tool(db, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.get("/", response_model=list[schemas.ToolRead])
def get_tools(db: Session = Depends(get_db)):
    return repository.get_all_tools(db)
