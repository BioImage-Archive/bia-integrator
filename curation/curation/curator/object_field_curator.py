from pydantic import BaseModel

from curation.curator.base_object_curator import ObjectCurator
from curation.directive.base_directive import Directive
from curation.directive.field_directive import FieldCommand, FieldDirective


class ObjectFieldCurator(ObjectCurator):

    def update(self, target_object: BaseModel, directive: Directive):
        if not isinstance(directive, FieldDirective):
            raise TypeError

        match directive.command:
            case FieldCommand.SET_FIELD:
                target_object = self._set_fields(
                    api_object=target_object, directive=directive
                )
            case _:
                raise NotImplementedError

        return target_object

    def _set_fields(self, api_object: BaseModel, directive: FieldDirective):
        object_model_type = type(api_object)
        object_dict = api_object.model_dump()
        for field in directive.object_fields:
            object_dict[field] = directive.object_fields[field]
        return object_model_type.model_validate(object_dict)
