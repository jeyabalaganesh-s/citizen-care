from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def complaint_list(request):
    return render(request, 'complaints/complaint_list.html')