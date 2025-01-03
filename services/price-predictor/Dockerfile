# An example using multi-stage image builds a final image without uv.
# The multistage.Dockerfile example extends the Dockerfile example to use multistage
# builds to reduce the final size of the image.

# First, build the application in the `/app` directory.
# See `Dockerfile` for details.
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Then, use a final image without uv
FROM python:3.11-slim-bookworm
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# This add the settings.env into the image
WORKDIR /app

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Create the state folder
RUN mkdir -p /app/state

# Document that /app/state should be a volume
VOLUME /app/state

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the Python service "without uv"
CMD ["python", "/app/run.py"]