from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required
def all_status(request):
    return JsonResponse(["Pending", "In Progress", "Complete"], safe=False)


@login_required
def all_type(request):
    return JsonResponse(["Unclassified", "Classified", "Secret", "Top Secret"], safe=False)