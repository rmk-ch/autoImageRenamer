$projectPath = $env:AUTO_IMAGE_RENAMER_PATH
$currentDir = Get-Location
Push-Location
Set-Location $projectPath
& poetry run autoImageRenamer rename "$currentDir" "$currentDir" --interactive -l "$currentDir/autoImageRenamer.log"
Pop-Location