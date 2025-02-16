#!/bin/bash
# Given an accession ID, propose images, assign and convert
#   e.g. source assign_and_convert_images.sh S-BIAD686
# Optionally, to skip propose images step also give path to proposal file
#   e.g. source assign_and_convert_images.sh S-BIAD686 /home/bia_svc/temp/propose_images_S-BIAD686.tsv
# Assumes the script is being run in this directory and env variables in ./set_local_env_template.sh are set

accession_id=$1
propose_images_output=""
if [ $# -gt 1 ]; then
    propose_images_output=$2
fi

n_images_to_convert=5
artefact_dir_base=~/temp/assign_and_convert

if [ ! -d $artefact_dir_base ]; then
    mkdir -p $artefact_dir_base
    mkdir -p $artefact_dir_base/logs
fi

# Directory to store log outputs from conversion. Used to get uuids for next stage
logs_dir_base="$artefact_dir_base/logs/$accession_id"
if [ ! -d $logs_dir_base ]; then
    mkdir -p $logs_dir_base
fi

# Put these in a set_environment.sh file and source
bia_assign_image_dir=../../bia-assign-image
bia_converter_dir=../
update_example_image_uri_script_path=$(realpath update_example_image_uri_for_dataset.py)
# Create proposals if the location of a proposals file was not specified
if [ -z "$propose_images_output" ]; then
    propose_images_output="$artefact_dir_base/propose_$accession_id.tsv"
    command="poetry --directory $bia_assign_image_dir run bia-assign-image propose-images --no-append --max-items $n_images_to_convert $accession_id $propose_images_output"

    echo $command
    eval $command
fi

# Assign Images from proposals
assign_from_proposals_output="$logs_dir_base/assign_from_proposal_output.txt"
command="poetry --directory $bia_assign_image_dir run bia-assign-image assign-from-proposal $propose_images_output 2>&1 | tee $assign_from_proposals_output"
echo $command
eval $command

# Convert images
image_uuids=$(grep "Persisted image_representation" $assign_from_proposals_output | cut -d' ' -f3)
n_images_converted=0
for image_uuid in $image_uuids
do
    # Create interactive display representation
    convert_to_interactive_display_output="$logs_dir_base/convert_to_interactive_display_output.txt"
    command='poetry --directory '"$bia_converter_dir"' run bia-converter convert '"$image_uuid"' INTERACTIVE_DISPLAY 2>&1 | tee '"$convert_to_interactive_display_output"'; echo exit_status=${PIPESTATUS[0]}'
    echo $command;
    eval_output=$(eval "$command")
    echo $eval_output
    exit_status=$(echo $eval_output | grep -oP 'exit_status=\K[0-9]+')

    if [ "$exit_status" = "0" ]; then
        ((n_images_converted++))
        interactive_display_uuid=$(grep -oP 'Created INTERACTIVE_DISPLAY image representation with uuid: \K[0-9a-fA-F-]+' $convert_to_interactive_display_output)
        # Create static display representatino and update example image uri if this is first image converted
        if [ "$n_images_converted" -eq 1 ]; then
            convert_to_static_display_output="$logs_dir_base/convert_to_static_display_output.txt"
            command="poetry --directory $bia_converter_dir run bia-converter convert $interactive_display_uuid STATIC_DISPLAY 2>&1 | tee $convert_to_static_display_output"
            echo $command
            eval $command

            static_display_uuid=$(grep -oP 'Created STATIC_DISPLAY image representation with uuid: \K[0-9a-fA-F-]+' $convert_to_static_display_output)
            command="poetry --directory $bia_converter_dir run python $update_example_image_uri_script_path --update-mode replace $static_display_uuid"
            echo $command
            eval $command
        fi

        # Create thumbnail representation
        convert_to_thumbnail_output="$logs_dir_base/convert_to_thumbnail.txt"
        command="poetry --directory $bia_converter_dir run bia-converter convert $interactive_display_uuid THUMBNAIL 2>&1 | tee $convert_to_thumbnail_output"
        echo $command
        eval $command
    fi
done
