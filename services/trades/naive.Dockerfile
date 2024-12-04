
# Dockerfile not optimized for production, but for development
# As it is not caching through the use of the --mount flag
# The project dependencies are installed twice
# with the ADD and RUN command, which is not optimal for production 
# base layer based on Linux Debian
FROM python:3.11-slim-bookworm

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

# Run our service
CMD ["uv", "run", "run.py"]