from bia_test_data.mock_objects.utils import accession_id
from typer.testing import CliRunner
from bia_assign_image import cli
from bia_test_data.mock_objects import mock_file_reference
from bia_ingest.persistence_strategy import persistence_strategy_factory

def test_bia_assign_cli(monkeypatch, tmpdir):
    runner = CliRunner()
    file_reference_uuids = " ". join([str(f.uuid) for f in mock_file_reference.get_file_reference()])

    output_dir_base = tmpdir
    persister = persistence_strategy_factory(
        persistence_mode="disk",
        output_dir_base=str(output_dir_base),
        accession_id=accession_id,
    )
    persister.persist(mock_file_reference.get_file_reference())

    monkeypatch.setattr(cli, "output_dir_base", str(output_dir_base))
    result = runner.invoke(
        cli.app, [
            "assign",
            accession_id,
            file_reference_uuids,
        ],
    )
    print(result.stdout)
    assert result.exit_code == 0