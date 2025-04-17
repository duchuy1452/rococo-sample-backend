from flask_restx import Namespace, Resource
from flask import request
from app.helpers.decorators import login_required
from app.helpers.todo_helper import TodoHelper
from common.app_config import config
from common.services.todo import TodoService, TodoNotFoundError, UnauthorizedError, ConcurrentModificationError
from common.models.todo import Todo
import uuid

todo_api = Namespace('todos', description='Todo operations')

@todo_api.route('/')
class TodoList(Resource):
    @login_required()
    def get(self, person):
        """Get list of todos with optional filters"""
        status = request.args.get('status')
        entity_id = person.entity_id

        todo_service = TodoService(config)
        try:
            if status == 'completed':
                todos = todo_service.get_todos_by_person_id_and_status(entity_id, True)
            elif status == 'incomplete':
                todos = todo_service.get_todos_by_person_id_and_status(entity_id, False)
            else:
                todos = todo_service.get_todos_by_person_id(entity_id)
                
            return TodoHelper.format_todos_response(todos)
        except Exception as e:
            return {'error': str(e)}, 500

    @login_required()
    def post(self, person):
        """Create a new todo"""
        data = request.get_json()

        # Validate data
        error = TodoHelper.validate_todo_data(data)
        if error:
            return {'error': error}, 400
            
        # Parse due date
        due_date = TodoHelper.parse_todo_date(data.get('due_date'))

        # Create todo object
        todo = Todo(
            entity_id=str(uuid.uuid4().hex),
            version=str(uuid.uuid4().hex),
            title=data['title'],
            description=data.get('description'),
            due_date=due_date,
            priority=data.get('priority', 0),
            person_id=person.entity_id
        )

        # Save todo
        todo_service = TodoService(config)
        try:
            saved_todo = todo_service.create_todo(todo)
            return TodoHelper.format_todo_response(saved_todo), 201
        except Exception as e:
            return {'error': str(e)}, 500

@todo_api.route('/<string:todo_id>')
class TodoItem(Resource):
    @login_required()
    def put(self, person, todo_id):
        """Update a todo"""
        data = request.get_json()
        todo_service = TodoService(config)
        person_id = person.entity_id
        
        try:
            # Get existing todo
            todo = todo_service.get_todo_by_id(todo_id, person_id)
            
            # Update fields if provided
            if 'title' in data:
                todo.title = data['title']
            if 'description' in data:
                todo.description = data['description']
            if 'priority' in data:
                todo.priority = data['priority']
            if 'due_date' in data:
                todo.due_date = TodoHelper.parse_todo_date(data['due_date'])

            # Update version
            version = todo.version
            todo.previous_version = todo.version
            todo.version = str(uuid.uuid4().hex)

            # Save updates
            updated_todo = todo_service.update_todo(todo, person_id, version)
            return TodoHelper.format_todo_response(updated_todo)

        except TodoNotFoundError:
            return {'error': 'Todo not found'}, 404
        except UnauthorizedError as e:
            return {'error': str(e)}, 403
        except Exception as e:
            return {'error': str(e)}, 500

    @login_required()
    def delete(self, person, todo_id):
        """Delete a todo (soft delete)"""
        todo_service = TodoService(config)
        person_id = person.entity_id
        try:
            todo_service.delete_todo(todo_id, person_id)
            return '', 204
        except TodoNotFoundError:
            return {'error': 'Todo not found'}, 404
        except UnauthorizedError as e:
            return {'error': str(e)}, 403
        except Exception as e:
            return {'error': str(e)}, 500

@todo_api.route('/<string:todo_id>/complete')
class TodoComplete(Resource):
    @login_required()
    def put(self, person, todo_id):
        """Mark a todo as complete or incomplete"""
        data = request.get_json()
        is_completed = data.get('is_completed', True)
        version = data.get('version')
        person_id = person.entity_id
        
        if not version:
            return {'error': 'Version is required'}, 400
        
        todo_service = TodoService(config)
        try:
            todo = todo_service.update_todo_status(todo_id, person_id, is_completed, version)
            return {
                'id': todo.entity_id,
                'is_completed': todo.is_completed,
                'completed_at': todo.completed_at.isoformat() if todo.completed_at else None,
                'version': todo.version
            }
        except TodoNotFoundError:
            return {'error': 'Todo not found'}, 404
        except UnauthorizedError as e:
            return {'error': str(e)}, 403
        except ConcurrentModificationError as e:
            return {'error': str(e)}, 409
        except Exception as e:
            return {'error': str(e)}, 500
