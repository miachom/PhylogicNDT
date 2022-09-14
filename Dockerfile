FROM ubuntu:20.04
LABEL maintainer = "maria_nakhoul@dfci.harvard.edu"
ENV DEBIAN_FRONTEND=noninteractive 


RUN apt-get -y update && apt-get -y install curl libfreetype6-dev python-setuptools build-essential python-dev r-base r-base-dev git graphviz python-tk sudo libgraphviz-dev cmake wget gzip 

RUN sudo curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py
RUN sudo python get-pip.py

RUN pip install numpy==1.16.6 matplotlib==2.0.0 pandas==0.19.2 scipy==1.2.3

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt
#RUN pip install -e git+https://github.com/rmcgibbo/logsumexp.git#egg=sselogsumexp

RUN mkdir /phylogicndt/

COPY PhylogicSim /phylogicndt/PhylogicSim
COPY GrowthKinetics /phylogicndt/GrowthKinetics
COPY BuildTree /phylogicndt/BuildTree
COPY Cluster /phylogicndt/Cluster
COPY SinglePatientTiming /phylogicndt/SinglePatientTiming
COPY LeagueModel /phylogicndt/LeagueModel
COPY data /phylogicndt/data
COPY ExampleData /phylogicndt/ExampleData
COPY ExampleRuns /phylogicndt/ExampleRuns
COPY output /phylogicndt/output
COPY utils /phylogicndt/utils
COPY PhylogicNDT.py /phylogicndt/PhylogicNDT.py
COPY LICENSE /phylogicndt/LICENSE
COPY requirements.txt /phylogicndt/requirements.txt
COPY README.md /phylogicndt/README.md
