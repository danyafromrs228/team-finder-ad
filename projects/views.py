from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Project
from .forms import ProjectForm


def projects_list_view(request):
    projects = Project.objects.filter(status="open")
    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "projects/project_list.html", {"page_obj": page_obj})


def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)  
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user and not request.user.is_staff:
        return redirect("projects:detail", project_id=project.id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner == request.user and project.status == "open":
        project.status = "closed"
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})

    return JsonResponse({"status": "error", "message": "Недостаточно прав"}, status=403)


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_participant = False
    else:
        project.participants.add(request.user)
        is_participant = True

    return JsonResponse({
        "status": "ok",
        "participant": is_participant
    })


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user in project.interested_users.all():
        request.user.favorites.remove(project)
        is_favorited = False
    else:
        request.user.favorites.add(project)
        is_favorited = True

    return JsonResponse({
        "status": "ok",
        "favorited": is_favorited
    })


@login_required
def favorites_view(request):
    projects = request.user.favorites.all()
    return render(request, "projects/favorite_projects.html", {"projects": projects})
