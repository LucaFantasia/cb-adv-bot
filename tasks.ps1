param([Parameter(Position=0)] [ValidateSet('setup','fmt','lint','type','test','run','clean')] $Task)

function Use-Py { param([string[]]$Args) & python @('-m') @Args }

switch ($Task) {
  'setup' {
    Use-Py pip install -U pip
    Use-Py pip install -U -e . ruff black isort mypy pytest pre-commit
    Use-Py pre_commit install
  }
  'fmt' {
    Use-Py ruff --fix .
    Use-Py ruff format .
    Use-Py isort .
    Use-Py black .
  }
  'lint' { Use-Py ruff . }
  'type' { Use-Py mypy src }
  'test' { Use-Py pytest }
  'run'  { Use-Py src.main }
  'clean' {
    Remove-Item -Recurse -Force .mypy_cache, .pytest_cache -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path artifacts) { Remove-Item -Recurse -Force artifacts }
  }
}
