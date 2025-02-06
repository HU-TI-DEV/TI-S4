# Begin met een Ubuntu 24.04 image, de laatste stabiele versie van ubuntu
FROM ubuntu:24.04

# Deze environment variabele zorgt ervoor dat de installatie van
# packages niet interactief is, e.g. geen vragen of je het wel
# zeker weet allemaal.
ARG DEBIAN_FRONTEND=noninteractive

# Update de package database en installeer de benodigde tools
RUN apt-get update && \
    apt-get install -y build-essential cmake

# Stel de werkdirectory in
WORKDIR /app

# Kopieer alle projectbestanden naar de container
COPY . /app

# Configureer en bouw het C++ project via CMake
RUN mkdir -p build
RUN cd build && cmake .. && make

# Bij het opstarten van de container wordt de applicatie gestart
CMD ["./build/buggy_project"]
