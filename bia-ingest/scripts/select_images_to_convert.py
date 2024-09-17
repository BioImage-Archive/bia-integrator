"""Ad hoc script to select images to convert based on size"""

import sys
from bia_ingest.config import api_client
from bia_ingest.image_utils.image_utils import in_bioformats_single_file_formats_list


# From https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


accession_id = sys.argv[1]
# file_reference_path = Path(settings.bia_data_dir) / "file_references" / accession_id
# file_reference_names = [ frp for frp in file_reference_path.glob("*.json")]
# mongodb_serialiser = MongodbSerialisation(api_client)
# mongodb_serialiser = MongodbSerialiser(api_client)
studies = api_client.get_studies()
study = next(s for s in studies if s.accession_id == accession_id)
eids = api_client.get_experimental_imaging_dataset_in_study(study.uuid)
file_references = []
for eid in eids:
    file_references.extend(
        api_client.get_file_reference_in_experimental_imaging_dataset(eid.uuid)
    )
# disk_serialiser = DiskSerialiser(accession_id=accession_id, output_dir_base=settings.bia_data_dir)

# file_references = disk_serialiser.deserialise_by_uuid([f"{fr}".split(".")[0] for fr in file_reference_names], bia_data_model.FileReference)

convertible_file_references = [
    {
        "name": fr.file_path,
        "uuid": fr.uuid,
        "size_in_bytes": fr.size_in_bytes,
        "size_human_readable": sizeof_fmt(fr.size_in_bytes),
    }
    for fr in file_references
    if in_bioformats_single_file_formats_list(fr.file_path)
]

convertible_file_references = sorted(
    convertible_file_references, key=lambda fr: fr["size_in_bytes"], reverse=True
)
for cfr in convertible_file_references:
    print(
        f"{cfr['name']}\t{cfr['uuid']}\t{cfr['size_in_bytes']}\t{cfr['size_human_readable']}"
    )
