param(
    [string]$BaseUrl = "http://localhost:8080"
)

$ErrorActionPreference = "Stop"
$base = $BaseUrl.TrimEnd("/")

$health = Invoke-RestMethod -Uri "$base/health" -Method Get
if ($health.status -ne "ok" -or $health.database -ne "connected") {
    throw "Health check did not confirm the database connection."
}

$runId = [guid]::NewGuid().ToString("N").Substring(0, 12)
$email = "smoke-$runId@example.com"
$password = "Smoke-$([guid]::NewGuid().ToString('N'))"
$credentials = @{ email = $email; password = $password } | ConvertTo-Json

$user = Invoke-RestMethod -Uri "$base/api/v1/auth/register" -Method Post `
    -ContentType "application/json" -Body $credentials
if (-not $user.id) { throw "Registration did not return a user ID." }

$login = Invoke-RestMethod -Uri "$base/api/v1/auth/login" -Method Post `
    -ContentType "application/json" -Body $credentials
if (-not $login.access_token) { throw "Login did not return an access token." }
$headers = @{ Authorization = "Bearer $($login.access_token)" }

$project = Invoke-RestMethod -Uri "$base/api/v1/projects" -Method Post `
    -Headers $headers -ContentType "application/json" `
    -Body (@{ name = "Smoke test project" } | ConvertTo-Json)
if (-not $project.id) { throw "Project creation did not return an ID." }

$task = Invoke-RestMethod -Uri "$base/api/v1/projects/$($project.id)/tasks" -Method Post `
    -Headers $headers -ContentType "application/json" `
    -Body (@{ title = "Smoke test task"; priority = "high" } | ConvertTo-Json)
if (-not $task.id -or $task.project_id -ne $project.id) {
    throw "Task creation did not return the expected project ID."
}

Write-Host "Smoke test passed: health, registration, login, project, and task."
