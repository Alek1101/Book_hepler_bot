lint:
    @echo 'Running linter...'
    black .
    ruff check .