from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator, EmptyPage
from .fusion_auth_service import get_roles_for_application, find_by_fusion_auth_user_id
from .models import Todo
from .api import TodoSchema, APIResponseTodoListSchema, APIResponseBoolSchema, APIResponseTodoSchema
from ninja import Router


router = Router()


def translate_status(status):
    if status == "PENDING":
        return "Pending"
    if status == "IN_PROGRESS":
        return "In Progress"
    if status == "COMPLETE":
        return "Complete"


def get_email(request):
    return find_by_fusion_auth_user_id(request.user.username)["email"]


def get_roles(request):
    return get_roles_for_application(request.user.username)


def get_types(request):
    roles = get_roles(request)
    types = []
    if "Aid" in roles or "Top Secret" in roles:
        types.append("Top Secret")
    if "Aid" in roles or "Secret" in roles or "Top Secret" in roles:
        types.append("Secret")
    if "Aid" in roles or "Classified" in roles or "Secret" in roles or "Top Secret" in roles:
        types.append("Classified")
    types.append("Unclassified")
    return types


def validate(request, todo):
    errors = []
    if len(todo.title) > 255:
        errors.append("title is too long (max 255 characters)")
    if len(todo.description) > 2048:
        errors.append("title is too long (max 2048 characters)")
    if todo.type not in get_types(request):
        errors.append("you are not permitted to create a todo of that classification")
    if "Aid" not in get_types(request) and todo.status != "Pending":
        errors.append("you are not permitted to change the status of a todo")
    return errors


@router.get("list/{status}", response=APIResponseTodoListSchema)
@login_required
def todo_list(request, status: str, search: str = "", groupBy: str = "", groupByDesc: str = "", sortBy: str = "title", sortDesc: str = "false", page: int = 1, mustSort: str = "", multiSort: str = "", itemsPerPage: int = 10):
    todos = Todo.objects.filter(status=translate_status(status), type__in=get_types(request))
    if search != "":
        todos = todos.filter(title__contains=search)
    if sortBy != "":
        if sortDesc:
            todos = todos.order_by("-" + sortBy)
        else:
            todos = todos.order_by(sortBy)
    paginator = Paginator(todos, itemsPerPage)
    try:
        page = paginator.page(page)
        return {"success": True, "response": {"total": todos.count(), "items": list(page.object_list)}}
    except EmptyPage:
        return {"success": True, "response": {"total": todos.count(), "items": []}}


@router.post("create", response=APIResponseTodoSchema)
@login_required
def create(request, data: TodoSchema):
    if request.user.has_perm("Aid"):
        return {"success": False, "errorMessage": "You are not permitted to access this action"}
    if data.id is None:
        errors = validate(request, data)
        if len(errors) == 0:
            todo = Todo.objects.create(
                title=data.title,
                description=data.description,
                status=data.status,
                type=data.type,
                created_by=get_email(request)
            )
            return {"success": True, "response": todo}
        else:
            return {"success": False, "errorMessage": ", ".join(errors)}
    return {"success": False, "errorMessage": "cannot update todo via create"}


@router.post("update", response=APIResponseTodoSchema)
@login_required
@permission_required('Aid')
def update(request, data: TodoSchema):
    try:
        todo = Todo.objects.filter(type__in=get_types(request)).get(id=data.id)
        errors = validate(request, data)
        if len(errors) == 0:
            todo.title = data.title
            todo.description = data.description
            todo.status = data.status
            todo.type = data.type
            todo.updated_by = get_email(request)
            todo.save()
            return {"success": True, "response": todo}
        else:
            return {"success": False, "errorMessage": ", ".join(errors)}
    except Todo.DoesNotExist:
        return {"success": False, "errorMessage": "Todo not found"}


@router.post("delete", response=APIResponseBoolSchema)
@login_required
@permission_required('Aid')
def delete(request, data: TodoSchema):
    try:
        Todo.objects.filter(type__in=get_types(request)).get(id=data.id).delete()
    except Todo.DoesNotExist:
        pass
    return {"success": True, "response": True}


@router.get("{identifier}", response=APIResponseTodoSchema)
@login_required
def by_id(request, identifier: int):
    try:
        todo = Todo.objects.filter(type__in=get_types(request)).get(id=identifier)
        return {"success": True, "response": todo}
    except Todo.DoesNotExist:
        return {"success": False, "errorMessage": "Todo not found"}
