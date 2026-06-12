# Internal API

## Email handling

Both `src/users.py` and `src/auth.py` normalize email addresses before
use. Behavior is duplicated and should be consolidated.
