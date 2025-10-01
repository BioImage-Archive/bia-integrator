from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from pathlib import Path


class PointAnnotationProposal(BaseModel):
    annotation_data_uuid: UUID
    image_representation_uuid: UUID
    mode: str
    x_column: str | int
    y_column: str | int
    z_column: str | int
    filter_column: str | None = None
    filter_value: str | None = None
    local_file_path: Path | None = None

    model_config = ConfigDict(frozen=True, extra="ignore")


class BasePointAnnotationProposal(BaseModel):
    """
    Likely an incomplete PointAnnotationProposal, that needs to be merged with a GroupedPointAnnotationProposal
    to create a valid PointAnnotationProposal
    """

    annotation_data_uuid: UUID | None = None
    image_representation_uuid: UUID | None = None
    mode: str | None = None
    x_column: str | int | None = None
    y_column: str | int | None = None
    z_column: str | int | None = None
    filter_column: str | None = None
    filter_value: str | None = None
    local_file_path: Path | None = None

    model_config = ConfigDict(frozen=True, extra="forbid")


class GroupedPointAnnotationProposal(BasePointAnnotationProposal):
    proposal: list[BasePointAnnotationProposal] = Field(default_factory=list)

    model_config = ConfigDict(frozen=True, extra="forbid")

    def flatten(self) -> list[PointAnnotationProposal]:
        """
        Return a list of complete PointAnnotationProposal per BasePointAnnotationProposal under self.proposal.
        Will prefer to use any values in the idividual BasePointAnnotationProposal, but fall back to the equivalent
        ones defined in the GroupedPointAnnotationProposal.
        """

        point_annotation_proposal_list = []
        for individual_proposal in self.proposal:
            individual_proposal_overriden_values = {
                individual_proposal_key: individual_proposal_value
                for individual_proposal_key, individual_proposal_value in individual_proposal.model_dump().items()
                if individual_proposal_value is not None
            }

            merged_proposal_dict = (
                self.model_dump() | individual_proposal_overriden_values
            )

            point_annotation_proposal_list.append(
                PointAnnotationProposal(**merged_proposal_dict)
            )

        if point_annotation_proposal_list == []:
            point_annotation_proposal_list.append(
                PointAnnotationProposal(**self.model_dump())
            )

        return point_annotation_proposal_list
