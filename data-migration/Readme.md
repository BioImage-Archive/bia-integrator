## Setup

In this directory, run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Migrating data repo to api on local

1. Follow the api readme to get an api instance running.
2. Run `python migration.py` to migrate all studies
3.  To avoid the start-from-scratch requirement during debugging, `python migration.py S-BIAD123 S-BIAD234` will only migrate the two studies (or any number of studies given as space-delimited parameters) but will still fail for any conflict and the environment will need to be recreated

## Recreating the environment

The migration assumes everything works - either because necessary adjustments are already in the code or studies that need to be skipped are removed. If anything breaks, **all the api data needs to be deleted** before it can be re-run after fixing. This is to simplify this one-off operation.

Also, please check the `migration.py` code if fields are actually mapped correctly (especially that uuids are not generated when they shouldn't be), and also check that the api data is as expected with `biaint`. Please make note of all odd ifs (if any), and 

To reset all api data, run `./env_reset.sh`