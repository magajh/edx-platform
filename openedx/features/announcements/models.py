"""
Models for Announcements
"""


from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Announcement(models.Model):
    """Site-wide announcements to be displayed on the dashboard"""
    class Meta:
        app_label = 'announcements'

    content = models.CharField(max_length=1000, null=False, default="lorem ipsum")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.content
