from pydantic import BaseModel, Field
from rdflib.graph import Graph
from rdflib import RDF, OWL
from bia_shared_datamodels.linked_data.ld_context.ContextTerm import ContextTerm
from .FieldContext import FieldContext


class ObjectReference(BaseModel):
    id: str = Field(alias="@id")


class LDModel(BaseModel):

    @classmethod
    def generate_field_context(cls, compacted_ids: bool = False) -> list[ContextTerm]:
        # TODO: add support for various json-ld profiles / other context generation settings
        field_contexts = []

        for field_name, field_info in cls.model_fields.items():
            field_context = next(
                (m for m in field_info.metadata if isinstance(m, FieldContext)), None
            )

            if field_context:
                if compacted_ids and field_context.isIdField:
                    term = ContextTerm(
                        full_uri=field_context.uri,
                        field_name=field_name,
                        type_mapping="@id",
                    )
                else:
                    term = ContextTerm(
                        full_uri=field_context.uri, field_name=field_name
                    )

                field_contexts.append(term)

        return field_contexts

    @classmethod
    def validate_ontology_field_consistency(cls, ontology: Graph):
        # TODO: make this collect error and list all issues
        for field_name, field_info in cls.model_fields.items():
            field_context = next(
                (m for m in field_info.metadata if isinstance(m, FieldContext)), None
            )

            if field_context:
                # Check uri exists in ontology
                if field_context.uri not in ontology.subjects():
                    raise KeyError(
                        f"Field {field_name} has a context uri {field_context.uri} that is not in the ontology"
                    )

                # Check uri for field is a property
                if not any(
                    object_type
                    in [
                        OWL.ObjectProperty,
                        OWL.DatatypeProperty,
                        OWL.AnnotationProperty,
                        RDF.Property,
                    ]
                    for object_type in ontology.objects(field_context.uri, RDF.type)
                ):
                    raise ValueError(
                        f"Field {field_name} has a context uri {field_context.uri} that is not a property in the ontology"
                    )

            # TODO: add check that pydantic type is a reasonable match for the ontology type
            # TODO: add check that none of the inferred types of the model are owl:disjoint with each other
            # TODO: check for validation recursively in nested models, including that the inferred types from the parent model are compatible with the child model

    @classmethod
    def is_valid(cls, ontology: Graph):
        try:
            cls.validate_ontology_field_consistency(ontology)
        except Exception as e:
            return False

        return True
