from sqlalchemy.orm import Session
from api.database.table_models import Tool
from api.models import tool as schemas


def create_tool(db: Session, tool: schemas.ToolCreate):
    db_tool = Tool(**tool.dict())
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool


def get_tool(db: Session, tool_id):
    return db.query(Tool).filter(Tool.id == tool_id).first()


def get_tool_by_name(db: Session, name: str):
    return db.query(Tool).filter(Tool.name == name).first()


def get_all_tools(db: Session):
    return db.query(Tool).all()
