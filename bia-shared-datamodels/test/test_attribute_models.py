import pytest
from pydantic import ValidationError
from bia_shared_datamodels import (
    semantic_models,
    mock_objects,
    attribute_models,
)
from typing import Callable


@pytest.mark.parametrize(
    ("expected_model_type", "dict_creation_func"),
    (
        (
            attribute_models.DatasetAssociatedUUIDAttribute,
            mock_objects.get_dataset_associated_uuid_attribute,
        ),
        (
            attribute_models.DatasetAssociationAttribute,
            mock_objects.get_dataset_associatation_attribute,
        ),
        (
            attribute_models.DocumentUUIDUinqueInputAttribute,
            mock_objects.get_document_uuid_uinque_input_attribute,
        ),
    ),
)
def test_sub_attribute_models(
    expected_model_type: semantic_models.Attribute,
    dict_creation_func: Callable[[mock_objects.Completeness], dict],
):

    model_completeness_list = [
        mock_objects.Completeness.COMPLETE,
        mock_objects.Completeness.MINIMAL,
    ]

    for model_completion in model_completeness_list:

        model_dict = dict_creation_func(model_completion)

        attribute_model = semantic_models.Attribute.model_validate(model_dict)
        sub_attribute_model = expected_model_type.model_validate(model_dict)

        # We have modified the __eq__ function, so it is good to check:
        assert sub_attribute_model == sub_attribute_model

        assert attribute_model.model_dump() == sub_attribute_model.model_dump()

        assert attribute_model == sub_attribute_model

        assert attribute_model == semantic_models.Attribute.model_validate(
            sub_attribute_model
        )

        # Check basic attribute doesn't pass validation
        try:
            expected_model_type.model_validate(
                mock_objects.get_attribute_dict(model_completion)
            )
            assert False
        except ValidationError:
            assert True
