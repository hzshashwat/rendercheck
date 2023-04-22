from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.core.validators import MaxValueValidator

# Create your models here.
class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""

    def create_user(self, leader_email, password=None):
        """Create a new user profile"""
        if not leader_email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(leader_email)
        user = self.model(leader_email = leader_email)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, leader_email, password):
        """Create and save a new superuser with given details"""
        user = self.create_user(leader_email, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user

class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system"""
    team_name = models.CharField(max_length=150, null= True)
    leader_name = models.CharField(max_length=150, null= True)
    leader_email = models.CharField(max_length=150, primary_key=True)
    leader_hosteler = models.CharField(max_length=150, null= True)
    leader_year = models.CharField(max_length=150, null= True)
    leader_branch = models.CharField(max_length=150, null= True)
    leader_rollNo = models.CharField(max_length=150, null= True)
    leader_phoneNo = models.CharField(max_length=150, null= True)
    member_name = models.CharField(max_length=150, null= True)
    member_phoneNo = models.CharField(max_length=150, null= True)
    member_branch = models.CharField(max_length=150, null= True)
    member_email = models.CharField(max_length=150, null= True)
    member_rollNo = models.CharField(max_length=150, null= True)
    member_hosteler = models.CharField(max_length=150, null= True)
    member_year = models.CharField(max_length=150, null= True)
    selected_schema = models.CharField(max_length=150, null= True)
    final_submission_completed = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'leader_email'
    REQUIRED_FIELDS = []

    def get_team_name(self):
        """Retrieve full name for user"""
        return self.team_name

    def get_leader_name(self):
        """Retrieve short name of user"""
        return self.leader_name

    def __str__(self):
        """Return string representation of user"""
        return self.leader_email
    
class LeaderBoard(models.Model):
    team = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True)
    team_name = models.CharField(max_length=150)
    score = models.IntegerField(default=0)