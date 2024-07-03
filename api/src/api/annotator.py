from ..models.repository import Repository
from typing import Annotated, List
from fastapi import Depends, Query
from ..models import persistence as db_models


class Annotator:
    """
    Intended to keep all annotation-related params / functionality self-contained
    """

    apply_annotations: bool = False

    """
    Out of an abundance of caution, close the database connection as soon as any annotation is applied,
    To ensure annotated data can't accidentally be pushed back to the db, downstream of applying annotations, in the api
    """
    db: Repository

    async def __call__(
        self,
        db: Repository = Depends(),
        apply_annotations: Annotated[bool, Query()] = False,
    ):
        """
        Note that annotation application params need to be compatible with all HTTP verbs
        e.g. no Body()
        """
        self.apply_annotations = apply_annotations
        self.db = db

        return self

    def annotate_if_needed(
        self,
        response_object: (
            db_models.AnnotatedMixin | List[db_models.AnnotatedMixin]
        ) = False,
    ):
        if not self.apply_annotations:
            return

        self.db.close()
        if isinstance(response_object, list):
            for rsp_item in response_object:
                self._apply_annotations(rsp_item)
        else:
            self._apply_annotations(response_object)

    def _apply_annotations(self, response_object: db_models.AnnotatedMixin):
        response_object.annotations_applied = True

        document_attributes = set(response_object.__dict__.keys())

        reserved_attribute_names_for_all_models = [
            "model",
            "uuid",
            "annotations_applied",
            "version",
        ]
        for annotation in response_object.annotations:
            if annotation.key in reserved_attribute_names_for_all_models:
                raise Exception(
                    f"Annotation {annotation} of object {response_object.uuid} overwrites a read-only property"
                )

            # annotations that don't overwrite a field are 'annotation attributes'
            if annotation.key in document_attributes:
                if type(response_object.__dict__[annotation.key]) is list:
                    response_object.__dict__[annotation.key].append(annotation.value)
                else:
                    response_object.__dict__[annotation.key] = annotation.value
            else:
                response_object.attributes[annotation.key] = annotation.value


annotator = Annotator()
