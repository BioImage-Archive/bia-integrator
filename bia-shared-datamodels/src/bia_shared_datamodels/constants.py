from typing import Dict

# ---- Link type constants ----
ARRAYDESIGN_LINK_TYPE = "Array Design"
ARRAYEXPRESS_LINK_TYPE = "ArrayExpress"
BIOPROJECT_LINK_TYPE = "BioProject"
BIOSAMPLES_LINK_TYPE = "BioSamples"
BIOSTUDIES_LINK_TYPE = "BioStudies"
CHEBI_LINK_TYPE = "ChEBI"
CHEMAGORA_LINK_TYPE = "ChemAgora"
COMPOUND_LINK_TYPE = "Compound"
DBSNP_LINK_TYPE = "dbSNP"
DOI_LINK_TYPE = "DOI"
EGA_LINK_TYPE = "EGA"
ENA_LINK_TYPE = "ENA"
EMPIAR_LINK_TYPE = "EMPIAR"
ENSEMBL_LINK_TYPE = "Ensembl"  # Missing url template
EXPRESSIONATLAS_LINK_TYPE = "Expression Atlas"
EXPRESSIONATLAS_SC_LINK_TYPE = "Expression Atlas (Single Cell)"
EXTERNAL_LINK_TYPE = "External"  # Missing url template
GEO_LINK_TYPE = "GEO"
GENEONTOLOGY_LINK_TYPE = "Gene Ontology"
IDR_LINK_TYPE = "IDR"
INTACT_LINK_TYPE = "IntAct"
INTERPRO_LINK_TYPE = "InterPro"
NCT_LINK_TYPE = "NCT"
NUCLEOTIDE_LINK_TYPE = "Nucleotide"
OMIM_LINK_TYPE = "OMIM"
PDBE_LINK_TYPE = "PDBe"
PFAM_LINK_TYPE = "Pfam"
RFAM_LINK_TYPE = "Rfam"
RNACENTRAL_LINK_TYPE = "RNAcentral"
SOURCE_DATA_LINK_TYPE = "SourceData"  # Missing url template
UNIPROT_LINK_TYPE = "UniProt"

# ---- URL templates ----
ARRAYDESIGN_URL_TEMPLATE = "https://www.ebi.ac.uk/arrayexpress/arrays/{0}"
ARRAYEXPRESS_URL_TEMPLATE = "https://www.ebi.ac.uk/arrayexpress/experiments/{0}"
BIOPROJECT_URL_TEMPLATE = "https://www.ncbi.nlm.nih.gov/bioproject/{0}"
BIOSAMPLES_URL_TEMPLATE = "https://www.ebi.ac.uk/biosamples/samples/{0}"
BIOSTUDIES_URL_TEMPLATE = "https://www.ebi.ac.uk/biostudies/studies/{0}"
CHEBI_URL_TEMPLATE = "https://www.ebi.ac.uk/chebi/searchId.do?chebiId={0}"
CHEMAGORA_URL_TEMPLATE = "http://chemagora.jrc.ec.europa.eu/chemagora/inchikey/{0}"
COMPOUND_URL_TEMPLATE = "https://www.ebi.ac.uk/biostudies/studies/{0}"
DBSNP_URL_TEMPLATE = "http://www.ncbi.nlm.nih.gov/SNP/snp_ref.cgi?rs={0}"
DOI_URL_TEMPLATE = "https://dx.doi.org/{0}"
EGA_URL_TEMPLATE = "https://www.ebi.ac.uk/ega/studies/{0}"
ENA_URL_TEMPLATE = "https://www.ebi.ac.uk/ena/browser/view/{0}"
EMPIAR_URL_TEMPLATE = "https://www.ebi.ac.uk/empiar/{0}/"
EXPRESSIONATLAS_URL_TEMPLATE = (
    "https://www.ebi.ac.uk/gxa/experiments/{0}?ref=biostudies"
)
EXPRESSIONATLAS_SC_URL_TEMPLATE = (
    "https://www.ebi.ac.uk/gxa/sc/experiments/{0}?ref=biostudies"
)
GEO_URL_TEMPLATE = "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}"
GENEONTOLOGY_URL_TEMPLATE = "http://amigo.geneontology.org/amigo/term/{0}"
IDR_URL_TEMPLATE = "https://idr.openmicroscopy.org/search/?query=Name:{0}"
INTACT_URL_TEMPLATE = "https://www.ebi.ac.uk/intact/interaction/{0}"
INTERPRO_URL_TEMPLATE = "https://www.ebi.ac.uk/interpro/entry/{0}"
NCT_URL_TEMPLATE = "https://clinicaltrials.gov/ct2/show/{0}"
NUCLEOTIDE_URL_TEMPLATE = "http://www.ncbi.nlm.nih.gov/nuccore/{0}"
OMIM_URL_TEMPLATE = "http://omim.org/entry/{0}"
PDBE_URL_TEMPLATE = "https://www.ebi.ac.uk/pdbe-srv/view/entry/{0}/summary"
PFAM_URL_TEMPLATE = "http://pfam.xfam.org/family/{0}"
RFAM_URL_TEMPLATE = "http://rfam.org/family/{0}"
RNACENTRAL_URL_TEMPLATE = "http://rnacentral.org/rna/{0}"
UNIPROT_URL_TEMPLATE = "https://www.uniprot.org/uniprot/{0}"

