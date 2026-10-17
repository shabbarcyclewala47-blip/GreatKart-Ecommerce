from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode
from .models import Account


# Create your views here.
def register(request):
    if request.method=='POST':
        f_name=request.POST['first_name']
        l_name=request.POST['last_name']
        email=request.POST['email']
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        phone_no=request.POST['phone_no']

        username=email.split ('@')[0]
        if password!=confirm_password:
            messages.error(request,"password does not match")
            return redirect('register')

        if Account.objects.filter(email=email).exists():
            messages.error(request,"email id already exists")
            return redirect('register')

        if Account.objects.filter(username=username).exists():
            messages.error(request,"username already exists")
            return redirect('register')

        account=Account.objects.create_user(first_name=f_name,last_name=l_name,email=email,password=password,username=username)
        account.phone_no=phone_no
        account.is_active=True
        account.save()
        messages.success(request,"u have successfully registered, you can login ")
        return redirect('loggedin')

    return render(request, 'accounts/register.html')



def loggedin(request):

    if request.method=='POST':
       email=request.POST['email']
       password=request.POST['password']
       user=authenticate(email=email,password=password)
       if user is not None:  #jab user ke credentials database se match ho jayege
           login(request,user)
           messages.success(request,"you have successsfully loggedin")
           return redirect('index')
       else:
           messages.error(request,"please enter correct credentials")
           return redirect('loggedin')

    return render (request,'accounts/login.html')


def loggedout(request):
    logout(request)
    messages.success(request,"you have successfully logout")
    return redirect('loggedin')


def forgotpassword(request):
    if request.method=='POST':
        email_addr=request.POST['email']
        if Account.objects.filter(email=email_addr).exists(): 
            user=Account.objects.get(email__exact=email_addr)
            cuurent_site=get_current_site(request)  #127.0.0.1
            mail_subject='please activate your account' # email ma subject ma ause
            message=render_to_string('accounts/account_verification_email.html',{  #render to string matlab link ne string ma kari desa
                
                'user':user,   # key=column name
                'domain':cuurent_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),

            })
            to_email=email_addr
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,"password reset email has sent")
            return redirect('loggedin')
        else:
            messages.error(request,"Account doesn't exist")
            return redirect("forgotpassword")

    return render (request,'accounts/forgotpassword.html')


def activate(request,uid,token):
    try:
        uid=urlsafe_base64_decode(uid).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'please reset ur passsword')
        return redirect("resetpassword")
    else:
        messages.error(request,'this link has been expired')
        return redirect(request,'forgotpassword')



def resetpassword(request):
    if request.method=='POST':
        newpassword=request.POST['new_password']
        confirmpassword=request.POST['confirm_password']
        if newpassword==confirmpassword:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(newpassword)
            user.save()
            messages.success(request,'password has been set')
            return redirect ('loggedin')
        else:
            messages.error(request,"new password and confirm password didn't match")
            return redirect('resetpassword')

    return render(request,'accounts/resetpassword.html')

    





       
           


