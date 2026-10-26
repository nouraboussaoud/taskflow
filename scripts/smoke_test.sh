#!/usr/bin/env bash
set -euo pipefail

base_url="${1:-http://localhost:8080}"
base_url="${base_url%/}"
python_bin="${PYTHON_BIN:-python3}"

health="$(curl --fail-with-body --silent --show-error "$base_url/health")"
printf '%s' "$health" | "$python_bin" -c 'import json,sys; data=json.load(sys.stdin); assert data["status"] == "ok" and data["database"] == "connected"'

run_id="$("$python_bin" -c 'import uuid; print(uuid.uuid4().hex[:12])')"
email="smoke-${run_id}@example.com"
password="$("$python_bin" -c 'import secrets; print(secrets.token_urlsafe(24))')"
credentials="$("$python_bin" -c 'import json,sys; print(json.dumps({"email":sys.argv[1],"password":sys.argv[2]}))' "$email" "$password")"

registered="$(printf '%s' "$credentials" | curl --fail-with-body --silent --show-error \
  --request POST --header 'Content-Type: application/json' --data-binary @- \
  "$base_url/api/v1/auth/register")"
printf '%s' "$registered" | "$python_bin" -c 'import json,sys; assert json.load(sys.stdin)["id"] > 0'

login="$(printf '%s' "$credentials" | curl --fail-with-body --silent --show-error \
  --request POST --header 'Content-Type: application/json' --data-binary @- \
  "$base_url/api/v1/auth/login")"
token="$(printf '%s' "$login" | "$python_bin" -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')"

project="$(printf '%s' '{"name":"Smoke test project"}' | curl --fail-with-body --silent --show-error \
  --request POST --header 'Content-Type: application/json' --header "Authorization: Bearer $token" \
  --data-binary @- "$base_url/api/v1/projects")"
project_id="$(printf '%s' "$project" | "$python_bin" -c 'import json,sys; print(int(json.load(sys.stdin)["id"]))')"

task="$(printf '%s' '{"title":"Smoke test task","priority":"high"}' | curl --fail-with-body --silent --show-error \
  --request POST --header 'Content-Type: application/json' --header "Authorization: Bearer $token" \
  --data-binary @- "$base_url/api/v1/projects/$project_id/tasks")"
printf '%s' "$task" | "$python_bin" -c 'import json,sys; assert json.load(sys.stdin)["id"] > 0'

echo 'Smoke test passed: health, registration, login, project, and task.'
