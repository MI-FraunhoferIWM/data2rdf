# data2rdf

A pipeline for generating data representation in RDF out of raw data given in ASCII, CSV, JSON or EXCEL format.

https://data2rdf.readthedocs.io/en/latest/

<!-- Pytest Coverage Comment:Begin -->
\n<!-- Pytest Coverage Comment:End -->

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
