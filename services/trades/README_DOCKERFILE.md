# Dockerfile

There are three Dockerfiles in the directory:

- **Naive** (`naive.Dockerfile`): basic Dockerfile, not optimized as it is not caching through the use of the --mount flag and the project dependencies are installed twice

- **Standard** (`Dockerfile`): optimized Dockerfile for production. Includes caching and bytecode compilation

- **Multistage** (`multistage.Dockerfile`): like the standard but builds a final image without `uv` to reduce the final size of the image.
