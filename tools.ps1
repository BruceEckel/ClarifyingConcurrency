# tools.ps1

param(
    [string]$arg
)

if ($arg) {
    # If an argument is provided, run tools.py with the argument
    Clear-Host; rye run tools $arg
} else {
    # If no argument is provided, display the help for tools.py
    Clear-Host; rye run tools --help
}
