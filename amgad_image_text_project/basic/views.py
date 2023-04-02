from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
import json
from .utilities import *
import base64
import tempfile
import io 
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.contrib import  messages
from django.contrib.auth.models import User
import os
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate ,logout
from django.views.generic import CreateView
from django.urls import reverse_lazy
from . import forms
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm

# Create your views here.
def home(request):
    return render(request, 'index.html')

@login_required
def main_page(request):
    return render(request, 'main.html')


@login_required
def upload_file(request):
    if request.method == "POST":
        # file = request.FILES.get("doc_file")
        type = request.POST.get('type')
        
        data_url = request.POST.get('image_data')
        extension = data_url.split(';')[0].split('/')[-1]

        request.session['extension'] = extension 
        filename = 'image'
        request.session['filename'] = filename
        filepath = settings.MEDIA_ROOT
        if type == 'image':
            image_data = base64.b64decode(data_url.split(',')[1])
            # Create a Pillow Image object from the image data and format
            with Image.open(io.BytesIO(image_data)) as img:

                # Save the processed image in the original format

                # filepath = os.path.join(settings.MEDIA_URL, filename)
                
                # Save the image in the original format
                img.save(f'{filepath}/{request.user.email}.{extension}', format=extension)
        elif type == 'PDF':
            pdf_data = base64.b64decode(data_url.split(',')[1])

                    # write the rendered content to a file
            with open(f'{filepath}/{request.user.email}.pdf', "wb") as f:
                f.write(pdf_data)


        return JsonResponse({'result': 'success'})

@login_required
def img_to_table_view(request):
        extension = request.session['extension'] 
        file_name = request.user.email 
        filepath = settings.MEDIA_ROOT
        if default_storage.exists(f'{filepath}/{file_name}.{extension}'):

            try:
                text = img_to_text(f'{filepath}/{file_name}.{extension}')
                default_storage.delete(f'{filepath}/{file_name}.{extension}')                 
                if search_for_bank(text):
                    df = extract_bank_df(text)
                    
                else:
                    df = extract_invoice_df(text)

                return render(request, 'img_result.html', {"df": df})
            except:
                   
                 return redirect('error_message')


        else:
            print("failed")

            return render(request,'img_result.html',{"error": 'failed'})

@login_required
def img_to_text_view(request):
        extension = request.session['extension'] 
        file_name = request.user.email
        filepath = settings.MEDIA_ROOT
        if default_storage.exists(f'{filepath}/{file_name}.{extension}'):
            text = img_to_text(f'{filepath}/{file_name}.{extension}')
            default_storage.delete(f'{filepath}/{file_name}.{extension}')    
            return render(request, 'img_text.html', {"text": text})
        else:
            print("failed")

            return render(request,'img_text.html',{"error": 'failed'})                 


@login_required
def pdf_to_text_view(request):
        extension = request.session['extension'] 
        file_name = request.user.email
        filepath = settings.MEDIA_ROOT
        if default_storage.exists(f'{filepath}/{file_name}.{extension}'):
 
            text = pdf_to_text(f'{filepath}/{file_name}.pdf')
            default_storage.delete(f'{filepath}/{file_name}.{extension}')    
            return render(request, 'pdf_text.html', {"text": text})
        else:
            print("failed")

            return render(request,'pdf_text.html',{"error": 'failed'})                 



@login_required
def download_text(request):
    print('hello')
    if request.method == "POST":
        
        # file = request.FILES.get("doc_file")
        text_val = request.POST.get('text_val')
     

    
        response = HttpResponse(text_val, content_type='application/text charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="result.txt"'
        return response
    


def logout_user(request):
    logout(request)
    return redirect('/')

class SignUp(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy("login")

def error_message(request):

    return render(request,'error_message.html')                 