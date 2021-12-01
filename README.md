# FastFiles API (FF-API)

A demo API service built with FastAPI for managing files on a host machine.

## How it works

The API service is run from a docker container with a volume that is mapped to a volume on the host machine. This allows the service to manage that particular volume of the host machine without exposing external volumes to the container.

## Instructions

1. Clone the repo and `cd`.

    ```sh
    git clone git@github.com:resurrexi/ff-api.git
    cd ff-api
    ```

2. Create a `.env` file and add a `LOCAL_FILE_DIR` environment variable. This variable defines the host's volume that will be mapped.

    ```sh
    touch .env
    echo "LOCAL_FILE_DIR=/home/user/files" > .env
    ```

    **Important:** Please be wary when choosing the volume as some paths contain system files that are essential for the host's operating system, e.g. */usr/bin*. Setting the variable to these paths can irreversibly break the OS.

3. Run `docker-compose`. The images and container will be built if they do not exist already.

    ```sh
    docker-compose up -d
    ```

    **Note:** Docker Compose is required. Refer to [Docker's website](https://docs.docker.com/compose/install/) for installation instructions.

4. Open http://localhost in your browser. The API docs can be accessed by going to http://localhost/docs. The container uses the host's web port (80) to communicate with the service. In the event that the port is already being used, you can modify the *docker-compose.yml* file.

    ```yaml
    # from
    ports:
      - 80:8000

    # to
    ports:
      - HOST_PORT:8000
    ```

    The URL for the API would then be http://localhost:HOST_PORT, where `HOST_PORT` is the port number you set in *docker-compose.yml*.

## Unit Tests

The docker container already comes with development packages for running the written unit tests. To run the tests, execute the following command in your shell:

```sh
docker-compose exec web pytest
```
