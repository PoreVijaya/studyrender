from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from .forms import StudentSelectForm, MonthlyFeeForm

def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/index.html')


# Logout
from django.contrib.auth import logout
def logout_view(request):
    logout(request)  # Logs out the user
    request.session.flush()  # Clears all session data (user_type, user_id, etc.)
    return render(request, 'school/index.html')



#for showing signup/login button for teacher
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/adminclick.html')


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/studentclick.html')



def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()


            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            return HttpResponseRedirect('adminlogin')
    return render(request,'school/adminsignup.html',{'form':form})



def student_signup_view(request):
    form1 = forms.StudentUserForm()
    form2 = forms.StudentExtraForm()
    mydict = {'form1': form1, 'form2': form2}

    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST, request.FILES)
        
        if form1.is_valid() and form2.is_valid():
            user = form1.save()
            user.set_password(user.password)
            user.save()

            # Create Student first
            student = models.Student.objects.create(user=user)

            # Now save StudentExtra
            f2 = form2.save(commit=False)
            f2.student = student
            f2.collected_by = request.user  # optional
            f2.save()

            # Add student to group
            group = Group.objects.get_or_create(name='STUDENT')[0]
            group.user_set.add(user)

            return HttpResponseRedirect('studentlogin')

    return render(request, 'school/studentsignup.html', context=mydict)




#for checking user is techer , student or admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()



def afterlogin_view(request):
    user = request.user
    
    # Admin
    if is_admin(user):
        request.session['user_type'] = 'admin'
        request.session['user_id'] = user.id
        return redirect('admin-dashboard')
    
    # Student
    elif is_student(user):
        accountapproval = models.StudentExtra.objects.filter(user_id=user.id, status=True).first()
        if accountapproval:
            request.session['user_type'] = 'student'
            request.session['user_id'] = user.id
            return redirect('student-dashboard')
        else:
            return render(request, 'school/student_wait_for_approval.html')

    # Fallback
    return redirect('login')  



# from django.db.models import Count, Sum, F
# @login_required(login_url='adminlogin')
# def admin_dashboard_view(request):
#     if not request.user.is_authenticated or request.session.get('user_type') != 'admin' or not request.user.groups.filter(name='ADMIN').exists():
#         return render(request, 'school/index.html')

#     selected_month = request.GET.get('month')
#     month_filter = {}
#     if selected_month:
#         try:
#             year, month = selected_month.split('-')
#             month_filter = {'start_date__year': int(year), 'start_date__month': int(month)}
#         except:
#             month_filter = {}

#     student_records = StudentMonthlyRecord.objects.all()
#     if month_filter:
#         student_records = student_records.filter(**month_filter)

#     # Total fees
#     total_studentfee = student_records.aggregate(total=Sum('fee'))['total'] or 0
#     paid_studentfee = student_records.aggregate(total=Sum('paid_fees'))['total'] or 0
#     pendingstudentfee = total_studentfee - paid_studentfee

#     # Admin stats
#     admin_stats = (
#         student_records.filter(collected_by__isnull=False)
#         .values('collected_by', 'collected_by__first_name', 'collected_by__last_name')
#         .annotate(
#             total_students=Count('student_id', distinct=True),
#             total_fee=Sum('fee'),
#             total_paid=Sum('paid_fees'),
#             remaining_amount=Sum(F('fee') - F('paid_fees'))
#         )
#     )

#     # Unique student count
#     unique_student_count = student_records.values('student_id').distinct().count()

#     notice = models.Notice.objects.all()

#     context = {
#         'studentcount': unique_student_count,   
#         'pendingstudentcount': 0,               
#         'studentfee': total_studentfee,
#         'pendingstudentfee': pendingstudentfee,
#         'admin_stats': admin_stats,
#         'selected_month': selected_month,
#         'notice': notice,
#     }

#     return render(request, 'school/admin_dashboard.html', context)



