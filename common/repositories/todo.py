from common.repositories.base import BaseRepository
from common.models.todo import Todo

class TodoRepository(BaseRepository):
    MODEL = Todo
