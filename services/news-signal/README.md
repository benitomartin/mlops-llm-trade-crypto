# 3. Fix connectivity issue between the dockerized news-signal and Ollama

If you are not on Mac and have NVIDIA, you just run Ollama with docker run and attach it to the redpanda_network.

## RunPod

Add the SSH Key id_ed2551.pub to the instance

H100 NVL, Pytorch 2.1 with SSH terminal access

Use connection SSH over exposed from RunPod to the terminal

In VSCode: Remote-SSH: Add New SSH Host and add the same connection, also in .ssh/config

Then select the host and connect

Push repo to github and clone it in the remote

    # Install group
    uv sync --group gpu-instance

    # Install dev and all groups
    uv sync --all-groups --all-extras

    # Install dev
    uv sync --all-extras

## Unsloth

https://unsloth.ai/blog/llama3-1

While using llama.cpp cmake must be installed

    sudo apt update
    sudo apt install cmake
    cmake --version

Then build llama.cpp using CMake:

https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md

    cd llama.cpp
    cmake -B build # Remove build folder if any error
    cmake --build build --config Release

Locally quantization_method = q4_k_m, can save the model. q8 gives make error.

Here are some sizes
https://github.com/ggerganov/llama.cpp/blob/master/examples/quantize/README.md
https://github.com/unslothai/unsloth/wiki#gguf-quantization-options
