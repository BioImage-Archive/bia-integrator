BIA Export
==========

Export data from the BIA to feed static pages, and other downstream consumers. This:

* Selects attributes for studies stored in local files
* Transforms to a specific export format
* Writes the result to a JSON file

The expectation is to use this on the output from the bia-ingest package, that can cache the documents that will be uploaded to the api as local files.

This does not yet:

* Cover images, or even complete study metadata
* Pulls data from the BIA Integrator API
* Derives information from OME-Zarr representations (physical dimensions, axis sizes)
 
Installation
------------

1. Clone the repository.
2. Run `poetry install`

Setup
-----

None required post installation

Usage
-----

Study export 
Run:

    `poetry run bia-export website-study S-BIADTEST -o bia-study-metadata.json -r test/input_data` 

This will create `bia-study-metadata.json` using the example test data for studies

Image Export
Run:
    
    `poetry run bia-export website-image S-BIADTEST -o bia-image-export.json -r test/input_data `

This will create `bia-image-export.json` using the example test data.

Image Dataset Export
Run:
    `poetry run bia-export datasets-for-website-image S-BIADTEST -o bia-dataset-export.json -r test/input_data`
This will create `bia-dataset-exportt.json` using the example test data.


Commands to generate the current BIA data
-----------------------------------------

Study export:

```
poetry run bia-export website-study S-BIAD1218 S-BIAD1201 S-BIAD1034 S-BIAD1026 S-BIAD1287 S-BIAD1055 S-BIAD1185 S-BIAD957 S-BIAD748 S-BIAD850 S-BIAD1018 S-BIAD1077 S-BIAD1122 S-BIAD1163 S-BIAD618 S-BIAD620 S-BIAD650 S-BIAD814 S-BIAD825 S-BIAD954 S-BIAD963 S-BIAD1044 S-BIAD1183 S-BIAD627 S-BIAD826 S-BIAD843 S-BIAD845 S-BIAD849 S-BIAD890 S-BIAD1008 S-BIAD1024 S-BIAD1092 S-BIAD1093 S-BIAD1134 S-BIAD1135 S-BIAD1165 S-BIAD1175 S-BIAD1197 S-BIAD1215 S-BIAD1248 S-BIAD1260 S-BIAD663 S-BIAD831 S-BIAD846 S-BIAD851 S-BIAD887 S-BIAD922 S-BIAD928 S-BIAD1005 S-BIAD1009 S-BIAD1057 S-BIAD1079 S-BIAD1083 S-BIAD1088 S-BIAD1091 S-BIAD1099 S-BIAD1104 S-BIAD1168 S-BIAD1169 S-BIAD1193 S-BIAD1203 S-BIAD1268 S-BIAD1284 S-BIAD1323 S-BIAD607 S-BIAD608 S-BIAD610 S-BIAD616 S-BIAD626 S-BIAD661 S-BIAD694 S-BIAD705 S-BIAD800 S-BIAD813 S-BIAD815 S-BIAD823 S-BIAD824 S-BIAD829 S-BIAD830 S-BIAD847 S-BIAD848 S-BIAD852 S-BIAD861 S-BIAD865 S-BIAD866 S-BIAD884 S-BIAD885 S-BIAD904 S-BIAD931 S-BIAD955 S-BIAD970 S-BIAD986 S-BIAD1012 S-BIAD1019 S-BIAD1028 S-BIAD1039 S-BIAD1064 S-BIAD1078 S-BIAD1084 S-BIAD1090 S-BIAD1094 S-BIAD1095 S-BIAD1097 S-BIAD1102 S-BIAD1114 S-BIAD1116 S-BIAD1119 S-BIAD1130 S-BIAD1133 S-BIAD1151 S-BIAD1152 S-BIAD1157 S-BIAD1159 S-BIAD1162 S-BIAD1167 S-BIAD1196 S-BIAD1199 S-BIAD1200 S-BIAD1204 S-BIAD1236 S-BIAD1244 S-BIAD1245 S-BIAD1267 S-BIAD1271 S-BIAD1272 S-BIAD1274 S-BIAD1285 S-BIAD1293 S-BIAD1308 S-BIAD1327 S-BIAD612 S-BIAD633 S-BIAD646 S-BIAD678 S-BIAD680 S-BIAD684 S-BIAD700 S-BIAD720 S-BIAD725 S-BIAD728 S-BIAD770 S-BIAD855 S-BIAD860 S-BIAD862 S-BIAD864 S-BIAD882 S-BIAD886 S-BIAD915 S-BIAD916 S-BIAD965 S-BIAD967 S-BIAD985 S-BIAD987 S-BIAD992 S-BIAD993 S-BIAD1027 S-BIAD1030 S-BIAD1033 S-BIAD1045 S-BIAD1063 S-BIAD1080 S-BIAD1082 S-BIAD1086 S-BIAD1096 S-BIAD1100 S-BIAD1121 S-BIAD1155 S-BIAD1158 S-BIAD1184 S-BIAD1186 S-BIAD1194 S-BIAD1216 S-BIAD1232 S-BIAD1235 S-BIAD1237 S-BIAD1239 S-BIAD1247 S-BIAD1250 S-BIAD1259 S-BIAD1270 S-BIAD1282 S-BIAD1298 S-BIAD1300 S-BIAD1302 S-BIAD1314 S-BIAD1316 S-BIAD1333 S-BIAD602 S-BIAD603 S-BIAD606 S-BIAD609 S-BIAD611 S-BIAD617 S-BIAD619 S-BIAD621 S-BIAD624 S-BIAD647 S-BIAD651 S-BIAD652 S-BIAD657 S-BIAD658 S-BIAD664 S-BIAD668 S-BIAD669 S-BIAD676 S-BIAD679 S-BIAD682 S-BIAD696 S-BIAD703 S-BIAD704 S-BIAD767 S-BIAD769 S-BIAD777 S-BIAD807 S-BIAD808 S-BIAD817 S-BIAD821 S-BIAD822 S-BIAD827 S-BIAD832 S-BIAD840 S-BIAD841 S-BIAD842 S-BIAD844 S-BIAD863 S-BIAD900 S-BIAD901 S-BIAD903 S-BIAD910 S-BIAD913 S-BIAD914 S-BIAD926 S-BIAD930 S-BIAD961 S-BIAD969 S-BIAD976 S-BIAD984 S-BIAD988 S-BIAD999 -o bia-study-metadata.json -r ~/.cache/bia-integrator-data-sm/
```

And similarly for the images and datasets.

