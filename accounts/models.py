from django.db import models
from django. contrib. auth.models import BaseUserManager,AbstractUser

# Create your models here.
class MyAccountManager(BaseUserManager):# for admin and user
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError('user must have an email address')
        if not username:
            raise ValueError('user must have an username')
        user=self.model(
            email=self.normalize_email(email),#for lower also and upper case also
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)# encrypted form cant see password
        user.save(using=self.db)
        return user

    def create_superuser(self,first_name,last_name,email,username,password):# admin panel
        user=self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        
        )
        user.is_admin=True
        user.is_staff=True
        user.is_active=True
        user.is_superadmin=True
        user.save(using=self.db)
        return user
class Account(AbstractUser):
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=50)
    username=models.CharField(max_length=30,unique=True)
    email=models.EmailField(max_length=50,unique=True)
    phone_no=models.CharField(max_length=10)

#required

    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_superadmin=models.BooleanField(default=False)

    objects=MyAccountManager()

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username','first_name','last_name']

    def __str__(self):
        return self.email

    def has_perm (self,perm,obj=None):
        return self.is_admin

    def has_module_perms(self,add_label):
        return True

