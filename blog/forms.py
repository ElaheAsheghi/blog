from django import forms
from .models import Comment, Post, User, Account
from django.contrib.auth.forms import AuthenticationForm


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد', 'پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش')
    )
    message = forms.CharField(widget=forms.Textarea, required=True)
    name = forms.CharField(max_length=250, required=True, 
                           widget=forms.TextInput(attrs={'placeholder':'نام',
                                                         'class':'name',}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'ایمیل',
                                                            'class':'email'}))
    phone = forms.CharField(max_length=11, required=True, 
                            widget=forms.NumberInput({'placeholder':'شماره تماس',
                                                        'class':'phone'}))
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError("مقدار وارد شده عددی نیست")
            else:
                return phone
            

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

        widgets={
            'body': forms.TextInput(attrs={
                'placeholder': 'متن کامنت',
                'class': 'cm-body',
                'height': '50px',
                }),
        }



class CreatePostForm(forms.ModelForm):
    
    image1 = forms.ImageField(label="تصویر اول", required=True)
    image2 = forms.ImageField(label="تصویر دوم", required=True)
    
    class Meta:
        model = Post
        fields = ['title', 'description', 'category', 'reading_time']

    

    def clean_title(self):
        title = self.cleaned_data['title']
        if title:
            if title.isnumeric():
                raise forms.ValidationError("استفاده از عدد برای عنوان پست امکانپذیر نیست")
            elif 10 < len(title) or len(title) < 2:
                raise forms.ValidationError("عنوان پست باید شامل 2 تا ۱۰ کاراکتر باشد")
            else:
                return title

    def clean_description(self):
        description = self.cleaned_data['description']
        if description:
            if 100 <= len(description) or len(description)<= 2:
                raise forms.ValidationError("تعداد کاراکتر وارد شده برای متن پست مجاز نیست")
            else:
                return description
            
    

class SearchForm(forms.Form):
    query = forms.CharField()


#forme dasti baraye login
# class LoginForm(forms.Form):
#     username = forms.CharField(max_length=250, required=True)
#     password = forms.CharField(max_length=250, required=True, widget=forms.PasswordInput)
    

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=20, widget=forms.PasswordInput,label="password")
    password2 = forms.CharField(max_length=20, widget=forms.PasswordInput, label="repeat password")
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("پسوردها مطابقت ندارند")
        return cd['password2']
    

class UserEditForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class AccountEditForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ['date_of_birth', 'bio', 'job', 'photo']


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='نام کاربری', widget=forms.TextInput(
        attrs = {
            'placeholder':'username'
        }
    ))
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput(
        attrs = {
            'placeholder': 'password'
        }
    ))


class LogoutForm(AuthenticationForm):
    pass