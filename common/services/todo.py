from common.repositories.factory import RepositoryFactory, RepoType
from common.models.todo import Todo
from datetime import datetime, timezone
from typing import List

class TodoError(Exception):
    pass

class TodoNotFoundError(TodoError):
    pass

class UnauthorizedError(TodoError):
    pass

class ConcurrentModificationError(TodoError):
    pass

class TodoService:
    def __init__(self, config):
        self.config = config
        self.repo_factory = RepositoryFactory(config)
        self.todo_repo = self.repo_factory.get_repository(RepoType.TODO)
    
    def create_todo(self, todo: Todo) -> Todo:
        return self.todo_repo.save(todo)

    def update_todo(self, todo: Todo, person_id: str) -> Todo:
        if todo.person_id != person_id:
            raise UnauthorizedError("You don't have permission to update this todo")

        return self.todo_repo.save(todo)

    def get_todo_by_id(self, todo_id: str, person_id: str) -> Todo:
        todo = self.todo_repo.get_one({'entity_id': todo_id, 'active': True})
        if not todo:
            raise TodoNotFoundError(f"Todo {todo_id} not found")

        if todo.person_id != person_id:
            raise UnauthorizedError("You don't have permission to access this todo")

        return todo

    def get_todos_by_person_id(self, person_id: str) -> List[Todo]:
        return self.todo_repo.get_many({'person_id': person_id, 'active': True})

    def get_todos_by_person_id_and_status(self, person_id: str, is_completed: bool) -> List[Todo]:
        return self.todo_repo.get_many({'person_id': person_id, 'active': True, 'is_completed': is_completed})

    def update_todo_status(self, todo_id: str, person_id: str, is_completed: bool, version: str) -> Todo:
        todo = self.get_todo_by_id(todo_id, person_id)
        if not todo:
            raise TodoNotFoundError(f"Todo {todo_id} not found")

        if todo.person_id != person_id:
            raise UnauthorizedError("You don't have permission to update this todo")

        if todo.version != version:
            raise ConcurrentModificationError("Todo has been modified by another request")

        todo.is_completed = is_completed
        todo.completed_at = datetime.now(timezone.utc) if is_completed else None
        return self.todo_repo.save(todo)
    
    def delete_todo(self, todo_id: str, person_id: str):
        todo = self.get_todo_by_id(todo_id, person_id)
        if not todo:
            raise TodoNotFoundError(f"Todo {todo_id} not found")

        todo.active = False
        return self.todo_repo.save(todo)
