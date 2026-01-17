# Project Context

## Purpose
Enable kids to track their tasks in a fun way. It's called pocket-tasks.
We are building software that will run in a RaspberryPi computer with a touch screen embedded. The RaspberryPi device will be dedicated to this single application. The software will be able to support a family, i.e. more than one kid.
Through simple and engaging interactions, the kids will be able to check what weekly tasks are pending and how many of them they completed already. For each completed task they'll receive some money

## Tech Stack
- RaspberryPi as platform
- Waveshare 2.13" Touch e-Paper HAT for the display.
- PIL/Pillow Library
- Python
- plain file system storage to save each kid's weekly progress
- Amazon SES

## Project Structure

```
pocket-tasks/
├── src/
│   ├── app.py                 # Main application entry point
│   ├── ui/                    # UI rendering and display logic
│   │   ├── __init__.py
│   │   ├── screen.py          # Display abstraction for e-paper/emulator
│   │   ├── renderer.py        # Image rendering and button drawing
│   │   └── themes.py          # Visual theme definitions (colors, fonts, layouts)
│   ├── tasks/                 # Task and progress management
│   │   ├── __init__.py
│   │   ├── models.py          # Task and Family data structures
│   │   └── manager.py         # Task loading and state management
│   ├── storage/               # File system persistence
│   │   ├── __init__.py
│   │   ├── repository.py      # Data persistence layer
│   │   └── serializers.py     # JSON/file format handlers
│   ├── events/                # Input handling (touch events)
│   │   ├── __init__.py
│   │   └── handlers.py        # Touch input processing
│   ├── notifications/         # Email and notifications
│   │   ├── __init__.py
│   │   └── email.py           # Amazon SES integration
│   └── config.py              # Configuration and constants
├── tests/
│   ├── __init__.py
│   ├── test_ui.py
│   ├── test_tasks.py
│   ├── test_storage.py
│   ├── fixtures/              # Test data and sample files
│   └── conftest.py            # Pytest configuration
├── assets/
│   ├── fonts/                 # Font files for display
│   ├── images/                # Pixel art assets
│   └── sample_data/           # Sample task definitions
├── Makefile                   # Build and test commands
├── requirements.txt           # Python dependencies
├── requirements-dev.txt       # Development dependencies
└── README.md                  # Project documentation
```

## Code Style & Conventions

### Python Style
- Follow PEP 8 for code formatting
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints for function signatures where practical
- Use meaningful variable names; avoid single letters except for loop counters

