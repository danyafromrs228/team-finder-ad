from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project


PAGINATION_PAGE_SIZE = 12

STATUS_OPEN = "open"
STATUS_CLOSED = "closed"


def paginate_queryset(request, queryset, page_size=PAGINATION_PAGE_SIZE):
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def projects_list_view(request):
    projects = Project.objects.filter(status=STATUS_OPEN).select_related("owner")
    page_obj = paginate_queryset(request, projects)
    return render(request, "projects/project_list.html", {"page_obj": page_obj})


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        id=project_id
    )
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
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND
        )

    if project.owner == request.user and project.status == STATUS_OPEN:
        project.status = STATUS_CLOSED
        project.save()
        return JsonResponse(
            {"status": "ok", "project_status": STATUS_CLOSED},
            status=HTTPStatus.OK
        )

    return JsonResponse(
        {"status": "error", "message": "Недостаточно прав"},
        status=HTTPStatus.FORBIDDEN
    )


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND
        )

    is_participant = project.participants.filter(id=request.user.id).exists()

    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({
        "status": "ok",
        "participant": not is_participant
    }, status=HTTPStatus.OK)


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND
        )

    is_favorited = request.user.favorites.filter(id=project_id).exists()

    if is_favorited:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)

    return JsonResponse({
        "status": "ok",
        "favorited": not is_favorited
    }, status=HTTPStatus.OK)


@login_required
def favorites_view(request):
    projects = request.user.favorites.select_related("owner").prefetch_related("participants")
    return render(request, "projects/favorite_projects.html", {"projects": projects})
