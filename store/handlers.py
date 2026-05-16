import logging
from django.apps import apps
from django.utils import timezone

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            SiteLog = apps.get_model('store', 'SiteLog')
            message = self.format(record)
            SiteLog.objects.create(
                timestamp=timezone.now(),
                level=record.levelname,
                logger_name=record.name,
                message=message,
                pathname=getattr(record, 'pathname', ''),
                func_name=getattr(record, 'funcName', ''),
                line_no=getattr(record, 'lineno', None),
            )
        except Exception:
            pass
