# Install in the DSMS

A detailed description on how to update the pipeline package in the DSMS instance is given in the DSMS docs: <https://dsms.pages.fraunhofer.de/platform/documentation/platform-developer-docs/data2rdf_integration.html>
Usually the newest version should be installed when the DSMS docker image was build.
In this case it can be imported with

```python
from data2rdf.annotation_pipeline import AnnotationPipeline
```

# Add upload pipeline as profile to the DSMS

In order to use the pipeline to upload files to the DSMS it needs to included as a notebook to the jupyterlab instance of the DSMS.
In the notebook the parsing arguments and the paths to the `abox template` and the `mapping file` need to be provided. The `abox template` and the `mapping file` must be available in the jupyterlab folder. They can be uploaded together in a folder as zip file and then extracted with:

```python
import zipfile as zf
files = zf.ZipFile("profile-data", 'r')
files.extractall('.')
files.close()
```

The input file (`SCRIPT_INPUT_FILE_PATH`) and output storage path (`OUTPUT_STORAGE`) from the DSMS must be assigned.
The created turtle file can then be uploaded to the graph using the utility function provide in <https://gitlab.cc-asp.fraunhofer.de/dsms/python-sdk/-/blob/main/utils/dsms_tools.py>

Example of a notebook that allows for upload of tensile test data stored in a Excel file:

```python
from data2rdf.annotation_pipeline import AnnotationPipeline

from dsms_tools import connect2graph
from franz.openrdf.rio.rdfformat import RDFFormat
import os
import uuid

input_folder = os.path.join(os.path.dirname(__file__), "demo_files","excel") #if run as python
raw_data = os.environ.get('SCRIPT_INPUT_FILE_PATH') #with input

file_id = str(uuid.uuid4()) #Multiple files are stored in the same upload folder but separate output folder needs to be created for each converted file
output_folder = os.path.join(os.environ.get('OUTPUT_STORAGE'), file_id)

#hard coded args since they cannot be set in the frontend yet
template = os.path.join(input_folder,"tensile_test_method_v6.mod.ttl")
mapping_file = os.path.join(input_folder,"mapping.xlsx")
location_mapping = os.path.join(input_folder,"location_mapping.xlsx")

parser = "excel"
parser_args = {
    "location_mapping_f_path":location_mapping,
   }

pipeline = AnnotationPipeline(
    raw_data,
    parser,
    parser_args,
    template,
    mapping_file,
    output_folder,
    base_iri = f"https://stahldigital.materials-data.space/{file_id}",
    data_download_iri = f"https://127.0.0.1/api/knowledge/data_api/{file_id}"
)

pipeline.run_pipeline()

merged_graph = os.path.join(output_folder, 'merged_graph.ttl')
pipeline.export_ttl(merged_graph)

conn = connect2graph()
conn.addFile(merged_graph, format=RDFFormat.TURTLE)
```

The created notebook must then be added as a scrip to a profile:
* Click: Admin / New dataset profile
* Then add a name
* Add the notebook as a Post-processing scripts

Now dataset can be uploaded using this profile.

# Set-up DSMS API based Data Access

In order to allow for the access of bulk data (e.g. column data) via the DSMS API a iri needs to be provided.
This is set as the `data_download_iri` argument.

```python
pipeline = AnnotationPipeline(
    raw_data,
    parser,
    parser_args,
    template,
    mapping_file,
    output_folder,
    base_iri = f"https://stahldigital.materials-data.space/{file_id}",
    data_download_iri = f"https://127.0.0.1/api/knowledge/data_api/{file_id}"
)
```

The iri must be relative to the server url e.g. `https://127.0.0.1/api/knowledge/data_api/<ID>` for a local instance and `https://stahldigital.materials-data.space/api/knowledge/data_api/<ID>` for an online instance. `<ID>` will be the identifier which can be used to query this data via the DSMS Data API. Based on this iri the data2rdf will add a `dcat#downloadURL` data property to all parsed columns which can be used to request the data as json from the server.

The data can requested with:

```python
url = "https://127.0.0.1/api/knowledge/data_api/<ID>/column-<ID>" #this will be provided as
resp = requests.get(url=url, verify=False)
data = json.loads(resp.text)
array = data['array']
```
