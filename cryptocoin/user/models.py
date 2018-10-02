from django.db import models
from django.utils import timezone

# imports from settings
from django.conf import settings
import os

# Create your models here.
class School(models.Model):
    name            = models.CharField(max_length=50)
    state           = models.CharField(max_length=30, default="")
    description     = models.CharField(max_length=300, default="")
    student_mode_for_admins = models.BooleanField(default=False)
    def __str__(self):
        return str(self.id) + " " + self.name + " " + self.state

class UserData(models.Model):
    username   = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    last_name  = models.CharField(max_length=30)
    password   = models.CharField(max_length=30, default="author:vitaly_ford")
    honory_coins    = models.IntegerField(default=settings.DEFAULT_HONORARY_COINS)
    permanent_coins = models.IntegerField(default=settings.DEFAULT_PERMANENT_COINS)
    items_bought    = models.IntegerField(default=0)
    date            = models.DateTimeField()
    is_admin        = models.BooleanField(default=False)
    tier            = models.IntegerField(default=0)
    driplets_score  = models.IntegerField(default=0)
    school          = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    def save(self, *args, **kwargs):
        if not self.id:
            self.date = timezone.now()
        return super(UserData, self).save(*args, **kwargs)
    def __str__(self):
        return "ID = " + str(self.id) + " " + self.username + ", " + self.first_name + " " + self.last_name + ", Team # = " + str(self.team_number) + " Driplets: " + str(self.driplets_score)

class PassRecQuestions(models.Model):
    question = models.CharField(max_length=255)
    def __str__(self):
        return self.question

class UserAnswers(models.Model):
    data       = models.OneToOneField(UserData, on_delete=models.CASCADE, primary_key=True,)
    question1  = models.CharField(max_length=255)
    question2  = models.CharField(max_length=255)
    question3  = models.CharField(max_length=255)
    answer1    = models.CharField(max_length=30)
    answer2    = models.CharField(max_length=30)
    answer3    = models.CharField(max_length=30)
    was_hacked = models.IntegerField(default=0)
    def __str__(self):
        return self.data.username
    def user_is_hacked(self):
        return was_hacked > 0

class Code(models.Model):
    allowed_hash = models.CharField(max_length=20)
    name         = models.CharField(max_length=70, default="registration")
    value        = models.IntegerField(default=0)
    infinite     = models.BooleanField(default=False)
    school       = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    def __str__(self):
        output = self.allowed_hash
        if self.name != "registration":
            output += " \n♥" + str(self.value)
        if self.infinite:
            return output + "\n(inf)"
        return output

class CodeRedeemer(models.Model):
    username = models.CharField(max_length=30)
    code     = models.CharField(max_length=20)
    date     = models.DateTimeField()
    def save(self, *args, **kwargs):
        if not self.id:
            self.date = timezone.now()
        return super(CodeRedeemer, self).save(*args, **kwargs)
    def __str__(self):
        return self.username + " has redeemed " + self.code

class TransferLogs(models.Model):
    sender   = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    date     = models.DateTimeField()
    amount   = models.IntegerField(default=0)
    hash     = models.CharField(max_length=100)
    school   = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    def save(self, *args, **kwargs):
        if not self.id:
            self.date = timezone.now()
        return super(TransferLogs, self).save(*args, **kwargs)
    def __str__(self):
        return self.sender + " sent to " + self.receiver + " " + str(self.amount) + " coins"

def image_upload_market(instance, filename):
    image_path = '{school}/market/{filename}'.format(school=instance.school.id, filename=filename)
    return image_path

def image_upload_activities(instance, filename):
    image_path = '{school}/activities/{filename}'.format(school=instance.school.id, filename=filename)
    return image_path

class MarketItem(models.Model):
    name            = models.CharField(max_length=50)
    description     = models.CharField(max_length=300)
    cost_permanent  = models.IntegerField(default=0)
    image_file      = models.ImageField(upload_to=image_upload_market, default='no-image.jpg')
    quantity        = models.IntegerField(default=1)
    tier            = models.IntegerField(default=10) # default is 10 => anyone can order
    school          = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    def __str__(self):
        return self.name

class Cart(models.Model):
    user_data       = models.OneToOneField(UserData, on_delete=models.CASCADE, primary_key=True,)
    market_items    = models.ManyToManyField(MarketItem, blank=True)
    date            = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        #if not self.date:
        #self.date = timezone.now()
        return super(Cart, self).save(*args, **kwargs)
    def __str__ (self):
        return self.user_data.first_name + " " + self.user_data.last_name + " (aka " + self.user_data.username + ")" + " wants "

class Achievement(models.Model):
    user_data       = models.ManyToManyField(UserData, blank=True)
    name            = models.CharField(max_length=50)
    description     = models.CharField(max_length=300)
    image_file      = models.ImageField(upload_to=image_upload_activities, default='no-image.jpg')
    school          = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    def __str__(self):
        return str(self.id) + " " + self.name

class PortalSetting(models.Model):
    name            = models.CharField(max_length=50)
    value           = models.CharField(max_length=50, default="false")
    school          = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    def __str__(self):
        return self.name

class Bugs(models.Model):
    name            = models.CharField(max_length=30)
    reward          = models.IntegerField(default=20)
    user_data       = models.ForeignKey(UserData, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    date            = models.DateTimeField()
    school          = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    link            = models.CharField(max_length=300)
    def save(self, *args, **kwargs):
        if not self.id:
            self.date = timezone.now()
            self.date = self.date
        return super(Bugs, self).save(*args, **kwargs)
    def __str__ (self):
        return self.name

class SEQuesAnsw(models.Model):
    question        = models.CharField(max_length=500)
    answer          = models.CharField(max_length=200)
    school          = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    def __str__ (self):
        return self.question

class SECorrectAnswer(models.Model):
    user_data       = models.ForeignKey(UserData, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    se_ques_answ    = models.ForeignKey(SEQuesAnsw, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    def __str__ (self):
        return self.user_data.first_name + " " + self.user_data.last_name + " answered " + self.se_ques_answ.question

class Feedback(models.Model):
    message = models.CharField(max_length=500)
    school  = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True) # one to many relationship
    date    = models.DateTimeField()
    def save(self, *args, **kwargs):
        if not self.id:
            self.date = timezone.now()
        return super(Feedback, self).save(*args, **kwargs)
    def __str__ (self):
        return self.message
