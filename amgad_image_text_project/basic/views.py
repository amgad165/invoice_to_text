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
                img.save(f'{filepath}/{request.user.username}.{extension}', format=extension)
        elif type == 'PDF':
            pdf_data = base64.b64decode(data_url.split(',')[1])

                    # write the rendered content to a file
            with open(f'{filepath}/{request.user.username}.pdf', "wb") as f:
                f.write(pdf_data)


        # with open(f'static/{filepath}.{extension}','wb') as fh:
        #     for chunk in image_data.chunks():
        #         fh.write(chunk)
        # df = img_to_df(f'static/{file.name}')
        # print(df.head())     
        # data = json.load(open(fr'result_files/{request.user.username}.json'))
        # return render(request, 'img_result.html', {"df": df})

        return JsonResponse({'result': 'success'})

@login_required
def img_to_table_view(request):
        extension = request.session['extension'] 
        file_name = request.user.username 
        filepath = settings.MEDIA_ROOT
        if default_storage.exists(f'{filepath}/{file_name}.{extension}'):
            df = img_to_df(f'{filepath}/{file_name}.{extension}')
            default_storage.delete(f'{filepath}/{file_name}.{extension}')  
            return render(request, 'img_result.html', {"df": df})
        else:
            print("failed")

            return render(request,'img_result.html',{"error": 'failed'})

@login_required
def img_to_text_view(request):
        extension = request.session['extension'] 
        file_name = request.user.username
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
        file_name = request.user.username
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
    
def login(request):
    if request.user.is_authenticated:
        return redirect("main_page")
    elif request.method == "POST":
        email = request.POST.get('email')
        email = email.split('@')[0]
        print('emmm',email)
        password = request.POST.get('password')
        user = authenticate(username=email.split('@')[0], password=password)
        
        if user is not None:
            auth_login(request,user)
            messages.error(request, 'Login Success')
            return redirect("main_page")
        else:
            messages.error(request, 'Login Failed')


            
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('/')

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['verify-password']
        if password != password2:
            messages.info(request, 'password didn"t match')
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email Taken')
            return redirect('signup')
        else:
            user = User.objects.create_user(
                email=email, username=email.split('@')[0], password=password)
            user.save()
            return redirect('login')
    return render(request, 'signup.html')