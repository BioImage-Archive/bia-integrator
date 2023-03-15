from fastapi import FastAPI

from bia_integrator_core.interface import get_all_study_identifiers
from bia_integrator_core.integrator import load_and_annotate_study
app = FastAPI()


@app.get("/studies/show/{accession_id}")
async def show_study(accession_id: str):
    bia_study = load_and_annotate_study(accession_id)
    return bia_study
    

@app.get("/studies/list")
async def list_studies():
    all_study_identifiers = get_all_study_identifiers()
    return sorted(all_study_identifiers)


@app.get("/")
async def root():
    return {"message": "Hello World"}