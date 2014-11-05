__title__ = 'fobi.contrib.plugins.form_handlers.db_store.fobi_form_handlers'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('DBStoreHandlerPlugin',)

import json
import datetime

from six import string_types

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from fobi.base import (
    FormHandlerPlugin, form_handler_plugin_registry, get_processed_form_data
)
from fobi.contrib.plugins.form_handlers.db_store import UID
from fobi.contrib.plugins.form_handlers.db_store.models import (
    SavedFormDataEntry
)

class DBStoreHandlerPlugin(FormHandlerPlugin):
    uid = UID
    name = _("DB store")

    def run(self, form_entry, request, form):
        """
        :param fobi.models.FormEntry form_entry: Instance of
            ``fobi.models.FormEntry``.
        :param django.http.HttpRequest request:
        :param django.forms.Form form:
        """
        #import ipdb; ipdb.set_trace()
        # Clean up the values, leave our content fields and empty values.
        field_name_to_label_map, cleaned_data = get_processed_form_data(form)

        for key, value in cleaned_data.items():
            if isinstance(value, string_types) and value.startswith(settings.MEDIA_URL):
                cleaned_data[key] = '<a href="{value}">{value}</a>'.format(value=value)
            if isinstance(value, (datetime.datetime, datetime.date)):
                cleaned_data[key] = value.isoformat() if hasattr(value, 'isoformat') else value

        saved_form_data_entry = SavedFormDataEntry(
            form_entry = form_entry,
            user = request.user if request.user and request.user.pk else None,
            form_data_headers = json.dumps(field_name_to_label_map),
            saved_data = json.dumps(cleaned_data)
            )
        saved_form_data_entry.save()

    def custom_actions(self, form_entry, request=None):
        """
        Adding a link to view the saved form enties.

        :return iterable:
        """
        return (
            (
                reverse('fobi.contrib.plugins.form_handlers.db_store.view_saved_form_data_entries', args=[form_entry.pk]),
                _("View entries"),
                'glyphicon glyphicon-list'
            ),
            (
                reverse('fobi.contrib.plugins.form_handlers.db_store.export_saved_form_data_entries', args=[form_entry.pk]),
                _("Export entries"),
                'glyphicon glyphicon-export'
            ),
        )


form_handler_plugin_registry.register(DBStoreHandlerPlugin)
