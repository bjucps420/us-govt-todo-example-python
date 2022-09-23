from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@login_required
@csrf_exempt
def all_status(request):
    return JsonResponse(["Pending", "In Progress", "Complete"], safe=False)


@login_required
@csrf_exempt
def all_type(request):
    return JsonResponse(["Unclassified", "Classified", "Secret", "Top Secret"], safe=False)