## Setup

In this directory, run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Setup local

```sh
# Note that only config.json is gitignored
cp src/template_config.json src/config.json

# change with actual credentials
# object key is environment name
vim src/config.json

## Example run
# note --env position (it's an option for the main "app")
# defaults to dev
poetry run python src/migration.py --env=beta studies recount EMPIAR-10988
```

## Migrating data repo to api on local

1. Follow the api readme to get an api instance running.
2. Run `python src/migration.py --env=beta studies migrate_all` to migrate all studies
3. To avoid the start-from-scratch requirement during debugging, `python src/migration.py --env=beta studies migrate_one S-BIAD234` will only migrate the two studies (or any number of studies given as space-delimited parameters) but will still fail for any conflict and the environment will need to be recreated
4. To see other options use the help `python src/migration.py studies --help`
## Recreating the environment

The migration assumes everything works - either because necessary adjustments are already in the code or studies that need to be skipped are removed. If anything breaks, **all the api data needs to be deleted** before it can be re-run after fixing. This is to simplify this one-off operation.

Also, please check the `migration.py` code if fields are actually mapped correctly (especially that uuids are not generated when they shouldn't be), and also check that the api data is as expected with `biaint`. Please make note of all odd ifs (if any), and 

To reset all api data, run `./env_reset.sh`
