
from pydantic import BaseModel

from curation.curator.base_object_curator import ObjectCurator
from curation.directive.attribute_directive import (
    AttributeCommand,
    AttributeDirective,
)
from curation.directive.base_directive import Directive


class ObjectAttributeCurator(ObjectCurator):

    def update(self, target_object: BaseModel, directive: Directive):
        if not isinstance(directive, AttributeDirective):
            raise TypeError
        
        match directive.command:
            case AttributeCommand.UPDATE_ATTRIBUTE:
                target_object = self._update_attribute(api_object=target_object, directive=directive)
            case AttributeCommand.ADD_ATTRIBUTE:
                target_object = self._add_attribute(api_object=target_object, directive=directive)
            case AttributeCommand.DELETE_ATTRIBUTE:
                target_object = self._delete_attribute(api_object=target_object, directive=directive)
            case _:
                raise NotImplementedError
        
        return target_object


    def _add_attribute(self, api_object: BaseModel, directive: AttributeDirective):
        attribute_from_directive = directive.assemble_attribute()
        api_object.additional_metadata.append(attribute_from_directive)
        return api_object

    def _delete_attribute(self, api_object, directive: AttributeDirective, error_on_missing: bool=True):
 
        updated_attribute_list = []
        for attribute in api_object.additional_metadata:
            if not (attribute.name == directive.name and attribute.provenance == directive.provenance):
                updated_attribute_list.append(attribute)

        if error_on_missing and len(updated_attribute_list) != len(api_object.additional_metadata) - 1:
            raise LookupError

        api_object.additional_metadata = updated_attribute_list

        return api_object
    
    def _update_attribute(self, api_object, directive: AttributeDirective):

        api_object = self._delete_attribute(api_object=api_object, directive=directive, error_on_missing=False)
        api_object = self._add_attribute(api_object=api_object, directive=directive)

        return api_object
    
    