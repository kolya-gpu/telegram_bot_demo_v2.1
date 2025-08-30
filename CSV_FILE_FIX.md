# CSV File Access Fix

## Problem Description
The bot was experiencing a `FileNotFoundError: [Errno 2] No such file or directory: '/app/logs/message_mapping.csv'` when running in Docker containers.

## Root Cause
1. **Hardcoded file path**: The CSV file path was hardcoded as `/app/logs/message_mapping.csv` in `main.py`
2. **Permission issues**: The container was running as the `bot` user but the mounted volume might have permission issues
3. **Path resolution**: The file path wasn't properly resolved relative to the working directory

## Fixes Applied

### 1. Configurable File Path (`bot/main.py`)
- Made CSV file path configurable through `CSV_FILE_PATH` environment variable
- Added fallback to relative path `logs/message_mapping.csv`
- Added automatic directory creation with `os.makedirs()`
- Added comprehensive logging for debugging

### 2. Environment Variable Support (`docker-compose.yml`)
- Added `CSV_FILE_PATH` environment variable with default value
- Allows easy configuration without code changes

### 3. Improved CSV Storage (`bot/csv_storage.py`)
- Added `check_file_accessibility()` method to verify file permissions
- Enhanced error handling with detailed logging
- Improved directory creation logic
- Better debugging information in `debug_print_mappings()`

### 4. Dockerfile Improvements (`bot/Dockerfile`)
- Fixed user permissions for the `bot` user
- Ensured proper ownership of the `/app/logs` directory
- Added proper `chmod` for the logs directory

### 5. Enhanced Error Handling (`bot/main.py`)
- Added file accessibility checks before initialization
- Better error messages and logging
- Graceful fallback when file access fails

## Usage

### Environment Variable
```bash
# Set in your .env file
CSV_FILE_PATH=/app/logs/message_mapping.csv

# Or use relative path
CSV_FILE_PATH=logs/message_mapping.csv
```

### Testing
Run the test script to verify file access:
```bash
docker exec telegram_bot python test_csv_access.py
```

### Rebuilding
Use the provided script to rebuild and test:
```bash
# PowerShell
.\rebuild_and_test.ps1

# Or manually
docker-compose down
docker-compose build --no-cache bot
docker-compose up -d
```

## Expected Behavior
1. Bot will now use configurable file paths
2. Automatic directory creation if needed
3. Better error messages for debugging
4. Proper permission handling in Docker containers
5. Fallback to relative paths if absolute paths fail

## Troubleshooting
If issues persist:
1. Check container logs: `docker-compose logs bot`
2. Verify file permissions: `docker exec telegram_bot ls -la /app/logs/`
3. Test file access: `docker exec telegram_bot python test_csv_access.py`
4. Check volume mounting: `docker inspect telegram_bot`
