Notes on creating the files in this directory:

1. Copy supported formats from https://bio-formats.readthedocs.io/en/stable/supported-formats.html
2. Paste into spreadsheet or text editor and get all extensions
3. Ensure extensions are unique and sorted
4. Manually curate into 'bioformats_curated_single_file_formats.txt' Which have 1-2-1 conversion with bioformats2raw and bioformats_curated_other_file_formats.txt which require more input for conversion (e.g. pattern files)

The above steps can be accomplished in a browser developer console using the following js snippet (thanks to LA):

[...new Set(Array.from(document.getElementsByTagName("tbody")[0].querySelectorAll("td:nth-child(2)")).map(el => el.innerText.split(",")).flat().filter(extension => extension.length))].sort()
