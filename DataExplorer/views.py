from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DataFile, DataVisualization
from Accounts.models import UserActivityLog, Profile
from .forms import DataFileForm, DataVisualizationForm
from django.http import JsonResponse
import pandas as pd
import json
from django.contrib import messages
import os
from Dataleakage.detection import AdvancedDataLeakDetector , AnomalyDetector , UserBehaviorAnalyzer  # Adjust import based on your app structure
import logging



@login_required
def data_explorer_home(request):
    files = DataFile.objects.all()  # Fetch all files from the database
    context = {
        'user': request.user,
        'files': files
    }
    return render(request, 'DataExplorer/DataExplorer.html', context)

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = DataFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                data_file = form.save(commit=False)
                original_filename = os.path.splitext(request.FILES['file'].name)[0]
                data_file.title = original_filename
                data_file.file_type = os.path.splitext(request.FILES['file'].name)[1][1:]

                # Set both uploaded_by and user fields
                data_file.uploaded_by = request.user  # User who uploaded the file
                data_file.user = request.user  # Associate the file with the user

                data_file.save()

                # Prepare metadata for the file analysis
                metadata = {
                    'user_id': request.user.id,   # ID of the user uploading the file
                    'filename': data_file.file.name  # Name of the uploaded file
                }

                # Analyze the uploaded file for sensitivity
                detector = AdvancedDataLeakDetector()
                result = detector.analyze_file(data_file.file.path, metadata)

                # Store sensitivity score and findings in the DataFile instance
                data_file.sensitivity_score = result.score  # Assuming you added this field to your model
                data_file.findings = result.findings  # Assuming you added this field to your model
                data_file.save()

                # Log the upload action with details as JSON string
                UserActivityLog.objects.create(
                    user=request.user,
                    action='Uploaded file',
                    details=json.dumps({
                        'message': f'User {request.user.username} uploaded file "{original_filename}" with a sensitivity score of {result.score}.',
                        'file_path': data_file.file.path
                    })
                )

                messages.success(request, f'File "{original_filename}" uploaded successfully with a sensitivity score of {result.score}!')
            except Exception as e:
                messages.error(request, f'Error uploading file: {str(e)}')
        else:
            messages.error(request, 'Please select a valid file to upload.')
    return redirect('data_explorer:data_explorer_home')


@login_required
def delete_file(request, file_id):
    file_to_delete = get_object_or_404(DataFile, id=file_id)
    if request.method == 'POST':
        try:
            file_name = file_to_delete.title
            file_to_delete.delete()

            # Log the delete action with JSON format
            UserActivityLog.objects.create(
                user=request.user,
                action='Deleted file',
                details=json.dumps({
                    'message': f'User {request.user.username} deleted file "{file_name}".',
                    'file_name': file_name
                })
            )

            messages.info(request, f'File "{file_name}" has been deleted.')
        except Exception as e:
            messages.error(request, f'Error deleting file: {str(e)}')
        return redirect('data_explorer:data_explorer_home')
    return render(request, 'DataExplorer/DataExplorer.html')


def load_file_data(file_path):
    """
    Load data from a CSV or Excel file and return it as a DataFrame.
    """
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)  # Load CSV files
    elif file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)  # Load Excel files
    else:
        raise ValueError("Unsupported file type")  # Raise error for unsupported types

@login_required
def view_data(request, file_id):
    data_file = get_object_or_404(DataFile, id=file_id)

    # Load data from the file
    try:
        data = load_file_data(data_file.file.path)

        # Convert data to a format that can be easily displayed in the template
        data_dict = {
            'columns': data.columns.tolist(),
            'rows': data.values.tolist(),
        }

        # Include sensitivity score and findings in the context
        return render(request, 'DataExplorer/ViewData.html', {
            'data_file': data_file,
            'data': data_dict,
            'sensitivity_score': data_file.sensitivity_score,  # Assuming you added this field to your model
            'findings': data_file.findings  # Assuming you added this field to your model
        })
    except ValueError as e:
        return render(request, 'DataExplorer/ViewData.html', {
            'data_file': data_file,
            'error': str(e)
        })
    except Exception as e:
        return render(request, 'DataExplorer/ViewData.html', {
            'data_file': data_file,
            'error': f'Error loading file: {str(e)}'
        })

@login_required
def update_row(request, file_id, row_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    data_file = get_object_or_404(DataFile, id=file_id)

    try:
        # Load the data
        df = load_file_data(data_file.file.path)

        # Update the row with new values
        for column in df.columns:
            if column in request.POST:
                df.at[row_id, column] = request.POST.get(column)

        # Save the updated DataFrame back to the file
        if data_file.file.path.endswith('.csv'):
            df.to_csv(data_file.file.path, index=False)
        else:
            df.to_excel(data_file.file.path, index=False)

        # Log the update action with JSON format
        UserActivityLog.objects.create(
            user=request.user,
            action='Updated row',
            details=json.dumps({
                'message': f'User {request.user.username} updated row {row_id} in file "{data_file.title}".',
                'file_name': data_file.title,
                'row_id': row_id
            })
        )

        # Return the updated values
        updated_row = df.iloc[row_id].to_dict()
        return JsonResponse({
            'success': True,
            'updated_values': updated_row
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def delete_row(request, file_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    data_file = get_object_or_404(DataFile, id=file_id)
    data = json.loads(request.body)
    row_id = data.get('row_id')

    df = load_file_data(data_file.file.path)

    if row_id not in df.index:
        return JsonResponse({'success': False, 'error': 'Row not found'})

    df = df.drop(index=row_id)

    if data_file.file.path.endswith('.csv'):
        df.to_csv(data_file.file.path, index=False)
    else:
        df.to_excel(data_file.file.path, index=False)

    # Log the delete row action with JSON format
    UserActivityLog.objects.create(
        user=request.user,
        action='Deleted row',
        details=json.dumps({
            'message': f'User {request.user.username} deleted row {row_id} in file "{data_file.title}".',
            'file_name': data_file.title,
            'row_id': row_id
        })
    )

    return JsonResponse({'success': True})

@login_required
def create_visualization(request, file_id):
    if request.method == 'POST':
        data_file = get_object_or_404(DataFile, id=file_id)
        form = DataVisualizationForm(request.POST)
        
        if form.is_valid():
            try:
                df = load_file_data(data_file.file.path)
                x_axis = form.cleaned_data['x_axis']
                y_axis = form.cleaned_data['y_axis']
                
                chart_data = {
                    'x': df[x_axis].tolist(),
                    'y': df[y_axis].tolist()
                }
                
                # Save visualization
                visualization = form.save(commit=False)
                visualization.data_file = data_file
                visualization.created_by = request.user
                visualization.configuration = chart_data
                visualization.save()
                
                return JsonResponse({
                    'success': True,
                    'chartData': chart_data
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        return JsonResponse({'success': False, 'error': form.errors})
    
    form = DataVisualizationForm()
    return render(request, 'DataExplorer/Visualize.html', {
        'form': form,
        'data_file': get_object_or_404(DataFile, id=file_id)
    })

@login_required
def get_columns(request, file_id):
    data_file = get_object_or_404(DataFile, id=file_id)
    try:
        df = load_file_data(data_file.file.path)
        columns = df.columns.tolist()
        return JsonResponse(columns, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
