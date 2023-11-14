# go.ps1

param(
    [string]$arg
)

if ($arg) {
    # If an argument is provided, run tools.py with the argument
    # python .\markdown_utils\tools.py $arg
    rye run tools $arg
} else {
    # If no argument is provided, display the help for tools.py
    # python .\markdown_utils\tools.py --help
    rye run tools --help
}
