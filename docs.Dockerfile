FROM python:3.10

RUN apt-get update && apt-get install -y \
    pandoc default-jre graphviz \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    latexmk

WORKDIR /app
ADD . .

RUN python -m pip install --upgrade pip
RUN python -m pip install -e .[docs]

CMD sphinx-autobuild --host 0.0.0.0 docs docs/_build/html

# Build:
# $ docker build -f docs.Dockerfile -t data2rdf-docs .

# Run:
# $ docker run -it --rm -v $PWD:/app -p 8000:8000 data2rdf-docs
