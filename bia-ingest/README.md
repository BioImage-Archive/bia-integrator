## Installation
1. Install the project using poetry.
2. Configure your environment (Optional if only persisting to disk, required if persisting/reading from the BIA API)
   Either create a .env file from .env_template or set environment variables for the items in .env_template.
    * In order to use the API for reading/persisting models set:
        - bia_api_basepath
        - bia_api_username
        - bia_api_password
    * When reading/persisting to disk the default location is `~/.cache/bia-integrator-data-sm/`. This can be changed by setting `bia_data_dir`.

## Ingest Commands
To create BIA API objects from one or more biostudies submissions, assuming the package was installed via poetry and you are running from the same directory as this readme, run:
```sh
$ poetry run biaingest ingest <LIST OF STUDY ACCESSION IDs>
```
E.g:
```sh
$ poetry run biaingest ingest S-BIAD1285 S-BIAD1316
```
Or can input a file of newline separated accesssion ids with -f:
```sh
$ poetry run biaingest ingest -f input_files/ingested_submissions
```

By default this will create objects on disk (`--persistence-mode disk`).
This creates the following structure (using S-BIAD325 as an example):
```sh
~/.cache/bia-integrator-data-sm/
  study/S-BIAD1285/
    study_uuid.json
  file_reference/S-BIAD1285/
    file_reference_1_uuid.json
    file_reference_2_uuid.json
    ...
  experimental_imaging_dataset/S-BIAD1285/
    experimental_imaging_dataset_1_uuid.json
    experimental_imaging_dataset_2_uuid.json
    ...
  bio_sample/S-BIAD1285/
    bio_sample_1_uuid.json
    bio_sample_1_uuid.json
    ...
```

To ingest into your local api, first set up the local api with
```sh
$ docker compose up --wait --build -d
```
and run ingest with the persistence-mode to `local-api`:
```sh
$ poetry run biaingest ingest --persistence-mode local-api S-BIAD1285
```

To ingest to the wwwdev api (the main one currently in use), you need to have a user account on the dev API. You can then copy the .env_template file to .env, and fill in the details (email and password) of your user account. Then, to ingest, you can run:
```sh
$ poetry run biaingest ingest --persistence-mode api S-BIAD1285
```

To run ingest without either saving to disk or writing to the api run with --dryrun:
```sh
$ poetry run biaingest ingest --dryrun S-BIAD1285
```

### Filelist processing settings

Some studies have huge filelists, which can cause issues when running locally. Therefore, there is a --process-filelist setting to control how file lists are handled (and therefore whether FileReferences get generated). The default value, "ask", will prompt the user with a y/n question for studies that have more than 200,000 files. "skip" avoids attempting to even download or process the filelist. "always" processes the filelist regardless of number of files in the study. An example of skipping, e.g. for debugging, alongside the dryrun option would be:
```sh
$ poetry run biaingest ingest --dryrun --process-filelist skip S-BIAD1285
```
### Output Mode

There are two types of outputs:
 the comprehensive table for each accession or the simple output mode which will print out Accession ID, Status, Message.

You can set the output mode by sepcifiyng `-om` or `--output-mode`.

For example

```sh
$ poetry run biaingest ingest --dryrun - --process-filelist skip -om simple S-BIAD1285
```
will output the following:

```log
S-BIAD1285, Success,
```
In case of success or
```log
S-BIAD1285, Failures, Error message
```
otherwise.
By default the output mode is set to table.

### Results table & object count
When ingest finishes a table of results is printed out. To also get this table written to a csv (which can be useful when running ingest on a lot of studies), add the --write-csv option with the path of where to write out the file. You can also include a count of all the objects that were created with the --count/-c options:

```sh
$ poetry run biaingest ingest S-BIAD1285 S-BIAD1385 -c --write-csv output_table.csv
```

### Logging level

By default, the command logs only CRITICAL events.
To increase verbosity, use the `-l` option followed by a numeric level:

  0. CRITICAL only
  1. ERROR and CRITICAL
  2. WARNING, ERROR, and CRITICAL
  3. INFO, WARNING, ERROR, and CRITICAL
  4. DEBUG, INFO, WARNING, ERROR, and CRITICAL

Examples:

Show all logs:
```sh
$ poetry run biaingest command -l4
```
Show only warnings and above:
```sh
$ poetry run biaingest command -l2
```




## Getting new Biostudies Studies

run:
```bash
$ poetry run biaingest find new-biostudies-studies
```

which will create a file in the input_files/ directory of studies that are relevant to the current ingest process but are not yet ingested.


## Running ingestion in parallel

The script `parallel_ingest.py` allows you to run the command:

```bash
$ poetry run biaingest ingest --dryrun -om=simple --process-filelist=skip ${accession_id}
```

The `accession_id` values are stored in a JSON file containing a list of strings, each representing one accession ID.

Example:

```json
[
  "S-BIAD2197",
  "S-BIAD2279",
  "S-BIAD2277",
  "S-BIAD2273",
  "S-BIAD2275",
  "S-BIAD2272",
  "S-BIAD2271",
  "S-BIAD2248",
  "S-BIAD2247",
  "S-BIAD2246",
  "S-BIAD2245"
]

```

This is a standalone script, created because the original program was not built for parallel execution.

It produces two log files: `ingest_success.log` and `ingest_failure.log`, each containing the results of the processing described above.

Run the script as follows:

```bash
$ poetry run python parallel_ingest.py -json my_file.json -j 100
```

The `-j` option specifies the number of parallel processes to use.

If no `--json` file is provided, the script defaults to using `accessions.json`.
