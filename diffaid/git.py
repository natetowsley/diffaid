import subprocess

def get_staged_diff() -> str:
    # Using subprocess to run 'git diff --staged'
    result = subprocess.run(
        ["git", "diff", "--staged"],
        # Captures output rather than printing to terminal
        capture_output=True,
        # Makes output strings rather than bytes
        text=True
    )
    return result.stdout.strip()
