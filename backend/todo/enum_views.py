from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from ninja import Router


router = Router()


@router.get("status/all", response=list)
@login_required
def all_status(request):
    return ["Pending", "In Progress", "Complete"]


@router.get("type/all", response=list)
@login_required
def all_type(request):
    return ["Unclassified", "Classified", "Secret", "Top Secret"]