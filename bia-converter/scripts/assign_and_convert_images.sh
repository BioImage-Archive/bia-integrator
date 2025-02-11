#!/bin/bash
# Given an accession ID, propose images, assign and convert
accession_id=$1
n_images_to_convert=5
artefact_dir_base=~/temp/assign_and_convert

if [ ! -d $artefact_dir_base ]; then
    mkdir -p $artefact_dir_base
fi

# Put these in a set_environment.sh file and source
bia_assign_image_dir=../../bia-assign-image
bia_converter_light_dir=../../bia-converter-light
bia_converter_dir=../

# Create proposals
propose_images_output="$artefact_dir_base/propose_$accession_id.tsv"
command="poetry --directory $bia_assign_image_dir run bia-assign-image propose-images --max-items $n_images_to_convert $accession_id $propose_images_output"

echo $command
eval $command

# Assign Images from proposals
assign_from_proposals_output="$artefact_dir_base/assign_from_proposal_output_$accession_id.txt"
command="poetry --directory $bia_assign_image_dir run bia-assign-image assign-from-proposal $propose_images_output 2>&1 | tee $assign_from_proposals_output"
echo $command
eval $command

# Convert images
image_uuids=$(grep "Persisted image_representation" $assign_from_proposals_output | cut -d' ' -f3)
n_images_converted=0
for image_uuid in $image_uuids
do
    # Create interactive display representation
    convert_to_interactive_display_output="$artefact_dir_base/convert_to_interactive_display_output.txt"
    command="poetry --directory $bia_converter_dir run bia-converter convert $image_uuid INTERACTIVE_DISPLAY 2>&1 | tee $convert_to_interactive_display_output"
    echo $command;
    eval $command;
    interactive_display_uuid=$(grep -oP 'Created INTERACTIVE_DISPLAY image representation with uuid: \K[0-9a-fA-F-]+' $convert_to_interactive_display_output)

    ((n_images_converted++))

    # Create statid display representatino and update example image uri if this is first image converted
    if [ "$n_images_converted" -eq 1 ]; then
        convert_to_static_display_output="$artefact_dir_base/convert_to_static_display_output.txt"
        command="poetry --directory $bia_converter_dir run bia-converter convert $interactive_display_uuid STATIC_DISPLAY 2>&1 | tee $convert_to_static_display_output"
        echo $command
        eval $command

        static_display_uuid=$(grep -oP 'Created STATIC_DISPLAY image representation with uuid: \K[0-9a-fA-F-]+' $convert_to_static_display_output)
        command="poetry --directory $bia_converter_light_dir run bia-converter-light update-example-image-uri-for-dataset $static_display_uuid"
        echo $command
        eval $command
    fi

    # Create thumbnail representation
    convert_to_thumbnail_output="$artefact_dir_base/convert_to_thumbnail.txt"
    command="poetry --directory $bia_converter_dir run bia-converter convert $interactive_display_uuid THUMBNAIL 2>&1 | tee $convert_to_interactive_display_output"
    echo $command
    eval $command
done
