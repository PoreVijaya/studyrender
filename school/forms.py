from django import forms
from django.contrib.auth.models import User
from . import models
from .models import Expense, ExpenseCategory

# ---------------------------------------------------
# ADMIN SIGNUP FORM
# ---------------------------------------------------
class AdminSigupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password"]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Username already exists. Please choose a different username."
            )
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # ✅ hash password
        if commit:
            user.save()
        return user


# ---------------------------------------------------
# STUDENT USER FORM (USER TABLE)
# ---------------------------------------------------
class StudentUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=True,
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "password"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # ✅ hash password
        if commit:
            user.save()
        return user


# ---------------------------------------------------
# STUDENT EXTRA FORM (PROFILE + EXTRA DATA)
# ---------------------------------------------------
class StudentExtraForm(forms.ModelForm):
    payment_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    profile_pic = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = models.StudentExtra
        fields = ["mobile", "payment_date", "profile_pic", "vehicle_number"]
        widgets = {
            "mobile": forms.TextInput(attrs={"class": "form-control"}),
            "vehicle_number": forms.TextInput(attrs={"class": "form-control"}),
        }


# ---------------------------------------------------
# NOTICE FORM
# ---------------------------------------------------
class NoticeForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 4, "class": "form-control"}
        ),
        required=True,
    )

    expiration_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
        required=True,
    )

    class Meta:
        model = models.Notice
        fields = ["message", "expiration_date"]


# ---------------------------------------------------
# STUDENT SELECT FORM
# ---------------------------------------------------
class StudentSelectForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=models.StudentExtra.objects.all(),
        empty_label="Choose student",
        widget=forms.Select(attrs={"class": "form-select"}),
    )


# ---------------------------------------------------
# MONTHLY FEE FORM
# ---------------------------------------------------
class MonthlyFeeForm(forms.ModelForm):
    class Meta:
        model = models.StudentMonthlyRecord
        fields = [
            "month",
            "start_date",
            "end_date",
            "facility",
            "payment_method",
            "fee",
            "paid_fees",
        ]
        widgets = {
            "month": forms.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "facility": forms.Select(attrs={"class": "form-select"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
            "paid_fees": forms.NumberInput(attrs={"class": "form-control"}),
        }


# ---------------------------------------------------
# EXPENSE FORM
# ---------------------------------------------------
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category", "amount", "date", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "category": forms.Select(
                choices=ExpenseCategory.choices,
                attrs={"class": "form-select"},
            ),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
        }


# school/forms.py
# from django import forms
# from .models import Expense

# class ExpenseForm(forms.ModelForm):
#     class Meta:
#         model = Expense
#         fields = ['category', 'amount', 'date', 'description']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#         }



# school/forms.py
from django import forms
from .models import Expense, ExpenseCategory

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date', 'description']  
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'category': forms.Select(choices=ExpenseCategory.choices)
        }
