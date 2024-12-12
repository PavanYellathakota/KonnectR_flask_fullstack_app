# baseObject.py
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

class BaseObject:
    def __init__(self, data: Dict[str, Any] = None):
        """Initialize base object with optional data dictionary"""
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.deleted = False
        self.id = None
        
        if data:
            for key, value in data.items():
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary, excluding None values and private attributes"""
        return {
            key: value 
            for key, value in self.__dict__.items() 
            if value is not None and not key.startswith('_')
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BaseObject':
        """Create object from dictionary"""
        obj = BaseObject()
        for key, value in data.items():
            setattr(obj, key, value)
        return obj

    def validate(self) -> Tuple[bool, str]:
        """Base validation method to be overridden by child classes"""
        return True, ""

    def before_save(self) -> None:
        """Hook called before saving"""
        self.updated_at = datetime.now()

    def after_save(self) -> None:
        """Hook called after saving"""
        pass

    def before_delete(self) -> None:
        """Hook called before deletion"""
        self.updated_at = datetime.now()

    def after_delete(self) -> None:
        """Hook called after deletion"""
        pass

    def mark_deleted(self) -> None:
        """Mark object as deleted (soft delete)"""
        self.before_delete()
        self.deleted = True
        self.updated_at = datetime.now()
        self.after_delete()

    def __repr__(self) -> str:
        """String representation of the object"""
        class_name = self.__class__.__name__
        attributes = [f"{k}={v}" for k, v in self.to_dict().items()]
        return f"{class_name}({', '.join(attributes)})"
