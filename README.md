# Pocket Tasks

This project is a simple task management application.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/pocket-tasks.git
    cd pocket-tasks
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv # This is a one-off
    source .venv/bin/activate
    ```
    *Note: You will need to run `source .venv/bin/activate` in every new terminal session before running any `make` commands.*

3.  **Install dependencies:**
    ```bash
    make install
    make install-dev
    ```

## Makefile Commands

Here are the available commands in the Makefile:

*   `make install`: Install production dependencies.
*   `make install-dev`: Install development dependencies.
*   `make test`: Run unit tests with coverage.
*   `make test-emulator`: Run manual tests with luma.emulator.
*   `make lint`: Check code style with flake8.
*   `make format`: Format code with black.
*   `make clean`: Remove test artifacts and cache.
*   `make run`: Start the application.
*   `make help`: Show this help message.
