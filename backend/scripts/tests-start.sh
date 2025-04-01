#! /usr/bin/env bash

# скрипт вызывает pytest после того, как убедится, что остальная часть стека запущена.
# Если вам нужно передать дополнительные аргументы в pytest,
#вы можете передать их этой команде, и они будут перенаправлены.

# Например, чтобы остановиться при первой ошибке:
# docker compose exec backend bash scripts/tests-start.sh -x

set -e
set -x

python src/tests_pre_start.py

bash scripts/test.sh "$@"
