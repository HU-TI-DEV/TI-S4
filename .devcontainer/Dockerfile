# Begin met een Ubuntu 24.04 image, de laatste stabiele versie van ubuntu
FROM mcr.microsoft.com/devcontainers/base:ubuntu

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y build-essential cmake cppcheck valgrind clang lldb llvm gdb && \
    apt-get install -y ghostscript

ENV BUN_INSTALL=/usr/local
RUN curl -fsSL https://bun.sh/install | bash
RUN ln -s /usr/local/bin/bun /usr/local/bin/node
RUN /usr/local/bin/bun install --global @slidev/cli @slidev/client @slidev/types playwright-chromium
RUN /usr/local/bin/bun x playwright install-deps
RUN /usr/local/bin/bun x playwright install