from django.db.models import Count, Sum, F
from django.contrib.auth.decorators import login_required
from .models import StudentMonthlyRecord
from school import models


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    if (
        not request.user.is_authenticated
        or request.session.get('user_type') != 'admin'
        or not request.user.groups.filter(name='ADMIN').exists()
    ):
        return render(request, 'school/index.html')

    # 🔹 Month & Year filter (YYYY-MM)
    selected_month = request.GET.get('month')

    student_records = StudentMonthlyRecord.objects.all()

    if selected_month:
        try:
            year, month = selected_month.split('-')
            student_records = student_records.filter(
                start_date__year=int(year),
                start_date__month=int(month)
            )
        except ValueError:
            pass

    # 🔹 Total fees
    total_studentfee = student_records.aggregate(
        total=Sum('fee')
    )['total'] or 0

    paid_studentfee = student_records.aggregate(
        total=Sum('paid_fees')
    )['total'] or 0

    pendingstudentfee = total_studentfee - paid_studentfee

    # 🔹 Admin-wise stats
    admin_stats = (
        student_records
        .filter(collected_by__isnull=False)
        .values(
            'collected_by',
            'collected_by__first_name',
            'collected_by__last_name'
        )
        .annotate(
            total_students=Count('student_id', distinct=True),
            total_fee=Sum('fee'),
            total_paid=Sum('paid_fees'),
            remaining_amount=Sum(F('fee') - F('paid_fees'))
        )
    )

    # 🔹 Unique student count
    unique_student_count = (
        student_records
        .values('student_id')
        .distinct()
        .count()
    )

    notice = models.Notice.objects.all()

    context = {
        'studentcount': unique_student_count,
        'studentfee': total_studentfee,
        'pendingstudentfee': pendingstudentfee,
        'admin_stats': admin_stats,
        'selected_month': selected_month,
        'notice': notice,
    }

    return render(request, 'school/admin_dashboard.html', context)



#for student by admin

@login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
def admin_student_view(request):
     # Check 1: User not logged in
    if not request.user.is_authenticated:
        return render(request, 'school/index.html')
 
    # Check 2: Not an admin by session or group
    if request.session.get('user_type') != 'admin' or not request.user.groups.filter(name='ADMIN').exists():
        return render(request, 'school/index.html')
    
    return render(request,'school/admin_student.html')


from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import F, Value
from django.db.models.functions import Concat

from . import forms
from .models import StudentExtra


# ---------------------------------------------------
# ADD STUDENT (ADMIN)
# ---------------------------------------------------
def admin_add_student_view(request):
    # Authentication check
    if not request.user.is_authenticated:
        return render(request, 'school/index.html')

    # Admin access check
    if request.session.get('user_type') != 'admin' or \
       not request.user.groups.filter(name='ADMIN').exists():
        return render(request, 'school/index.html')

    form1 = forms.StudentUserForm()
    form2 = forms.StudentExtraForm()

    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST, request.FILES)

        if form1.is_valid() and form2.is_valid():
            # ---- Save User ----
            user = form1.save(commit=False)
            user.set_password(form1.cleaned_data['password'])
            user.save()

            # ---- Save StudentExtra ----
            student = form2.save(commit=False)
            student.user = user

            # REQUIRED fields
            student.first_name = user.first_name
            student.last_name = user.last_name
            student.collected_by = request.user

            student.save()

            # ---- Add to STUDENT group ----
            group, _ = Group.objects.get_or_create(name='STUDENT')
            group.user_set.add(user)

            return HttpResponseRedirect('admin-student')

    return render(request, 'school/admin_add_student.html', {
        'form1': form1,
        'form2': form2
    })


# ---------------------------------------------------
# VIEW STUDENTS (ADMIN)
# ---------------------------------------------------
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F, Value
from django.db.models.functions import Concat

from .models import StudentExtra


@login_required(login_url='adminlogin')
def admin_view_student_view(request):
    # ---- Admin access check ----
    if request.session.get('user_type') != 'admin' or \
       not request.user.groups.filter(name='ADMIN').exists():
        return render(request, 'school/index.html')

    # ---- Base queryset ----
    students = StudentExtra.objects.select_related(
        'user',
        'collected_by'
    )

    search_name = request.GET.get('search_name', '').strip()
    month = request.GET.get('month')

    # ---- Name search (User table is source of truth) ----
    if search_name:
        students = students.annotate(
            full_name=Concat(
                F('user__first_name'),
                Value(' '),
                F('user__last_name')
            )
        ).filter(full_name__icontains=search_name)

    # ---- Month filter ----
    if month:
        year, month = month.split('-')
        students = students.filter(
            payment_date__year=year,
            payment_date__month=month
        )

    return render(request, 'school/admin_view_student.html', {
        'students': students,
        'total_count': students.count(),
        'search_name': search_name,
    })





@login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
def delete_student_from_school_view(request, pk):

    if not request.user.is_authenticated:
        return render(request, 'school/index.html')

    if request.session.get('user_type') != 'admin' or not request.user.groups.filter(name='ADMIN').exists():
        return render(request, 'school/index.html')

    student = get_object_or_404(models.StudentExtra, id=pk)

    # ✅ NEW: Block if not the owner
    if student.collected_by != request.user:
        return HttpResponseForbidden("You are not allowed to delete this student.")

    user = models.User.objects.get(id=student.user_id)

    user.delete()
    student.delete()

    return redirect('admin-view-student')


@login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
def delete_student_view(request,pk):
     # Check 1: User not logged in
    if not request.user.is_authenticated:
        return render(request, 'school/index.html')
 
    # Check 2: Not an admin by session or group
    if request.session.get('user_type') != 'admin' or not request.user.groups.filter(name='ADMIN').exists():
        return render(request, 'school/index.html')
    
    student=models.StudentExtra.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return redirect('admin-approve-student')



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from . import models, forms
from django.http import HttpResponseForbidden

@login_required(login_url='adminlogin')
def update_student_view(request, pk):

    if not request.user.is_authenticated:
        return render(request, 'school/index.html')

    if request.session.get('user_type') != 'admin' or not request.user.groups.filter(name='ADMIN').exists():
        return render(request, 'school/index.html')

    student = get_object_or_404(models.StudentExtra, id=pk)
    user = get_object_or_404(User, id=student.user_id)

    # Optional: restrict editing to collector
    if student.collected_by != request.user:
        return HttpResponseForbidden("You are not allowed to edit this student.")

    form1 = forms.StudentUserForm(instance=user)
    form2 = forms.StudentExtraForm(instance=student)

    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST, instance=user)
        form2 = forms.StudentExtraForm(request.POST, request.FILES, instance=student)

        if form1.is_valid() and form2.is_valid():
            new_username = form1.cleaned_data['username']
            if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                form1.add_error('username', 'This username is already taken by another user.')
            else:
                updated_user = form1.save(commit=False)
                updated_user.save()

                student_extra = form2.save(commit=False)
                student_extra.facility = request.POST.get("facility")
                student_extra.save()

                return redirect('admin-student')

    context = {'form1': form1, 'form2': form2}
    return render(request, 'school/admin_update_student.html', context)




#notice related viewsssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss


from .models import Notice
from django.utils import timezone
from datetime import datetime

@login_required(login_url='adminlogin')
# @user_passes_test(is_admin)
def admin_notice_view(request):
     # Check 1: User not logged in
    if not request.user.is_authenticated:
        return render(request, 'school/index.html')
 
    # Check 2: Not an admin by session or group
    if request.session.get('user_type') != 'admin' or not request.user.groups.filter(name='ADMIN').exists():
        return render(request, 'school/index.html')
    
    # Remove expired notices
    Notice.objects.filter(expiration_date__lt=timezone.now().date()).delete()

    form = forms.NoticeForm()
    if request.method == 'POST':
        form = forms.NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.by = request.user
            notice.save()
            return redirect('admin-notice')

    # Fetch all notices posted by the logged-in admin
    # notices = Notice.objects.filter(by=request.user.first_name).order_by('-date')
    notices = Notice.objects.all().order_by('-date')  # Shows all notices

    
    return render(request, 'school/admin_notice.html', {'form': form, 'notices': notices})



from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Notice
from .forms import NoticeForm

# Function to check if a user is an admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

@login_required
def edit_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)

    # Dynamically determine base template
    base_template = "school/adminbase.html" if is_admin(request.user) else "school/teacherbase.html"

    # Permission check (Admins can edit any notice, Teachers can edit only their own)
    if not is_admin(request.user) and notice.by != request.user:
        return HttpResponseForbidden("You are not allowed to edit this notice.")

    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            # Redirect to appropriate page after editing
            return redirect('admin-notice' if is_admin(request.user) else 'teacher-notice')
    else:
        form = NoticeForm(instance=notice)

    return render(request, 'school/edit_notice.html', {'form': form, 'notice': notice, 'base_template': base_template})


@login_required
def delete_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)

    # Permission check
    if not is_admin(request.user):
        if notice.by != request.user:
            return HttpResponseForbidden("You are not allowed to delete this notice.")

    notice.delete()
    # Redirect to appropriate page based on role
    if is_admin(request.user):
        return redirect('admin-notice')
    else:
        return redirect('teacher-notice')




