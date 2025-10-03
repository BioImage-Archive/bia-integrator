import rdflib
import pathlib
import logging
from urllib.parse import urljoin

logger = logging.getLogger("__main__." + __name__)


def get_dataset_for_filelist(
    file_list_id: str, graph: rdflib.Graph, crate_path: pathlib.Path
) -> str:
    pathlib_path_uri = pathlib.Path(crate_path).absolute().as_uri() + "/"
    file_list_rdf_ref = urljoin(pathlib_path_uri, file_list_id)
    subjects = list(
        graph.subjects(
            rdflib.URIRef("http://bia/associationFileMetadata"), rdflib.URIRef(file_list_rdf_ref)
        )
    )
    if len(subjects) == 1:
        parent_id = pathlib.Path.from_uri(str(subjects[0])).relative_to(crate_path)
        return f"{str(parent_id)}/"
    else:
        raise ValueError(
            f"Incorrect number of datasets found for filelist {file_list_id}. Please check the RO-Crate metadata."
        )


def get_hasPart_parent_id_from_child(
    child_id: str, graph: rdflib.Graph, crate_path: pathlib.Path
) -> str:
    pathlib_path_uri = pathlib.Path(crate_path).absolute().as_uri() + "/"
    child_rdf_ref = urljoin(pathlib_path_uri, child_id)
    subjects = list(
        graph.subjects(
            rdflib.URIRef("http://schema.org/hasPart"), rdflib.URIRef(child_rdf_ref)
        )
    )
    if len(subjects) == 0:
        logger.exception(f"No dataset found for image {child_id}.")
        raise ValueError(
            f"No dataset found for hasPart object: {child_id}. Please check the RO-Crate metadata."
        )
    elif len(subjects) > 1:
        logger.exception(f"Multiple datasets found for image {child_id}.")
        raise ValueError(
            f"Multiple datasets found for hasPart object: {child_id}. Please check the RO-Crate metadata."
        )
    else:
        parent_id = pathlib.Path.from_uri(str(subjects[0])).relative_to(crate_path)
        return f"{str(parent_id)}/"


def ro_crate_data_entity_id_to_uri(crate_base_path, entity_id) -> str:
    crate_base_path_uri = pathlib.Path(crate_base_path).absolute().as_uri() + "/"
    entity_uri = urljoin(crate_base_path_uri, entity_id)
    return entity_uri


def ro_crate_data_entity_id_to_path(crate_base_path, entity_id) -> pathlib.Path:
    entity_uri = ro_crate_data_entity_id_to_uri(crate_base_path, entity_id)
    return pathlib.Path().from_uri(entity_uri)
