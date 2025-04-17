from datetime import datetime
from common.models.todo import Todo
from typing import Dict, List, Optional

class TodoHelper:
    @staticmethod
    def validate_todo_data(data: Dict) -> Optional[str]:
        """Validate todo data and return error message if invalid"""
        if not data.get('title'):
            return 'Title is required'
        return None

    @staticmethod
    def parse_todo_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        try:
            # Try parsing with format YYYY/MM/DD
            return datetime.strptime(date_str, '%Y/%m/%d')
        except ValueError:
            try:
                # Fallback to ISO format
                return datetime.fromisoformat(date_str)
            except ValueError:
                return None

    @staticmethod
    def format_todo_response(todo: Todo) -> Dict:
        """Format todo object to response format"""
        return {
            'id': todo.entity_id,
            'title': todo.title,
            'description': todo.description,
            'is_completed': todo.is_completed,
            'completed_at': todo.completed_at.isoformat() if todo.completed_at else None,
            'due_date': todo.due_date.isoformat() if todo.due_date else None,
            'priority': todo.priority,
            'version': todo.version
        }

    @staticmethod
    def format_todos_response(todos: List[Todo]) -> List[Dict]:
        """Format list of todos to response format"""
        return [TodoHelper.format_todo_response(todo) for todo in todos]
