import os
import yaml
import pytest_check as check

from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner
from annotation_data_converter.cli import annotation_data_convert
from curation.writer.yaml_directive_writer import YamlDirectiveWriter

runner = CliRunner()


def test_starfile_convert_to_neuroglancer(data_in_api, tmp_bia_data_dir):
    
    # Mock functions for getting image info (because no real s3 image to find) and to avoid writing directives in curation package
    def mock_get_image_info(image_uri):
        """Return fake but plausible OME image metadata"""
        contrast_bounds = (0.0, 1.0)
        image_resolution = (1024, 1024, 1)  # x, y, z
        voxels = {'t': 1, 'c': 1, 'z': 1, 'y': 1024, 'x': 1024}
        channel_info = None
        return contrast_bounds, image_resolution, voxels, channel_info
    
    def mock_write_to_tmp(directives):
        """Write directives to temp directory instead of curation"""
        output_path = tmp_bia_data_dir / "test_directive.yaml"
        directive_writer = YamlDirectiveWriter()
        directive_writer.update(output_path, directives)
    
    with patch('annotation_data_converter.point_annotations.converters.PointAnnotationConverter.get_image_info_from_ome', side_effect=mock_get_image_info), \
        patch('annotation_data_converter.cli.write_directives', side_effect=mock_write_to_tmp):
        
        commands = [
            "convert", 
            "-p",
            "proposals/point_annotations/test_proposal.json",
            "-od",
            str(tmp_bia_data_dir), 
            "-om",
            "dry_run", 
            "-am",
            "local", 
        ]

        result = runner.invoke(annotation_data_convert, commands)
        assert result.exit_code == 0

        # The actual path structure is: annotations/{accession_id}/{image_uuid}/{annotation_data_uuid}
        # Where accession_id is "point_annotations" and image_uuid is "f0444894-c673-458c-a07d-fd63994fce1e"
        image_uuid = "f0444894-c673-458c-a07d-fd63994fce1e"
        base_path = tmp_bia_data_dir / "annotations" / "point_annotations" / image_uuid
        
        expected_annotation_uuids = [
            "35c60bfa-6f41-46ef-b058-7b2207d681af",
            "15402ddb-30db-459b-9e2d-3a16479de8c4",
            "dc76699b-a366-4062-8084-e0cab772fa36",
        ]

        for annotation_uuid in expected_annotation_uuids:
            folder_path = base_path / annotation_uuid
            check.is_true(os.path.exists(folder_path), msg=f"Folder {folder_path} should exist")
            check.is_true(os.path.exists(folder_path / "info"), msg=f"Info file should exist in {folder_path}")
            check.is_true(len(os.listdir(folder_path/"by_id")) > 0, msg=f"by_id should have contents in {folder_path}")
            check.is_true(len(os.listdir(folder_path/"spatial0")) > 0, msg=f"spatial0 should have contents in {folder_path}")
        
        directive_file = tmp_bia_data_dir / "test_directive.yaml"
        check.is_true(directive_file.exists(), msg="Directive file should be created")
        
        with open(directive_file, 'r') as f:
            actual_directive = yaml.safe_load(f)
        
        expected_path = Path(__file__).parent / "output_data" / "curation_directive.yaml"
        with open(expected_path, 'r') as f:
            expected_directive = yaml.safe_load(f)
        
        # NOTE: Because of clashing directives in the expected file, we only check for one directive match
        # This tests that clashes are detected, but could be improved to test directives individually (and clashes too)
        check.equal(len(actual_directive), 1, msg="Should have 1 directive (clashing directives resolved)")
        
        actual = actual_directive[0]
        expected = expected_directive[0]
        
        check.equal(str(actual['target_uuid']), expected['target_uuid'], 
                   msg="target_uuid should match")
        check.equal(actual['object_type'], expected['object_type'],
                   msg="object_type should match")
        check.equal(actual['command'], expected['command'],
                   msg="command should match")
        check.equal(actual['provenance'], expected['provenance'],
                   msg="provenance should match")
        check.equal(actual['name'], expected['name'],
                   msg="name should match")
        check.equal(actual['value'], expected['value'],
                   msg="neuroglancer link should match")
        
        actual_attr = actual.get('attribute_model')
        expected_attr = expected.get('attribute_model')
        check.equal(actual_attr, expected_attr, msg="attribute_model should match")
