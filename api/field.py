# coding=utf-8
"""Field utilities"""
import abc
from copy import deepcopy

from api_exceptions import ValidationError
from api_exceptions import SchemaError
from constants import NO_DEFAULT
from constants import NO_VALUE


class Field(object):
    BLANK_FIELD_VALUES = ['', {}, [], ()]

    __metaclass__ = abc.ABCMeta

    # TODO: code contracts here?
    def __init__(self, name, primary=False, editable=True, default=NO_DEFAULT, validators=None, null=False, blank=False):
        assert not (primary and (default in [None] + self.BLANK_FIELD_VALUES or null is True or blank is True))
        assert not (default is None and not null)
        assert not (default in self.BLANK_FIELD_VALUES and not blank)

        self.name = name
        self.validators = validators or []
        self.primary = primary
        self.editable = editable
        self.null = null
        self.blank = blank

        self.has_default = default is not NO_DEFAULT
        self.default = default

    def run_validators(self, value):
        """Run the field's validators
        NOTE: override this function if you wish to have custom error-raising logic
        e.g. subform field requires raising errors as a dictionary, as there fields within.
        """
        # At this point these are errors that do not preclude having multiple failings
        # at a time, so we will collect and re-raise them as a group
        errors = []
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError as error:
                errors.append(str(error))

        return errors

    # TODO: change this to create validators that are then checked
    def validate(self, value):
        if not self.has_default and value is NO_VALUE:
            raise ValidationError('Must provide a value')
        elif not self.null and value is None:
            raise ValidationError('Cannot provide null value')
        elif not self.blank and value in self.BLANK_FIELD_VALUES:
            raise ValidationError('Cannot be blank')

        if value is NO_VALUE:
            value = deepcopy(self.default)

        self.validate_field(value)

        errors = self.run_validators(value)

        if errors:
            raise ValidationError(errors)

    def validate_field(self, value):
        pass

    def prepare(self, value):
        """Prepare the value of the field
        Prepares the value of a field. Is basically the cleaned version of the value
        i.e. '1' to 1 for an IntegerField
        """
        # TODO: change this assumption when prepare runs first? if it changes like that, that is
        if value is NO_VALUE:
            # Can assume validations run at this point, and default exists
            value = deepcopy(self.default)

        return value

    def to_json(self, value):
        """Convert values before insertion into database"""
        return value

    def clean(self, value):
        self.validate(value)
        cleaned_value = self.prepare(value)

        return cleaned_value


class TextField(Field):
    def __init__(self, name, uppercase=False, lowercase=False, **kwargs):
        assert not (uppercase and lowercase), 'Cannot have both uppercasing and lowercasing'
        self.uppercase = uppercase
        self.lowercase = lowercase
        super(TextField, self).__init__(name, **kwargs)

    def validate_field(self, value):
        if value is not None:
            try:
                unicode(value)
            except (TypeError, ValueError):
                raise ValidationError('Value must be string type')

    def prepare(self, value):
        value = super(TextField, self).prepare(value)
        if value is not None:
            value = unicode(value)

            if self.uppercase:
                value = value.upper()
            elif self.lowercase:
                value = value.lower()

        return value


class ArrayField(Field):
    def __init__(self, name, element_type, element_kwargs=None, **kwargs):
        # TODO: move this outside
        element_kwargs = element_kwargs.copy() if element_kwargs else {}
        element_kwargs['type'] = element_type

        self.element_field = process_field('subelement', element_kwargs)

        super(ArrayField, self).__init__(name, **kwargs)

    def validate_field(self, value):
        if value:
            if not isinstance(value, list):
                raise ValidationError('Must be a list of items')

            errors = {}

            for pos, element in enumerate(value):
                try:
                    self.element_field.validate_field(element)
                except ValidationError as error:
                    errors[pos] = error.args[0]

            if errors:
                raise ValidationError(errors)

    def prepare(self, value):
        if value:
            value = [self.element_field.prepare(element) for element in value]

        return value

    def to_json(self, value):
        if value:
            value = [self.element_field.to_json(element) for element in value]

        return value


FIELD_MAP = {
    'text': TextField,
    'array': ArrayField
}


def process_field(field_name, field_attrs):
    field_attrs = field_attrs.copy()

    try:
        field_type = field_attrs.pop('type')
    except KeyError:
        raise SchemaError('Missing field type for field "{}"'.format(field_name))
    else:
        try:
            field = FIELD_MAP[field_type]
        except KeyError:
            raise SchemaError('Bad field type "%s"' % str(field_type))
        else:
            # TODO: add validators if needed?
            # validators = process_validators(field_attrs.pop('validators', {}))
            instance = field(field_name, validators=[], **field_attrs)
            return instance


def process_fields(raw_fields):
    fields = [process_field(f, attrs) for f, attrs in raw_fields.iteritems()]
    return fields
