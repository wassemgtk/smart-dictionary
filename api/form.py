# coding=utf-8
"""Field utilities"""
from copy import deepcopy

from field import process_fields


NO_VALUE = object()


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def combine_items(value_a, value_b):
    assert type(value_a) is type(value_b)

    combined_items = deepcopy(value_a)

    if isinstance(combined_items, dict):
        for key, value in value_b.iteritems():
            if key in combined_items:
                combined_items[key] = combine_items(combined_items[key], value_b[key])
            else:
                combined_items[key] = value_b[key]
    elif isinstance(combined_items, (list, tuple, basestring, set)):
        combined_items = combined_items + value_b
    else:
        raise ValueError('Cannot combine type "{}"'.format(type(combined_items).__name__))

    return combined_items


class FormFactory(object):
    def __new__(cls, raw_fields, cleaners=None):
        """Create a new form
        :param raw_fields: The list of raw fields to process
        :type raw_fields: list
        :param cleaners: cleaners, if any
        :type cleaners: list
        :return: the newly created form
        :rtype: models.form.Form
        """
        fields = process_fields(raw_fields)

        form_klass = type(
            'AutoForm',
            (Form,),
            {
                'cleaners': cleaners or {},
                'fields': fields
            }
        )

        return form_klass


class Form(object):
    # Added by factory
    fields = ()
    cleaners = ()

    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        return self.data[item]

    @property
    def field_dict(self):
        return {field.name: field for field in self.fields}

    def is_valid(self):
        self.full_clean()

        return not self.errors

    def full_clean(self):
        self.errors = {}
        self.cleaned_data = self.clean()

    def field_not_editable(self, field_name, value):
        """Specify whether a field marked as non-editable should truly throw an error
        This is allowed to be overridden in subclasses so that simply echo'ing back already set
        data can be checked and caused to not throw an error, etc.
        """
        return True  # Always disallow editing of non-editable fields in raw form (no instance)

    def clean(self):
        # TODO: don't do it this way. cleaned data should only have items that pass validation, really
        cleaned_data = deepcopy(self.data)

        for field in self.fields:
            value = cleaned_data.get(field.name, NO_VALUE)
            field_name = field.name

            if field.editable or value is NO_VALUE:
                try:
                    cleaned_data[field_name] = field.clean(value)
                except ValidationError as error:
                    # TODO: remove duplication (use default dict?)
                    if isinstance(error.args[0], dict):
                        self.errors.setdefault(field_name, {})
                        self.errors[field_name] = (
                            combine_items(self.errors[field_name], error.args[0])
                        )
                    elif isinstance(error.args[0], list):
                        self.errors.setdefault(field_name, [])
                        self.errors[field_name].extend(error.args[0])
                    else:
                        self.errors.setdefault(field_name, [])
                        self.errors[field_name].append(str(error))
            else:
                if self.field_not_editable(field_name, value):
                    # A non-editable field with a value
                    self.errors.setdefault(field_name, [])
                    self.errors[field_name].append('Cannot edit this field')

        # Only run cleaners if the form is valid, as global cleaners don't work on invalid documents
        if not self.errors:
            for cleaner in self.cleaners:
                # Attempt to run cleaners, and stop when the first one breaks (as any invalidity in
                # one global cleaner, can taint the result of another)
                try:
                    cleaned_data = cleaner(self, cleaned_data)
                except ValidationError as error:
                    error_arg = error.args[0]

                    if isinstance(error_arg, dict):
                        # When a validation error is raised with a dictionary, assign it directly
                        self.errors = combine_items(error_arg, self.errors)
                    elif isinstance(error_arg, list):
                        self.errors.setdefault('__all__', [])
                        self.errors['__all__'].extend(error_arg)
                    else:
                        self.errors.setdefault('__all__', [])
                        self.errors['__all__'].append(str(error))

                    break

        return cleaned_data