# ---- LINKTYPE_DISPLAY mapping ----
LINKTYPE_DISPLAY: Dict[str, str] = {
    "array design": ARRAYDESIGN_LINK_TYPE,
    "arrayexpress": ARRAYEXPRESS_LINK_TYPE,
    "bioproject": BIOPROJECT_LINK_TYPE,
    "biosample": BIOSAMPLES_LINK_TYPE,
    "biostudies": BIOSTUDIES_LINK_TYPE,
    "chebi": CHEBI_LINK_TYPE,
    "chemagora": CHEMAGORA_LINK_TYPE,
    "compound": COMPOUND_LINK_TYPE,
    "doi": DOI_LINK_TYPE,
    "ega": EGA_LINK_TYPE,
    "empiar": EMPIAR_LINK_TYPE,
    "ena": ENA_LINK_TYPE,
    "ensembl": ENSEMBL_LINK_TYPE,
    "": EXTERNAL_LINK_TYPE,
    "geo": GEO_LINK_TYPE,
    "gxa": EXPRESSIONATLAS_LINK_TYPE,
    "gxa-sc": EXPRESSIONATLAS_SC_LINK_TYPE,
    "idr": IDR_LINK_TYPE,
    "intact": INTACT_LINK_TYPE,
    "interpro": INTERPRO_LINK_TYPE,
    "nct": NCT_LINK_TYPE,
    "omim": OMIM_LINK_TYPE,
    "pdb": PDBE_LINK_TYPE,
    "pfam": PFAM_LINK_TYPE,
    "refsnp": DBSNP_LINK_TYPE,
    "refseq": NUCLEOTIDE_LINK_TYPE,
    "rfam": RFAM_LINK_TYPE,
    "rnacentral": RNACENTRAL_LINK_TYPE,
    "sourcedata": SOURCE_DATA_LINK_TYPE,
    "sprot": UNIPROT_LINK_TYPE,
}

# ---- Allowed link types ----
ALLOWED_LINK_TYPES: Dict[str, str] = {v.lower(): v for v in LINKTYPE_DISPLAY.values()}

# ---- Dictionaries ----
URL_TEMPLATES: Dict[str, str] = {
    ARRAYDESIGN_LINK_TYPE.lower(): ARRAYDESIGN_URL_TEMPLATE,
    ARRAYEXPRESS_LINK_TYPE.lower(): ARRAYEXPRESS_URL_TEMPLATE,
    BIOPROJECT_LINK_TYPE.lower(): BIOPROJECT_URL_TEMPLATE,
    BIOSAMPLES_LINK_TYPE.lower(): BIOSAMPLES_URL_TEMPLATE,
    BIOSTUDIES_LINK_TYPE.lower(): BIOSTUDIES_URL_TEMPLATE,
    CHEBI_LINK_TYPE.lower(): CHEBI_URL_TEMPLATE,
    CHEMAGORA_LINK_TYPE.lower(): CHEMAGORA_URL_TEMPLATE,
    COMPOUND_LINK_TYPE.lower(): COMPOUND_URL_TEMPLATE,
    DBSNP_LINK_TYPE.lower(): DBSNP_URL_TEMPLATE,
    DOI_LINK_TYPE.lower(): DOI_URL_TEMPLATE,
    EGA_LINK_TYPE.lower(): EGA_URL_TEMPLATE,
    ENA_LINK_TYPE.lower(): ENA_URL_TEMPLATE,
    EMPIAR_LINK_TYPE.lower(): EMPIAR_URL_TEMPLATE,
    EXPRESSIONATLAS_LINK_TYPE.lower(): EXPRESSIONATLAS_URL_TEMPLATE,
    EXPRESSIONATLAS_SC_LINK_TYPE.lower(): EXPRESSIONATLAS_SC_URL_TEMPLATE,
    GEO_LINK_TYPE.lower(): GEO_URL_TEMPLATE,
    GENEONTOLOGY_LINK_TYPE.lower(): GENEONTOLOGY_URL_TEMPLATE,
    IDR_LINK_TYPE.lower(): IDR_URL_TEMPLATE,
    INTACT_LINK_TYPE.lower(): INTACT_URL_TEMPLATE,
    INTERPRO_LINK_TYPE.lower(): INTERPRO_URL_TEMPLATE,
    NCT_LINK_TYPE.lower(): NCT_URL_TEMPLATE,
    NUCLEOTIDE_LINK_TYPE.lower(): NUCLEOTIDE_URL_TEMPLATE,
    OMIM_LINK_TYPE.lower(): OMIM_URL_TEMPLATE,
    PDBE_LINK_TYPE.lower(): PDBE_URL_TEMPLATE,
    PFAM_LINK_TYPE.lower(): PFAM_URL_TEMPLATE,
    RFAM_LINK_TYPE.lower(): RFAM_URL_TEMPLATE,
    RNACENTRAL_LINK_TYPE.lower(): RNACENTRAL_URL_TEMPLATE,
    UNIPROT_LINK_TYPE.lower(): UNIPROT_URL_TEMPLATE,
}
