#!/bin/sh

set -eu

cd "$(dirname "$0")/../.."

repo_dir="$PWD"
venv_dir="$repo_dir/venv"

create_venv() {
  if [ ! -d "$venv_dir" ]; then
    ./tools/scripts/create_venv.sh
  fi
  # shellcheck disable=SC1090
  . "$venv_dir/bin/activate"
}

run_pytest() {
  coverage run --source=./securicad/model/ --omit=./securicad/model/ModelViewsPackage/*,./securicad/model/ObjectModelPackage/* --branch --module pytest --exitfirst --capture=no -vv ./tests/model/
  coverage html --fail-under=100 --skip-covered
}

main() {
  create_venv
  run_pytest
}

main