#FOR STUDENT AFTER THEIR Loginnnnnnnnnnnnnnnnnnnnn
@login_required(login_url='studentlogin')
def student_dashboard_view(request):
    if not request.user.is_authenticated or request.session.get('user_type') != 'student' or not request.user.groups.filter(name='STUDENT').exists():
        return render(request, 'school/index.html')

    student_extra = get_object_or_404(StudentExtra, user=request.user)
    student = student_extra.student

    fee_records = StudentMonthlyRecord.objects.filter(student=student)
    total_fee = fee_records.aggregate(total=Sum('fee'))['total'] or 0
    total_paid = fee_records.aggregate(total=Sum('paid_fees'))['total'] or 0
    total_remaining = total_fee - total_paid

    notice = models.Notice.objects.all()

    context = {
        'roll': getattr(student_extra, 'roll', ''),
        'mobile': student_extra.mobile,
        'total_fee': total_fee,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'notice': notice
    }

    return render(request, 'school/student_dashboard.html', context)




# for aboutus and contact ussssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
def aboutus_view(request):
    return render(request,'school/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message'] 
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'school/contactussuccess.html')
    return render(request, 'school/contactus.html', {'form':sub})




#Profile View For Admin , Teacher and Student

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User


def admin_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'school/index.html')

    if request.session.get('user_type') != 'admin' or not request.user.groups.filter(name='ADMIN').exists():
        return render(request, 'school/index.html')
    
    admin_user = request.user  
    return render(request, 'school/admin_profile.html', {'admin_user': admin_user})


from .models import StudentExtra

def student_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'school/index.html')

    if request.session.get('user_type') != 'student' or not request.user.groups.filter(name='STUDENT').exists():
        return render(request, 'school/index.html')
    
    student_user = request.user

    try:
        student_extra = StudentExtra.objects.get(user=student_user)
    except StudentExtra.DoesNotExist:
        student_extra = None

    return render(request, 'school/student_profile.html', {
        'student_user': student_user,
        'student_extra': student_extra
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import StudentExtra, StudentMonthlyRecord
from .forms import StudentSelectForm, MonthlyFeeForm
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, F  # Aggregate imports here
from django.db.models.functions import Concat
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime, timedelta  # For fee form initials
from . import forms, models

def select_student(request):
    if request.method == "POST":
        student_id = request.POST.get("student")
        if student_id:
            return redirect("student-fee-list", student_id=student_id)
        messages.error(request, "Please select a student.")
    form = StudentSelectForm()
    return render(request, "school/select_student.html", {"form": form})


from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from .models import StudentExtra, StudentMonthlyRecord

def student_fee_list(request, student_id):
    # Fetch student without filtering by 'status'
    student = get_object_or_404(StudentExtra, pk=student_id)

    # Get all monthly records for this student
    fee_records = StudentMonthlyRecord.objects.filter(student=student).order_by('-start_date')

    # Aggregate totals
    total_fee = fee_records.aggregate(total=Sum('fee'))['total'] or 0
    total_paid = fee_records.aggregate(total=Sum('paid_fees'))['total'] or 0
    total_remaining = total_fee - total_paid

    return render(request, "school/student_fee_list.html", {
        "student": student,
        "fee_records": fee_records,
        "total_fee": total_fee,
        "total_paid": total_paid,
        "total_remaining": total_remaining
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import StudentExtra
from .forms import MonthlyFeeForm

def add_fee_record(request, student_id):
    # Fetch student without filtering by status
    student = get_object_or_404(StudentExtra, pk=student_id)

    if request.method == "POST":
        form = MonthlyFeeForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.student = student

            # Always set collected_by as logged-in user
            record.collected_by = request.user

            record.save()
            messages.success(request, "Fee record added successfully!")
            return redirect("student-fee-list", student_id=student.id)
    else:
        form = MonthlyFeeForm()

    return render(request, "school/add_fee_record.html", {
        "form": form,
        "student": student
    })



from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='adminlogin')
def expenses_dashboard_view(request):
    return render(request, 'school/expenses.html')




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Expense, ExpenseCategory
from .forms import ExpenseForm


@login_required(login_url='adminlogin')
def add_expense_view(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, "Expense added successfully.")
            return redirect('expense_list')
    else:
        form = ExpenseForm()

    return render(request, 'school/add_expense.html', {'form': form})


@login_required(login_url='adminlogin')
def expense_list_view(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'school/expense_list.html', {'expenses': expenses})


# ✅ ADD THIS DELETE VIEW
@login_required(login_url='adminlogin')
def delete_expense_view(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted successfully.")

    return redirect('expense_list')
