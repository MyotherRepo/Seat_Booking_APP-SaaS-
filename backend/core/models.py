from django.db import models
from django.contrib.auth.models import AbstractUser

#1. Organization
class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    domain = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name # The organisation will be repesented by its name in the django admin shell
    
#2. User(custom with role and organisation)
class User(AbstractUser):
    ROLE_CHOICES = (
        ('employee','Employee'),
        ('manager','Manager'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='employee')
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,null=True,blank=True) # many to one mapping

    def __str__(self):
        return self.username
    
#3. FloorPlan
class FloorPlan(models.Model):
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE) # link to model organisation
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="floorplans/",null=True,blank=True)
    rows = models.IntegerField(default=10) # for grid representation
    columns = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.organisation.name} - {self.name}"

#4. Seat (associated with a particular floor plan)
class Seat(models.Model):
    floor_plan = models.ForeignKey(FloorPlan,on_delete=models.CASCADE,related_name='seats')
    label = models.CharField(max_length=10)
    row = models.IntegerField()
    column = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.label} ({self.floor_plan.name})"


#5. Booking
class Booking(models.Model):
    seat = models.ForeignKey(Seat,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    marked_attendance = models.BooleanField(default=False)
    booked_by_manager = models.BooleanField(default=False)

    class Meta : 
        unique_together = ('seat','date') # in order to avoid double booking of the same seat

    def __str__(self):
        return f"{self.user.username} - {self.seat.label} on {self.date}"

#6. Waitlist
class Waitlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat,on_delete=models.CASCADE)
    date = models.DateField()
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta : 
        unique_together = ('user','seat','date')

