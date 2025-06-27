import rdflib
import pathlib
import logging

logger = logging.getLogger("__main__." + __name__)


def get_hasPart_parent_id_from_child(
    child_id: str, graph: rdflib.Graph, crate_path: str
) -> str:
    pathlib_path = pathlib.Path(crate_path) / child_id
    child_rdf_ref = pathlib_path.absolute().as_uri()
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
        parent_id = pathlib.Path.from_uri(subjects[0]).relative_to(crate_path)
        return f"{str(parent_id)}/"
