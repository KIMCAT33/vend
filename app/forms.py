from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import F
from django import forms
from .models import Account


class CreateUserForm(UserCreationForm): # 내장 회원가입 폼을 상속받아서 확장한다.
    email = forms.EmailField(required=True) # 이메일 필드 추가
    name = forms.CharField(required=True) # 이름 필드 추가
    phone = forms.CharField(required=True) # 휴대폰번호 필드 추가
    user_status = forms.ChoiceField(choices=(('1', '벤더스터'), ('2', '자판기 관리자'),('3', '유통업자')))
    
    class Meta:
        model = User
        fields = ("email", "phone", "name", "username", "password")

    def save(self, commit=True): # 저장하는 부분 오버라이딩
        user = super(CreateUserForm, self).save(commit=False) # 본인의 부모를 호출해서 저장하겠다.
        user.email = self.cleaned_data["email"]
        user.is_active = 0
        if commit:
            user.save()
        auth_user_no = user.id
        print(auth_user_no)
        account = Account(Name=self.cleaned_data["name"], PhoneNumber=self.cleaned_data["phone"],
                          IsOwner=self.cleaned_data["user_status"], Auth_User_No_id=auth_user_no)
        account.save()
        return user