### Naming Conventions
- Classes: PascalCase (e.g., `TaskManager`, `DisplayRenderer`)
- Functions/methods: snake_case (e.g., `load_tasks`, `render_screen`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_DISPLAY_WIDTH`, `DEFAULT_FONT_SIZE`)
- Private methods: prefix with `_` (e.g., `_initialize_display`)
- Files: snake_case (e.g., `task_manager.py`, `email_handler.py`)

### Docstrings
- Use docstrings for all public functions and classes
- Format: Multi-line docstrings with summary, detailed description, and examples where applicable
- Include parameter and return type documentation

### Code Organization
- Keep modules focused on a single responsibility
- Related functionality grouped by feature (e.g., all task logic in `tasks/`)
- Avoid circular imports; use dependency injection where needed
- Use `__init__.py` files to expose public APIs from modules

## Dependencies & Build

### Python Version
- Target: Python 3.8+ (compatible with RaspberryPi OS)

### Core Dependencies
- `pillow` - Image rendering and manipulation
- `luma.core` - Display abstraction (works with physical hardware and emulator)
- `luma.emulator` - Emulated display for testing without hardware
- `waveshare-epd` - E-paper HAT driver (if using hardware-specific driver)
- `boto3` - Amazon SES integration

### Development Dependencies
- `pytest` - Unit testing framework
- `pytest-cov` - Test coverage reporting
- `black` - Code formatting
- `flake8` - Linting

### Dependency Management
- Pin major versions in `requirements.txt` for reproducible builds
- Keep `requirements-dev.txt` separate for development tools
- Test all changes with both emulator and hardware when available
- Update dependencies infrequently; test thoroughly when updating

### Build Commands (Makefile)
```makefile
install:        Install dependencies
install-dev:    Install dev dependencies
test:           Run unit tests with coverage
test-emulator:  Run manual tests with luma.emulator
lint:           Check code style with flake8
format:         Format code with black
clean:          Remove test artifacts and cache
run:            Start the application
```

## Data & Storage

### Storage Location
- Base directory: `/home/pocket-tasks/data/` on RaspberryPi (configurable via `DATA_DIR` env var)
- Each family has a dedicated directory: `/home/pocket-tasks/data/families/`

### Data Structure
```
/home/pocket-tasks/data/
├── families/
│   ├── family1/
│   │   ├── config.json        # Family metadata (name, members)
│   │   ├── kids/
│   │   │   ├── alice.json     # Child profile (age, preferences)
│   │   │   └── bob.json
│   │   └── progress/
│   │       ├── 2025-01-13.json  # Weekly progress snapshot (tasks completed, money earned)
│   │       └── 2025-01-20.json
│   └── family2/
└── app_state.json             # Current UI state (selected child, screen state)
```

### File Format
- All data stored as JSON for human readability and easy debugging
- Atomic writes: write to temporary file, then rename to avoid corruption
- Timestamps in ISO 8601 format (UTC)
- Single responsibility: each file contains one logical unit of data

### Initialization
- On first run, create default family directory if missing
- Scan existing families and load them at startup
- Weekly reset: check if new week detected, initialize fresh progress tracking

### Backup Strategy
- No built-in backup (assume SD card is backed up separately)
- All progress data stored locally; no cloud sync
- Manual export possible via email (future enhancement)

## Error Handling & Logging

### Logging
- Log to stdout in development, to `/home/pocket-tasks/logs/app.log` in production
- Log levels: DEBUG (dev only), INFO (milestones), WARNING (recoverable issues), ERROR (failures)
- Include timestamps and function names in log messages
- Example: `INFO: 2025-01-17 14:32:05 - app.py:main - Application started`

### Error Handling Patterns
- Graceful degradation: if display fails, log error and retry; don't crash
- Input validation: sanitize all file paths and user input before use
- File I/O: catch and log file-not-found, permission, and corruption errors
- Network (SES): retry failed email sends with exponential backoff; log for manual inspection

### Recovery Strategies
- Touch input: if input handler throws error, reset and wait for next touch
- Storage: if corrupted JSON detected, preserve original, log error, try backup if available
- Display: if e-paper communication fails, return to emulator mode (dev), or restart display driver
- Email: queue failed notifications; retry daily via cronjob

### Critical Failures
- If data directory unreachable: log critical error and alert operator (via stderr)
- If configuration missing: exit with helpful message pointing to setup instructions
- UI rendering failure: attempt fallback simple display before giving up

## Development Workflow

### Local Setup
1. Clone repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate environment: `source venv/bin/activate`
4. Install dependencies: `make install-dev`
5. Run tests: `make test`
6. Start emulator: `make test-emulator`

### Testing During Development
- Run unit tests frequently: `make test`
- Use `luma.emulator` for UI testing without physical hardware
- Emulator displays on-screen rendering; use keyboard/mouse to simulate touches
- Check test coverage: `pytest --cov=src tests/`
- Coverage target: aim for 80%+ of business logic

### Before Committing
1. Format code: `make format`
2. Lint code: `make lint`
3. Run full test suite: `make test`
4. Verify no debug statements or temporary code remains
5. Write descriptive commit messages

### Testing on RaspberryPi Hardware
1. SSH into device: `ssh pi@<ip-address>`
2. Navigate to app directory: `cd /home/pocket-tasks`
3. Manually stop running instance: `systemctl stop pocket-tasks` (if using systemd)
4. Run tests: `make test`
5. Test UI manually with `make test-emulator` (if X11 forwarding available)
6. Restart app: `systemctl start pocket-tasks`

### Debugging on Device
- Check application logs: `tail -f /home/pocket-tasks/logs/app.log`
- Check system logs: `journalctl -u pocket-tasks -f`
- SSH into device and run interactively (temporarily override cronjob)
- Use print debugging cautiously; always log important state for production issues

## Project Conventions

### Testing Strategy
- unit tests for all the changes
- a Makefile command spins up `luma.emulator` to perform manual tests without having to have the RaspberryPi and screen connected

### Deployment Strategy
We'll have a cronjob running on the raspberryPi that every night, at 2am, does the following:
- Stops pocket-tasks
- Gets the latest source code from github
- Starts pocket-tasks

### Visual Identity
Even though our selected display only supports two colours (black and white) and 250×122 resolution, the interface should be joyful. Consider having:
- round buttons
- pixel art
- minimal transition elements due to the low refresh speed

### Git Workflow
- PRs can only be merged once all the unit tests are passing
