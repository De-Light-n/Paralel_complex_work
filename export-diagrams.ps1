# Script to extract and export PlantUML diagrams from markdown files

param(
    [string]$OutputDir = "diagrams\exports",
    [string]$DiagramsDir = "diagrams",
    [string]$Format = "png"  # png, svg, pdf
)

Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PlantUML Diagram Exporter                              ║" -ForegroundColor Cyan
Write-Host "║   Investment Portfolio Management System                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Java is installed
Write-Host "[1/5] Checking Java installation..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "  ✓ Java found: $javaVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Java not found! Please install Java first." -ForegroundColor Red
    Write-Host "    Download from: https://www.java.com" -ForegroundColor Yellow
    exit 1
}

# Check if PlantUML JAR exists
$plantUmlJar = "plantuml.jar"
Write-Host "[2/5] Checking PlantUML JAR..." -ForegroundColor Yellow

if (-not (Test-Path $plantUmlJar)) {
    Write-Host "  ! PlantUML JAR not found. Downloading..." -ForegroundColor Yellow
    $downloadUrl = "https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar"
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $plantUmlJar
        Write-Host "  ✓ PlantUML downloaded successfully" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to download PlantUML. Please download manually from:" -ForegroundColor Red
        Write-Host "    https://plantuml.com/download" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "  ✓ PlantUML JAR found" -ForegroundColor Green
}

# Create output directory
Write-Host "[3/5] Creating output directory..." -ForegroundColor Yellow
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "  ✓ Created: $OutputDir" -ForegroundColor Green
} else {
    Write-Host "  ✓ Directory exists: $OutputDir" -ForegroundColor Green
}

# Find all markdown files
Write-Host "[4/5] Finding markdown files..." -ForegroundColor Yellow
$mdFiles = Get-ChildItem -Path $DiagramsDir -Filter "*.md" | Where-Object { $_.Name -ne "README.md" }
Write-Host "  ✓ Found $($mdFiles.Count) diagram files" -ForegroundColor Green

# Process each markdown file
Write-Host "[5/5] Extracting and exporting diagrams..." -ForegroundColor Yellow
Write-Host ""

$totalDiagrams = 0
$successCount = 0
$failCount = 0

foreach ($mdFile in $mdFiles) {
    Write-Host "  Processing: $($mdFile.Name)" -ForegroundColor Cyan
    
    $content = Get-Content $mdFile.FullName -Raw -Encoding UTF8
    
    # Extract all PlantUML code blocks
    $pattern = '```plantuml\s*\r?\n(.*?)\r?\n```'
    $matches = [regex]::Matches($content, $pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    
    if ($matches.Count -eq 0) {
        Write-Host "    ! No PlantUML diagrams found" -ForegroundColor Yellow
        continue
    }
    
    $counter = 1
    foreach ($match in $matches) {
        $totalDiagrams++
        $pumlCode = $match.Groups[1].Value.Trim()
        
        # Extract title from PlantUML code
        $titleMatch = [regex]::Match($pumlCode, 'title\s+(.+)')
        $title = if ($titleMatch.Success) { 
            $titleMatch.Groups[1].Value.Trim() 
        } else { 
            "Diagram $counter" 
        }
        
        # Create filename
        $baseName = $mdFile.BaseName
        $pumlFileName = "${baseName}-${counter}.puml"
        $pumlFilePath = Join-Path $OutputDir $pumlFileName
        
        # Save PUML file
        Set-Content -Path $pumlFilePath -Value $pumlCode -Encoding UTF8
        
        # Generate diagram using PlantUML
        $outputFormat = switch ($Format) {
            "png" { "-tpng" }
            "svg" { "-tsvg" }
            "pdf" { "-tpdf" }
            default { "-tpng" }
        }
        
        try {
            $result = java -jar $plantUmlJar $outputFormat $pumlFilePath 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                $outputFile = "${baseName}-${counter}.$Format"
                Write-Host "    ✓ Exported: $outputFile" -ForegroundColor Green
                Write-Host "      Title: $title" -ForegroundColor DarkGray
                $successCount++
            } else {
                Write-Host "    ✗ Failed to export diagram $counter" -ForegroundColor Red
                Write-Host "      Error: $result" -ForegroundColor DarkRed
                $failCount++
            }
        } catch {
            Write-Host "    ✗ Exception: $_" -ForegroundColor Red
            $failCount++
        }
        
        $counter++
    }
    
    Write-Host ""
}

# Summary
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Export Summary                                         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Total diagrams found:    $totalDiagrams" -ForegroundColor White
Write-Host "  Successfully exported:   $successCount" -ForegroundColor Green
Write-Host "  Failed:                  $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host "  Output directory:        $OutputDir" -ForegroundColor White
Write-Host "  Output format:           $Format" -ForegroundColor White
Write-Host ""

# List exported files
if ($successCount -gt 0) {
    Write-Host "Exported files:" -ForegroundColor Yellow
    Get-ChildItem -Path $OutputDir -Filter "*.$Format" | Sort-Object Name | ForEach-Object {
        $size = [math]::Round($_.Length / 1KB, 2)
        Write-Host "  • $($_.Name) ($size KB)" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "✓ All diagrams exported successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Open the '$OutputDir' folder" -ForegroundColor White
    Write-Host "  2. Copy $Format files to your report document" -ForegroundColor White
    Write-Host "  3. Add captions and descriptions" -ForegroundColor White
} else {
    Write-Host "⚠ No diagrams were exported" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to open output folder..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Invoke-Item $OutputDir
