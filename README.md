# data2rdf

A pipeline for generating data representation in RDF out of raw data given in ASCII, CSV, JSON or EXCEL format.

https://data2rdf.readthedocs.io/en/latest/

<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-88%25-green.svg" /></a><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>data2rdf</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/__init__.py">__init__.py</a></td><td>5</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/config.py">config.py</a></td><td>18</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/utils.py">utils.py</a></td><td>33</td><td>6</td><td>6</td><td><a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/utils.py#L 82%"> 82%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/warnings.py">warnings.py</a></td><td>2</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>data2rdf/models</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/models/__init__.py">__init__.py</a></td><td>3</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/models/base.py">base.py</a></td><td>47</td><td>4</td><td>4</td><td><a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/models/base.py#L 91%"> 91%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/models/graph.py">graph.py</a></td><td>122</td><td>26</td><td>26</td><td><a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/models/graph.py#L 79%"> 79%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/models/mapping.py">mapping.py</a></td><td>30</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>data2rdf/modes</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/modes/__init__.py">__init__.py</a></td><td>4</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>data2rdf/parsers</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/__init__.py">__init__.py</a></td><td>6</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/base.py">base.py</a></td><td>134</td><td>11</td><td>11</td><td><a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/base.py#L 92%"> 92%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/csv.py">csv.py</a></td><td>165</td><td>19</td><td>19</td><td><a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/csv.py#L 88%"> 88%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/excel.py">excel.py</a></td><td>159</td><td>13</td><td>13</td><td><a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/excel.py#L 92%"> 92%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/json.py">json.py</a></td><td>143</td><td>20</td><td>20</td><td><a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/json.py#L 86%"> 86%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/utils.py">utils.py</a></td><td>67</td><td>8</td><td>8</td><td><a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/parsers/utils.py#L 88%"> 88%</a></td></tr><tr><td colspan="5"><b>data2rdf/pipelines</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/pipelines/__init__.py">__init__.py</a></td><td>2</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/pipelines/main.py">main.py</a></td><td>82</td><td>9</td><td>9</td><td><a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/pipelines/main.py#L 89%"> 89%</a></td></tr><tr><td colspan="5"><b>data2rdf/qudt</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/qudt/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/qudt/utils.py">utils.py</a></td><td>42</td><td>12</td><td>12</td><td><a href="https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/data2rdf/qudt/utils.py#L 71%"> 71%</a></td></tr><tr><td><b>TOTAL</b></td><td><b>1064</b></td><td><b>128</b></td><td><b>88%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

# Installation

## Install for using the package

Either install the package from the pypi

```bash
pip install data2rdf
```


## Install for development
Install the package from the source code:
```bash
git clone git@github.com:MI-FraunhoferIWM/data2rdf.git
cd data2rdf
pip install -e .
```

# Unit tests

Before running the unit tests, please install the needed packages:

```{bash}
pip install data2rdf[tests]
```

Afterwards, run the unittest with:

```{bash}
pytest
```

# Building the docs locally
### HTML

A server will start, generate the docs and listen for changes in the source files.
This can be done by using docker or installing the development environment directly on the you machine. Next are installation guides for Docker and Linux OS.

#### Docker

First, build the Docker image by running the following command:

```shell
$ docker build -f docs.Dockerfile -t data2rdf-docs .
```

Then, start the program by running:

```shell
$ docker run -it --rm -v $PWD:/app -p 8000:8000 data2rdf-docs
```

#### Linux

At an OS level (these commands work on Linux Debian):

```shell
$ sudo apt install pandoc graphviz default-jre
$ sudo apt-get install texlive-latex-recommended \
                       texlive-latex-extra \
                       texlive-fonts-recommended \
                       latexmk
```

The python dependencies:

```shell
$ pip install .[docs]
```

Now you can start the server and render the docs:

```
$ sphinx-autobuild docs/source docs/build/html
```

The documentation will be available on [`http://127.0.0.1:8000`](http://127.0.0.1:8000).

### PDF (LaTeX)

To generate a PDF of the documentation, simply run (from the root project folder):

```sh
make -C docs latexpdf
```

The generated PDF can be found under docs/build/latex/data2rdf_docs.pdf
