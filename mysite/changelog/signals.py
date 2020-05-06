import time
import json
import datetime

from .models import ChangeLog, ACTION_CREATE, ACTION_UPDATE, ACTION_DELETE
from changelog.mixins import ChangeLogMixin


def changelog_save_handler(sender, instance, created, **kwargs):
    if isinstance(instance, ChangeLogMixin):
        last_saved = {}
        changed = False
        if changed:
            if created:
                ChangeLog.add(instance=instance, action=ACTION_CREATE, data={}, id=last_saved['id'])
            else:
                ChangeLog.add(instance=instance, action=ACTION_UPDATE, data={}, id=last_saved['id'])


def changelog_delete_handler(sender, instance, using, **kwargs):
    if isinstance(instance, ChangeLogMixin):
        last_saved = {}
        ChangeLog.add(instance, action=ACTION_DELETE, data={}, id=last_saved['id'])


_last_saved = {}

def get_last_saved(request, instance):
    last_saved = _last_saved[request] if request in _last_saved else None
    if not last_saved or last_saved['instance'].__class__ != instance.__class__ or last_saved['instance'].id != instance.id:
        last_saved = {
            'instance': instance,
            'changed': {},
            'id': None,
            'timestamp': time.time(),
        }
        _last_saved[request] = last_saved
    return last_saved


def merge(o1, o2):
    for key in o2:
        val2 = o2[key]
        if isinstance(val2, dict) and key in o1:
            val1 = o1[key]
            for k in val2:
                val1[k] = val2[k]
        else:
            o1[key] = val2
    return o1
