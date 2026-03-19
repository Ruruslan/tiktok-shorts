#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

ensure_env() {
  local target="$1"
  local example="$2"
  if [[ ! -f "$target" ]]; then
    cp "$example" "$target"
    echo "Создан $target из шаблона $example"
  fi
}

ensure_env "backend/.env" "backend/.env.example"
ensure_env "frontend/.env" "frontend/.env.example"

if grep -q 'OPENAI_API_KEY=sk-\.\.\.' backend/.env; then
  echo "[!] В backend/.env все еще указан шаблонный OPENAI_API_KEY."
  echo "    Приложение запустится, но AI-обработка не будет работать, пока вы не укажете реальный ключ."
fi

exec docker compose up --build
