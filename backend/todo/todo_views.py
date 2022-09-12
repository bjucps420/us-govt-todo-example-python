from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from .fusion_auth_service import get_roles_for_application, find_by_fusion_auth_user_id
from .models import Todo
from json import loads


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
    if len(todo["title"]) > 255:
        errors.append("title is too long (max 255 characters)")
    if len(todo["description"]) > 2048:
        errors.append("title is too long (max 2048 characters)")
    if todo["type"] not in get_types(request):
        errors.append("you are not permitted to create a todo of that classification")
    if "Aid" not in get_types(request) and todo["status"] != "Pending":
        errors.append("you are not permitted to change the status of a todo")
    return errors


@never_cache
@login_required
def todo_list(request, status):
    search = request.GET.get('search', '')
    groupBy = request.GET.get('groupBy', '')
    groupByDesc = request.GET.get('groupByDesc', '')
    sortBy = request.GET.get('sortBy', 'title')
    sortDesc = bool(request.GET.get('sortDesc', 'false'))
    page = int(request.GET.get('page', 1))
    mustSort = request.GET.get('mustSort', '')
    multiSort = request.GET.get('multiSort', '')
    itemsPerPage = int(request.GET.get('itemsPerPage', '10'))

    todos = Todo.objects.filter(status=translate_status(status), type__in=get_types(request))
    if search != "":
        todos = todos.filter(title__contains=search)
    if sortBy != "":
        if sortDesc:
            todos = todos.order_by("-" + sortBy)
        else:
            todos = todos.order_by(sortBy)
    paginator = Paginator(todos.values("id", "title", "description", "status", "type", "created_by", "updated_by"), itemsPerPage)
    try:
        page = paginator.page(page)
        return JsonResponse({
            "success": True,
            "response": {
                "total": todos.count(),
                "items": list(page.object_list)
            },
        })
    except EmptyPage:
        return JsonResponse({
            "success": True,
            "response": {
                "total": todos.count(),
                "items": []
            },
        })


@never_cache
@login_required
def by_id(request, id):
    try:
        todo = Todo.objects.filter(type__in=get_types(request)).get(id=id)
        return JsonResponse({
            "success": True,
            "response": {
                "title": todo.title,
                "description": todo.description,
                "status": todo.status,
                "type": todo.type,
                "created_by": todo.created_by,
                "updated_by": todo.updated_by,
            },
        })
    except Todo.DoesNotExist:
        return JsonResponse({
            "success": False,
            "errorMessage": "Todo not found",
        })


@never_cache
@login_required
def create(request):
    if request.user.has_perm("Aid"):
        return JsonResponse({
            "success": False,
            "errorMessage": "You are not permitted to access this action",
        })
    body = loads(request.body)
    if "id" not in body or body["id"] is None:
        errors = validate(request, body)
        if len(errors) == 0:
            todo = Todo.objects.create(
                title=body["title"],
                description=body["description"],
                status=body["status"],
                type=body["type"],
                created_by=get_email(request)
            )
            return JsonResponse({
                "success": True,
                "response": {
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "type": todo.type,
                },
            })
        else:
            return JsonResponse({
                "success": False,
                "errorMessage": ", ".join(errors),
            })
    return JsonResponse({
        "success": False,
        "errorMessage": "cannot update todo via create",
    })


@never_cache
@permission_required('Aid')
def update(request):
    body = loads(request.body)
    try:
        todo = Todo.objects.filter(type__in=get_types(request)).get(id=body["id"])
        errors = validate(request, body)
        if len(errors) == 0:
            todo.title = body["title"]
            todo.description = body["description"]
            todo.status = body["status"]
            todo.type = body["type"]
            todo.updated_by = get_email(request)
            todo.save()
            return JsonResponse({
                "success": True,
                "response": {
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "type": todo.type,
                },
            })
        else:
            return JsonResponse({
                "success": False,
                "errorMessage": ", ".join(errors),
            })
    except Todo.DoesNotExist:
        return JsonResponse({
            "success": True,
            "response": {},
        })


@never_cache
@permission_required('Aid')
def delete(request):
    body = loads(request.body)
    try:
        Todo.objects.filter(type__in=get_types(request)).get(id=body["id"]).delete()
    except Todo.DoesNotExist:
        pass
    return JsonResponse({
        "success": True,
    })
