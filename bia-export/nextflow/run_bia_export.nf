// Run export of study, dataset and image metadata

// default dry_run to FALSE
params.dry_run = false //"DRY_RUN: "

process run_export_scripts {
    // Commenting this block out as retries now implemented within
    // the bash script
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

    // ToDo: This is a terrible hack!!!
    //       Figure out how to iterate over elements in a channel!!!
    rows = study_uuid_chunk[0]
    //study_uuid_chunk.each { rows += (it[0] + ":" + it[1]) + " " }
    //study_uuid_chunk.each { rows += it + " " }

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
                    #source ${params.bia_export_dir}/nextflow/run_command_with_retry.sh
                    #run_command_with_retry "\$command" $params.timeout $params.n_tries $params.pause
                    eval \$command
                fi
            done
    """
}

// The manifest file is a text file with no header and rows of study_uuid:accession_id
n_elements = new File(params.manifest_path).text.readLines().size() - 1
n_jobs = params.n_jobs as int
//n_elements_per_job = n_elements / n_jobs as int
// We want to run export for each study separately as code crashes on error of a single one
n_elements_per_job = 2

workflow {
    Channel.fromPath(params.manifest_path)
        .splitText()
        .map({ it.trim() })
        .collate( n_elements_per_job ) // Ensure even single items are passed as an array
        //.splitText( by:n_elements_per_job )
        //.map({it.replaceAll("\n"," ")})
        //.map({it.strip()})
        //.collate( 1 ) // Ensure even single items are passed as an array
        | set { study_uuid_chunks }
    run_export_scripts(study_uuid_chunks)

}
