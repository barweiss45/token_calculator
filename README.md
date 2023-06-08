# Token Calculator in OpenAi

## Instructions

You will need an OpenAI account and an Open AI key to use this basic calculator.

Docker is needed as well. Use the .env-template file.

1. Update the file with your key.
2. Rename file to `.env`
3. Then build the container:
    ```docker
    docker build -t token_calculator .
    ```
5. Run the Docker container and access the application at port 8501.