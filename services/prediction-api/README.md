# Prediction API

Need to install rust compiler and cargo and add the rust analyzer extension.

Then in services folders, run:

    cargo new prediction-api

Then in folder prediction-api

    cargo run

This will create the lock file and compile/run the main.rs in `src`.

Then add a Cargo.toml in root directory to create a workspace for the prediction-api service.

Add dependencies with 

    cargo add actix-web 
    cargo add serde --features derive

[Actix Web](https://actix.rs/)