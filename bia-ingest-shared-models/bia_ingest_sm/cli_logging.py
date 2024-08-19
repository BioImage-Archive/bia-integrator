from rich.table import Table
from rich.text import Text
from .config import ObjectValidationResult

def tabulate_errors(dict_of_results: dict[ObjectValidationResult]) -> Table:
    table = Table("Accession ID", "Status", "Errors")
    for accession_id_key in dict_of_results:
        error_message = ""
        validation_result: ObjectValidationResult = dict_of_results[accession_id_key]
        errors = validation_result.model_dump()
        for field, value in errors.items():
            if value > 0:
                error_message += f"{field}: {value}; "
    
        if error_message == "":
            status = Text("Success")
            status.stylize("green")
        else:
            status = Text("Failures")
            status.stylize("red")
            error_message = Text(error_message)
            error_message.stylize("red")   

        table.add_row(accession_id_key, status, error_message)

    return table