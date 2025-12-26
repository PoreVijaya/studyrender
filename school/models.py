from django.db import models
from django.contrib.auth.models import User

# ---------------------------------------------------
# STUDENT EXTRA MODEL
# ---------------------------------------------------
class StudentExtra(models.Model):

    FACILITY_CHOICES = (
        ('seat', 'Reserved Seat'),
        ('locker', 'Reserved Locker'),
        ('seat_locker', 'Reserved Seat with Locker'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='extra'
    )
    payment_date = models.DateField(null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)

    facility = models.CharField(
        max_length=20,
        choices=FACILITY_CHOICES,
        null=True,
        blank=True
    )

    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)
    vehicle_number = models.CharField(max_length=20, null=True, blank=True)

    collected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collected_extra'
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"



# ---------------------------------------------------
# NOTICE MODEL
# ---------------------------------------------------
class Notice(models.Model):
    expiration_date = models.DateField(null=True, blank=True)
    message = models.CharField(max_length=500)
    by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.message[:30]


# ---------------------------------------------------
# MONTHLY RECORD MODEL (FIXED)
# ---------------------------------------------------
class StudentMonthlyRecord(models.Model):

    PAYMENT_METHOD_CHOICES = (
        ('online', 'Online'),
        ('Cash', 'Cash'),
    )

    FACILITY_CHOICES = (
        ('seat', 'Reserved Seat'),
        ('locker', 'Reserved Locker'),
        ('seat_locker', 'Reserved Seat with Locker'),
    )

    id = models.AutoField(primary_key=True)

    student = models.ForeignKey(
        StudentExtra,
        on_delete=models.CASCADE,
        related_name='monthly_records'
    )

    collected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collected_records'
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True
    )

    facility = models.CharField(
        max_length=20,
        choices=FACILITY_CHOICES,
        null=True,
        blank=True
    )

    month = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()

    fee = models.DecimalField(max_digits=10, decimal_places=2)
    paid_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'school_student_record'

    def save(self, *args, **kwargs):
        self.remaining_fee = self.fee - self.paid_fees
        super().save(*args, **kwargs)




from django.db import models

class ExpenseCategory(models.TextChoices):
    ELECTRICITY = "Electricity Bill", "Electricity Bill"
    CLEANING = "Cleaning Charges", "Cleaning Charges"
    WATER = "Water Bill", "Water Bill"
    INTERNET = "Internet Charges", "Internet Charges"
    RENT = "Rent", "Rent"
    REPEARING = "REPEARING", "Reparing"
    SALARY = "Salary", "Salary"
    


class Expense(models.Model):
    category = models.CharField(
        max_length=100,
        choices=ExpenseCategory.choices,
        default=ExpenseCategory.ELECTRICITY
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"
