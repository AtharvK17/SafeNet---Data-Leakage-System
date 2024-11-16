#Project views
from sqlite3 import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Accounts.models import Profile
from .models import Project
from Accounts.models import UserActivityLog
from .forms import ProjectForm


@login_required
def create_project(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)  # Create project instance without saving
            project.creator = request.user  # Set the creator to the logged-in user
            try:
                project.save()  # Attempt to save the project
                form.save_m2m()  # Save many-to-many relationships (assigned users)
                messages.success(request, 'Project created successfully!')

                # Log the creation of the project
                UserActivityLog.objects.create(
                    user=request.user,
                    action='Created project',
                    details=f'User {request.user.username} created project {project.name}.'
                )

                return redirect('project_list')  # Replace with your success URL
            except IntegrityError as e:
                messages.error(request, f'Error saving project: {e}')
        else:
            messages.error(request, 'Invalid form submission.')
            print(form.errors)  # Print form errors for debugging
    else:
        form = ProjectForm()

    return render(request, 'Projects/Create-project.html', {'form': form, 'profile': profile})


@login_required
def project_list(request):
    profile = get_object_or_404(Profile, user=request.user)
    projects = Project.objects.all()  # Fetch all projects
    context = {
        'projects': projects,
        'profile': profile,  # Include profile context
    }
    return render(request, 'Projects/Project.html', context)


@login_required
def edit_project(request, project_id):
    profile = get_object_or_404(Profile, user=request.user)
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()

            # Convert checkbox values to boolean
            profile.email_notifications = request.POST.get('email_notifications') == 'on'
            profile.browser_notifications = request.POST.get('browser_notifications') == 'on'
            profile.app_notifications = request.POST.get('app_notifications') == 'on'
            profile.save()

            messages.success(request, 'Project updated successfully!')

            # Log the update of the project
            UserActivityLog.objects.create(
                user=request.user,
                action='Updated project',
                details=f'User {request.user.username} updated project {project.name}.'
            )

            return redirect('project_list')
        else:
            print(form.errors.as_json())  # Debugging form errors
            messages.error(request, 'Invalid form submission.')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'Projects/Edit-project.html', {
        'form': form,
        'project': project,
        'profile': profile
    })


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project_name = project.name
    project.delete()

    messages.success(request, 'Project deleted successfully!')

    # Log the deletion of the project
    UserActivityLog.objects.create(
        user=request.user,
        action='Deleted project',
        details=f'User {request.user.username} deleted project {project_name}.'
    )

    return redirect('project_list')  # Redirect after deletion
