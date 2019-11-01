from django.db import models as _models
from django.contrib.auth.models import User as _user


from cvat.apps.engine.models import SafeCharField as _SafeCharField


class TFAnnotationModel(_models.Model):
    owner = _models.ForeignKey(_User, null=True, blank=True,
    on_delete= _models.SET_NULL)
    model_name = _SafeCharField(max_length=256)
    signature_name = _SafeCharField(max_length=256)
    created_date = _models.DateTimeField(auto_now_add=True)
    updated_date = _models.DateTimeField(auto_now_add=True)
    # upload_path_handler: https://github.com/opencv/cvat/blob/1487ceafb9d872a2afd3ad1b50a0c783efdb2808/cvat/apps/auto_annotation/models.py#L16
    labelmap_file = _models.FileField(upload_to=upload_path_handler, storage=fs)
    interpretation_file = _models.FileField(upload_to=upload_path_handler, storage=fs)

    class Meta:
        default_permissions = ()
