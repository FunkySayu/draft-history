# Developing Locally

This document outlines how to run the application locally for development purposes using Docker Compose.

## Prerequisites

*   [Docker](https://docs.docker.com/get-docker/) installed and running.
*   [Docker Compose](https://docs.docker.com/compose/install/) installed.
*   A code editor of your choice (e.g., VS Code).
*   Web browser.

## Running the Application

1.  **Clone the Repository:**
    If you haven't already, clone the repository to your local machine.
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Build and Start Docker Containers:**
    From the root directory of the project (where `docker-compose.yml` is located), run the following command:
    ```bash
    docker-compose up --build
    ```
    *   `--build`: This flag tells Docker Compose to build the images before starting the containers. You can omit this flag if the images have already been built and no code changes require a rebuild.
    *   `-d`: (Optional) Add this flag to run the containers in detached mode (in the background).
        ```bash
        docker-compose up --build -d
        ```

3.  **Accessing the Application:**
    *   **Main Application (UI and API via Nginx):** Open your web browser and navigate to `http://localhost:8080`.
        *   The Angular UI should be served.
        *   API requests from the UI to `/api/...` will be routed to the Flask API service.
    *   **Direct API Access (Optional):** The Flask API is also directly accessible on `http://localhost:5000` (though in a typical setup, you'd go through Nginx).
    *   **Direct UI Access (Optional):** The Angular app's Nginx server (within its own container) is accessible on `http://localhost:4201` (this is mostly for debugging the UI service independently).

4.  **Viewing Logs:**
    If you are not running in detached mode, logs will be streamed to your terminal.
    If running in detached mode, you can view logs for specific services:
    ```bash
    docker-compose logs -f api
    docker-compose logs -f ui
    docker-compose logs -f nginx
    ```
    To view all logs:
    ```bash
    docker-compose logs -f
    ```

5.  **Stopping the Application:**
    *   If running in the foreground, press `Ctrl+C` in the terminal where `docker-compose up` is running.
    *   If running in detached mode, or from another terminal, navigate to the project root and run:
        ```bash
        docker-compose down
        ```
        To stop and remove volumes (e.g., to clear the database):
        ```bash
        docker-compose down -v
        ```

## Development Workflow

*   **API (Flask - Python):**
    *   The `api` directory is mounted as a volume into the `api` service container.
    *   Changes to Python files in `./api` should be automatically reloaded by Gunicorn/Flask's development server (Gunicorn is configured with `--reload` in dev, or Flask's dev server does this by default. The current `api/Dockerfile` uses Gunicorn without explicit reload for dev, this could be enhanced).
    *   If you change `api/requirements.txt`, you'll need to rebuild the `api` image:
        ```bash
        docker-compose build api
        # or
        docker-compose up --build api
        ```
        Then restart the services.

*   **UI (Angular):**
    *   The `ui` directory is mounted as a volume into the `ui` service container.
    *   The `ui/Dockerfile` builds the Angular app using `npm run build`. This is a production build. For live reloading during development, the Angular Docker setup typically uses `ng serve` directly.
    *   **Current Setup for UI:** The current `ui/Dockerfile` and `docker-compose.yml` setup for the `ui` service will build the Angular app once when `docker-compose up --build` is run. Changes to the source code in `./ui` will **not** automatically rebuild the app and update the running container without manual intervention.
    *   **To see UI changes:** You would need to rebuild the `ui` service:
        ```bash
        docker-compose build ui
        docker-compose up -d --no-deps ui # Restart only the ui service
        # Or simply re-run:
        docker-compose up --build -d
        ```
    *   **For a better UI development experience (live reload):**
        The `ui/Dockerfile` could be modified or a separate Docker Compose override file could be used for development to run `ng serve` with the appropriate host and port, and map the port directly. This is a common pattern but adds complexity to the initial setup. For now, the simpler build-once approach is implemented.

## Database

*   The API uses a SQLite database by default.
*   The database file (`app.db`) is stored in a Docker named volume (`api_db_data`), so it persists across container restarts.
*   To connect to a different database (e.g., PostgreSQL), you would:
    1.  Update `DATABASE_URL` in `docker-compose.yml` for the `api` service.
    2.  Ensure the necessary Python database driver (e.g., `psycopg2-binary`) is in `api/requirements.txt` and rebuild the API image.
    3.  If using a separate database container (e.g., Postgres), add it to `docker-compose.yml`.

## Troubleshooting

*   **Port Conflicts:** If `8080`, `5000`, or `4201` are in use on your host machine, change the host-side port mappings in `docker-compose.yml`. For example, change `8080:80` to `8081:80` for the Nginx service.
*   **Build Issues:** Check the output of `docker-compose build` for errors. Ensure all dependencies are correctly listed in `requirements.txt` (for API) and `package.json` (for UI).
*   **Permissions (Linux):** Sometimes, files created in Docker volumes might have root ownership. This can be an issue for local editing. Ensure your user has permissions or adjust volume mounting strategies if this becomes problematic.

This setup provides a consistent environment for development and is a good starting point for the project.Tool output for `create_file_with_block`:
