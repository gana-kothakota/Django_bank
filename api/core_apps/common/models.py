import uuid
from typing import Any, Optional 
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType 
from django.db import IntegrityError, models 
from django.utils import timezone 
from django.utils.translation import gettext_lazy as _ 


# Create your models here. 
user = get_user_model()

class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
