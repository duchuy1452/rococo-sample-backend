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
                
            return {
                'success': True,
                'data': TodoHelper.format_todos_response(todos)
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 200

    @login_required()
    def post(self, person):
        """Create a new todo"""
        data = request.get_json()

        # Validate data
        error = TodoHelper.validate_todo_data(data)
        if error:
            return {
                'success': False,
                'message': error
            }, 200
            
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
            return {
                'success': True,
                'data': TodoHelper.format_todo_response(saved_todo)
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 200

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
            current_version = data.get('version')
            if current_version != todo.version:
                return {
                    'success': False,
                    'message': 'Todo has been modified by another request'
                }, 200

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
            todo.previous_version = todo.version
            todo.version = str(uuid.uuid4().hex)

            # Save updates
            updated_todo = todo_service.update_todo(todo, person_id)
            return {
                'success': True,
                'data': TodoHelper.format_todo_response(updated_todo)
            }, 200

        except TodoNotFoundError:
            return {
                'success': False,
                'message': 'Todo not found'
            }, 200
        except UnauthorizedError as e:
            return {
                'success': False,
                'message': str(e)
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 200

    @login_required()
    def delete(self, person, todo_id):
        """Delete a todo (soft delete)"""
        todo_service = TodoService(config)
        person_id = person.entity_id
        try:
            todo_service.delete_todo(todo_id, person_id)
            return {
                'success': True,
                'message': 'Todo deleted successfully'
            }, 200
        except TodoNotFoundError:
            return {
                'success': False,
                'message': 'Todo not found'
            }, 200
        except UnauthorizedError as e:
            return {
                'success': False,
                'message': str(e)
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 200

@todo_api.route('/<string:todo_id>/complete')
class TodoComplete(Resource):
    @login_required()
    def put(self, person, todo_id):
        """Mark a todo as complete or incomplete"""
        data = request.get_json()
        is_completed = data.get('is_completed', True)
        person_id = person.entity_id
        version = data.get('version')
        
        todo_service = TodoService(config)
        try:
            updated_todo = todo_service.update_todo_status(todo_id, person_id, is_completed, version)
            return {
                'success': True,
                'data': TodoHelper.format_todo_response(updated_todo)
            }, 200
        except TodoNotFoundError:
            return {
                'success': False,
                'message': 'Todo not found'
            }, 200
        except UnauthorizedError as e:
            return {
                'success': False,
                'message': str(e)
            }, 200
        except ConcurrentModificationError as e:
            return {
                'success': False,
                'message': str(e)
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 200
