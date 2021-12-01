def clean_path(path):
    """Cleans path of starting backslash.

    The API will interpret the starting backslash as an absolute path.
    This results in the API mistakenly providing the entire system
    file structure of the container. By removing the backslash,
    we ensure that the path being scanned is relative to the mounted
    path thats mapped in the docker-compose file.
    """
    if path.startswith("/"):
        return path[1:]
    return path
