FROM ubuntu:22.04

ENV TZ=Asia/Ho_Chi_Minh \ 
	DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
	vim \
	tmux \
	g++ \
	gdb \
	python3 \
	python3-pip \
	python-is-python3 \
	libzmq5 \
	libzmq5-dev \
	libprotobuf-dev \
	protobuf-compiler \
	libgl1 \
	libglib2.0-0
RUN mkdir -p /usr/ns3-gym
WORKDIR /usr/ns3-gym
COPY . .

RUN ./waf configure --disable-werror 
#RUN CXXFLAGS="-Wall -g -O0" ./waf configure 
RUN ./waf build
RUN pip3 install ./contrib/opengym/model/ns3gym
RUN pip3 install -r requirements.txt
RUN apt-get clean 
CMD tail -f /dev/null
