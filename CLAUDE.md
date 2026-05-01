# NSW Air Quality — Developer Notes

## Testing

Use TDD when adding new behaviour or fixing bugs:

1. Write a failing test that reproduces the bug or describes the new behaviour.
2. Run it to confirm it fails (`/usr/local/bin/python3 -m pytest <test>`).
3. Make the minimal code change to pass the test.
4. Run the full unit suite to confirm nothing regressed (`/usr/local/bin/python3 -m pytest -m unit`).

Tests live in `tests/`. Mark each test with `@pytest.mark.unit` (no external calls)
or `@pytest.mark.integration` (calls the live API).
