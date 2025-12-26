from django.contrib import admin
from django.urls import path
from school import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name=''),
    
    path('adminclick', views.adminclick_view),
    path('studentclick', views.studentclick_view),
    
    path('adminsignup', views.admin_signup_view),
    path('studentsignup', views.student_signup_view,name='studentsignup'),
    path('adminlogin', LoginView.as_view(template_name='school/adminlogin.html')),
    path('studentlogin', LoginView.as_view(template_name='school/studentlogin.html')),
    
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),
    
    
    path('admin-student', views.admin_student_view,name='admin-student'),
    path('admin-add-student', views.admin_add_student_view,name='admin-add-student'),
    path('admin-view-student', views.admin_view_student_view,name='admin-view-student'),
    path('delete-student-from-school/<int:pk>', views.delete_student_from_school_view,name='delete-student-from-school'),
    path('delete-student/<int:pk>', views.delete_student_view,name='delete-student'),
    path('update-student/<int:pk>', views.update_student_view,name='update-student'),
    
    # path('admin-notice', views.admin_notice_view,name='admin-notice'),
    path('admin-notice', views.admin_notice_view, name='admin-notice'),
    path('edit-notice/<int:notice_id>/', views.edit_notice, name='edit-notice'),
    path('delete-notice/<int:notice_id>/', views.delete_notice, name='delete-notice'),

    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),
    
    path('profile', views.admin_profile, name='admin_profile'),
    
    path('student/profile/', views.student_profile, name='student_profile'),
    
    path('select-student/', views.select_student, name='select-student'),
    path('student/<int:student_id>/fees/', views.student_fee_list, name='student-fee-list'),
    path('student/<int:student_id>/add-fee-record/', views.add_fee_record, name='add-fee-record'),

]


from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
