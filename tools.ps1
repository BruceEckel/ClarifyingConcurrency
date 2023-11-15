# tools.ps1

Clear-Host;

function Join-QuotedArgs {
    $result = @()
    foreach ($arg in $args) {
        if ($arg -like '* *') {
            # If the argument contains spaces, quote it
            $result += "`"$arg`""
        } else {
            # If no spaces, leave as is
            $result += $arg
        }
    }
    return $result -join ' '
}

# Check if any arguments are provided
if ($args.Count -gt 0) {
    # Join arguments with proper quoting
    $arguments = Join-QuotedArgs $args

    # Echo the command to the console
    Write-Host "Executing: rye run tools $arguments"

    # Execute the command
    rye run tools $arguments
} else {
    # If no arguments are provided, echo the help command
    Write-Host "Executing: rye run tools --help"

    # Display the help for tools.py
    rye run tools --help
}
