# This is an optimized Dockerfile for production
# Includes caching and bytecode compilation
# https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile
# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Install build dependencies (GCC compiler is required)
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
# Compiling Python source files to bytecode is typically desirable for
# production images as it tends to improve startup time (at the cost of increased installation time).
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy and Install the project's dependencies using the lockfile and settings
# uv sync --no-install-project will install the dependencies of the project
# but not the project itself. Since the project changes frequently, but its dependencies
# are generally static, this can be a big time saver.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code into the image
# Installing separately from its dependencies allows optimal layer caching
ADD . /app

# Note that the pyproject.toml is required to identify the project root and name,
# but the project contents are not copied into the image until the final uv sync comman
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Create the state folder
RUN mkdir -p /app/state

# Document that /app/state should be a volume
VOLUME /app/state

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the default entrypoint of the base image
#  ghcr.io/astral-sh/uv (don't invoke `uv`)
ENTRYPOINT []

# Run the Python service
CMD ["uv", "run", "run.py"]
