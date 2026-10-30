import uuid
from typing import Any, Optional 
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType 
from django.db import IntegrityError, models 
from django.utils import timezone 
from django.utils.translation import gettext_lazy as _ 

User = get_user_model()

class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContentView(TimeStampedModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_("content type"))    
    object_id = models.UUIDField(verbose_name=_("object id"))   
    content_object = GenericForeignKey('content_type', 'object_id') 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="content_views", verbose_name=_("user"))
    viewer_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("viewer ip"))
    last_viewed = models.DateTimeField(verbose_name=_("last viewed"))

    class Meta:
         verbose_name = _("Content View")
         verbose_name_plural = _("Content Views")
         unique_together = ["content_type", "object_id", "user", "viewer_ip"]

    def __str__(self) -> str:
        viewer = self.user.get_full_name() if self.user else 'Anonymous'
        return f"{self.content_type} viewed by {viewer} from IP {self.viewer_ip} on {self.last_viewed}"
       
    @classmethod
    def record_view(cls, content_object: Any, user: Optional[Any], viewer_ip: Optional[str]) -> None:
        content_type = ContentType.objects.get_for_model(content_object)
        try:
            view, created = cls.objects.get_or_create(
                content_type=content_type,
                object_id=content_object.id,
                defaults={
                    "user": user,
                    "viewer_ip": viewer_ip,
                    "last_viewed": timezone.now()
                }
            )
            if not created:
                view.last_viewed = timezone.now()
                view.save()
        except IntegrityError:
            pass
       

    

    
    
