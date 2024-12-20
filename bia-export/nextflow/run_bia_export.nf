// Run export of study, dataset and image metadata

// default dry_run to FALSE
params.dry_run = false //"DRY_RUN: "

process run_export_scripts {
    // errorStrategy {
    //     sleep(Math.pow(2, task.attempt) * 200 as long);
    //     return 'retry'
    // }
    // maxRetries 3

    errorStrategy 'ignore'

    debug true

    input:
    each study_uuid_chunk

    script:

    rows = study_uuid_chunk[0]

    """
            #source ${params.bia_export_dir}/nextflow/set_local_env.sh
            for row in $rows
            do
                study_uuid=\$(echo \$row | cut -d':' -f1)
                accession_id=\$(echo \$row | cut -d':' -f2)
                study_metadata_outpath="${params.output_dir_base}/bia-study-metadata-\$accession_id.json"
                dataset_metadata_outpath="${params.output_dir_base}/bia-dataset-metadata-\$accession_id.json"
                image_metadata_outpath="${params.output_dir_base}/bia-image-export-\$accession_id.json"
                command="poetry --directory $params.bia_export_dir run bia-export website-study -o \$study_metadata_outpath \$study_uuid"
                command="\$command && poetry --directory $params.bia_export_dir run bia-export datasets-for-website-image -o \$dataset_metadata_outpath \$study_uuid"
                command="\$command && poetry --directory $params.bia_export_dir run bia-export website-image -o \$image_metadata_outpath \$study_uuid"
                if [ $params.dry_run = true ]; then
                    echo "DRY_RUN: \$command"
                else
                    eval \$command
                fi
            done
    """
}

// The manifest file is a text file with no header and rows of study_uuid:accession_id
// We want to run export for each study separately as code crashes on error of a single one
n_elements_per_job = 1

workflow {
    Channel.fromPath(params.manifest_path)
        .splitText()
        .map({ it.trim() })
        .collate( n_elements_per_job ) // Ensure even single items are passed as an array
        | set { study_uuid_chunks }
    run_export_scripts(study_uuid_chunks)

}
