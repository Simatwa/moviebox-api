"""Interactive menu interface for moviebox-api"""

import platform
import shutil
import subprocess
import sys

import click

try:  # Resolves #51
    import gnureadline as readline
except ImportError:
    import readline


def clear_screen():
    """Clear the terminal screen"""
    click.clear()


def check_command_exists(command):
    """Check if a command exists in the system PATH"""
    return shutil.which(command) is not None


def install_mpv():
    """Install MPV player based on the operating system"""
    system = platform.system().lower()

    print("\nMPV PLAYER INSTALLATION INSTRUCTIONS")

    install_commands = []  # List of command lists to execute
    display_command = None  # String to display to user

    if system == "linux":
        # Detect package manager and provide appropriate instructions
        if check_command_exists("apt-get"):
            print("\nDetected Debian/Ubuntu system")
            print("\nTo install MPV, run the following commands:")
            display_command = "sudo apt-get update && sudo apt-get install -y mpv"
            print(f"  {display_command}")
            # Split into two separate commands to avoid shell=True
            install_commands = [["sudo", "apt-get", "update"], ["sudo", "apt-get", "install", "-y", "mpv"]]
        elif check_command_exists("dnf"):
            print("\nDetected Fedora/RHEL system")
            print("\nTo install MPV, run the following command:")
            display_command = "sudo dnf install -y mpv"
            print(f"  {display_command}")
            install_commands = [["sudo", "dnf", "install", "-y", "mpv"]]
        elif check_command_exists("yum"):
            print("\nDetected CentOS/RHEL system")
            print("\nTo install MPV, run the following command:")
            display_command = "sudo yum install -y mpv"
            print(f"  {display_command}")
            install_commands = [["sudo", "yum", "install", "-y", "mpv"]]
        elif check_command_exists("pacman"):
            print("\nDetected Arch Linux system")
            print("\nTo install MPV, run the following command:")
            display_command = "sudo pacman -S --noconfirm mpv"
            print(f"  {display_command}")
            install_commands = [["sudo", "pacman", "-S", "--noconfirm", "mpv"]]
        else:
            print("\nCould not detect package manager.")
            print("\nPlease install MPV manually using your distribution's package manager.")
            print("Visit: https://mpv.io/installation/")
            return False

    elif system == "darwin":
        if check_command_exists("brew"):
            print("\nDetected macOS system with Homebrew")
            print("\nTo install MPV, run the following command:")
            display_command = "brew install mpv"
            print(f"  {display_command}")
            install_commands = [["brew", "install", "mpv"]]
        else:
            print("\nHomebrew is not installed.")
            print("\nPlease install Homebrew first, then install MPV:")
            print(
                '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            )
            print("  brew install mpv")
            print("\nOr visit: https://brew.sh/ and https://mpv.io/installation/")
            return False
    else:
        print(f"\nUnsupported operating system: {system}")
        print("\nPlease install MPV manually.")
        print("Visit: https://mpv.io/installation/")
        return False

    # Offer automatic installation as explicit opt-in
    if install_commands:
        print("\nAUTOMATIC INSTALLATION (OPTIONAL)")
        print("\nWould you like to run the installation command automatically?")
        print("This will execute privileged commands on your system.")

        try:
            choice = (
                input("\nType 'yes' to proceed with automatic installation, or press Enter to skip: ")
                .strip()
                .lower()
            )

            if choice == "yes":
                print(f"\nExecuting: {display_command}")

                try:
                    # Execute each command in sequence without shell=True
                    for cmd in install_commands:
                        subprocess.run(cmd, check=True)
                    # Verify installation
                    if check_command_exists("mpv"):
                        print("\nMPV player installed successfully!")
                        return True
                    else:
                        print("\nInstallation command completed, but MPV is not detected.")
                        print("Please try installing manually using the command above.")
                        return False

                except subprocess.CalledProcessError as e:
                    print(f"\nInstallation failed with error code {e.returncode}")
                    print("Please try running the command manually.")
                    return False
            else:
                print("\nAutomatic installation skipped.")
                print("Please run the installation command manually when ready.")
                return False

        except KeyboardInterrupt:
            print("\n\nInstallation cancelled.")
            return False

    return False


def check_mpv():
    """Check if MPV player is installed (for streaming)"""
    if not check_command_exists("mpv"):
        print("\nWARNING: MPV player is not installed.")
        print("Streaming functionality requires MPV player.")
        choice = input("\nWould you like to install MPV now? (y/n): ")
        if choice.lower() in ["y", "yes"]:
            if install_mpv():
                return True
            else:
                return False
        else:
            print("Continuing without MPV. Streaming will not work.")
            input("Press Enter to continue...")
            return False
    return True


def show_main_menu():
    """Display the main menu"""
    clear_screen()
    print("\n")
    print("┌┬┐┌─┐┬  ┬┬┌─┐┌┐ ┌─┐─┐ ┬ ")
    print("││││ │└┐┌┘│├┤ ├┴┐│ │┌┴┬┘ ")
    print("┴ ┴└─┘ └┘ ┴└─┘└─┘└─┘┴ └─ ")
    print("\nDOWNLOAD OPTIONS")
    print("[1] Download Movie")
    print("[2] Download TV Series")
    print("\nSTREAMING OPTIONS")
    print("[3] Stream Movie")
    print("[4] Stream TV Series")
    print("\nDISCOVER & INFO")
    print("[5] Show Homepage Content")
    print("[6] Show Popular Searches")
    print("[7] Show Mirror Hosts")
    print("\n[0] Exit")


def get_quality_choice():
    """Get quality selection from user"""
    print("\nQuality Selection:")
    print("[1] Best quality (default)")
    print("[2] Worst quality")
    print("[3] 360p")
    print("[4] 480p")
    print("[5] 720p (HD)")
    print("[6] 1080p (Full HD)")
    choice = input("Choose quality [1-6]: ").strip()

    quality_map = {"1": "best", "2": "worst", "3": "360p", "4": "480p", "5": "720p", "6": "1080p"}

    return quality_map.get(choice, "best")


def get_subtitle_choice():
    """Get subtitle preference from user"""
    print("\nSubtitle Options:")
    print("[1] Yes (default)")
    print("[2] No")
    print("[3] Subtitles only")
    choice = input("Choose option [1-3]: ").strip()

    return choice if choice in ["1", "2", "3"] else "1"


def download_movie():
    """Handle movie download"""
    clear_screen()
    print("\nMOVIE DOWNLOAD WIZARD")

    title = input("\nEnter movie title: ").strip()
    if not title:
        print("ERROR: Movie title is required!")
        input("\nPress Enter to continue...")
        return

    print("\nOptional parameters (press Enter to use defaults):")
    year = input("Release year (leave empty for any): ").strip()

    quality = get_quality_choice()

    print("\nDownload Settings:")
    download_dir = input("Download directory (leave empty for current): ").strip()
    language = input("Subtitle language (leave empty for English): ").strip()

    subtitle_choice = get_subtitle_choice()

    command = [sys.executable, "-m", "moviebox_api", "download-movie", title]

    if year and year.strip():
        command.extend(["-y", year])
        command.append("-Y")
    if quality:
        command.extend(["-q", quality])
    if download_dir and download_dir.strip():
        command.extend(["-d", download_dir])
    if language and language.strip():
        command.extend(["-x", language])

    if subtitle_choice == "2":
        command.append("--no-caption")
    elif subtitle_choice == "3":
        command.append("-O")
    else:
        command.append("--caption")

    print(f"\nExecuting: {' '.join(command)}")

    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print("\nDownload cancelled.")
    input("\nPress Enter to continue...")


def download_series():
    """Handle TV series download"""
    clear_screen()
    print("\nTV SERIES DOWNLOAD WIZARD")

    title = input("\nEnter series title: ").strip()
    if not title:
        print("ERROR: Series title is required!")
        input("\nPress Enter to continue...")
        return

    # Get season number
    print("\nEpisode Selection:")
    while True:
        season = input("Season number: ").strip()
        if season.isdigit():
            break
        print("ERROR: Season must be a number!")

    # Get episode number
    while True:
        episode = input("Starting episode number: ").strip()
        if episode.isdigit():
            break
        print("ERROR: Episode must be a number!")

    limit = input("Number of episodes to download [default: 1]: ").strip()
    if not limit.isdigit():
        limit = "1"

    print("\nOptional parameters (press Enter to use defaults):")
    year = input("Release year (leave empty for any): ").strip()

    quality = get_quality_choice()

    print("\nDownload Settings:")
    download_dir = input("Download directory (leave empty for current): ").strip()
    language = input("Subtitle language (leave empty for English): ").strip()

    subtitle_choice = get_subtitle_choice()

    # Build command
    command = [
        sys.executable,
        "-m",
        "moviebox_api",
        "download-series",
        title,
        "-s",
        season,
        "-e",
        episode,
    ]

    if year and year.strip():
        command.extend(["-y", year])
        command.append("-Y")
    if quality:
        command.extend(["-q", quality])
    if download_dir and download_dir.strip():
        command.extend(["-d", download_dir])
    if language and language.strip():
        command.extend(["-x", language])
    if limit and limit.strip():
        command.extend(["-l", limit])

    if subtitle_choice == "2":
        command.append("--no-caption")
    elif subtitle_choice == "3":
        command.append("-O")
    else:
        command.append("--caption")

    print(f"\nExecuting: {' '.join(command)}")

    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print("\nDownload cancelled.")

    input("\nPress Enter to continue...")


def stream_movie():
    """Handle movie streaming"""
    clear_screen()
    print("\nMOVIE STREAMING WIZARD")

    media_player = click.prompt(
        "Enter media player", type=click.Choice(["vlc", "mpv"]), show_choices=True, default="mpv"
    )

    if media_player == "mpv":
        if not check_mpv():
            print("\nERROR: MPV player is required for streaming. Please install it first.")
            input("\nPress Enter to return to main menu...")
            return

    title = input("\nEnter movie title: ").strip()
    if not title:
        print("ERROR: Movie title is required!")
        input("\nPress Enter to continue...")
        return

    print("\nOptional parameters (press Enter to use defaults):")
    year = input("Release year (leave empty for any): ").strip()

    quality = get_quality_choice()

    print("\nSubtitle Options:")
    print("[1] Yes")
    print("[2] No (default)")
    subtitle_choice = input("Choose option [1-2]: ").strip()

    language = ""
    if subtitle_choice == "1":
        language = input("Subtitle language (leave empty for English): ").strip()

    # Build command
    command = [
        sys.executable,
        "-m",
        "moviebox_api",
        "download-movie",
        title,
        "--stream-via",
        media_player,
    ]

    if year and year.strip():
        command.extend(["-y", year])
        command.append("-Y")
    if quality:
        command.extend(["-q", quality])

    if subtitle_choice == "1":
        command.append("--caption")
        if language:
            command.extend(["-x", language])
    else:
        command.append("--no-caption")

    print(f"\nExecuting: {' '.join(command)}")

    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print("\nStreaming cancelled.")

    input("\nPress Enter to continue...")


def stream_series():
    """Handle TV series streaming"""
    clear_screen()
    print("\nTV SERIES STREAMING WIZARD")

    # Check if MPV is installed
    if not check_mpv():
        print("\nERROR: MPV player is required for streaming. Please install it first.")
        input("\nPress Enter to return to main menu...")
        return

    title = input("\nEnter series title: ").strip()
    if not title:
        print("ERROR: Series title is required!")
        input("\nPress Enter to continue...")
        return

    # Get season number
    print("\nEpisode Selection:")
    while True:
        season = input("Season number: ").strip()
        if season.isdigit():
            break
        print("ERROR: Season must be a number!")

    # Get episode number
    while True:
        episode = input("Episode number: ").strip()
        if episode.isdigit():
            break
        print("ERROR: Episode must be a number!")

    print("\nOptional parameters (press Enter to use defaults):")
    year = input("Release year (leave empty for any): ").strip()

    quality = get_quality_choice()

    print("\nSubtitle Options:")
    print("[1] Yes")
    print("[2] No (default)")
    subtitle_choice = input("Choose option [1-2]: ").strip()

    language = ""
    if subtitle_choice == "1":
        language = input("Subtitle language (leave empty for English): ").strip()

    # Build command
    command = [
        sys.executable,
        "-m",
        "moviebox_api",
        "download-series",
        title,
        "-s",
        season,
        "-e",
        episode,
        "--stream",
    ]

    if year and year.strip():
        command.extend(["-y", year])
        command.append("-Y")
    if quality:
        command.extend(["-q", quality])

    if subtitle_choice == "1":
        command.append("--caption")
        if language:
            command.extend(["-x", language])
    else:
        command.append("--no-caption")

    print(f"\nExecuting: {' '.join(command)}")

    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print("\nStreaming cancelled.")

    input("\nPress Enter to continue...")


def show_homepage():
    """Show homepage content"""
    clear_screen()
    print("\nHOMEPAGE CONTENT")

    print("\nFetching homepage content...")

    try:
        subprocess.run([sys.executable, "-m", "moviebox_api", "homepage-content"])
    except KeyboardInterrupt:
        print("\nCancelled.")

    input("\nPress Enter to continue...")


def show_popular():
    """Show popular searches"""
    clear_screen()
    print("\nPOPULAR SEARCHES")

    print("\nFetching popular searches...")

    try:
        subprocess.run([sys.executable, "-m", "moviebox_api", "popular-search"])
    except KeyboardInterrupt:
        print("\nCancelled.")

    input("\nPress Enter to continue...")


def show_mirrors():
    """Show mirror hosts"""
    clear_screen()
    print("\nMIRROR HOSTS")

    print("\nDiscovering mirror hosts...")

    try:
        subprocess.run([sys.executable, "-m", "moviebox_api", "mirror-hosts"])
    except KeyboardInterrupt:
        print("\nCancelled.")

    input("\nPress Enter to continue...")


def run_interactive_menu():
    """Run the interactive menu interface"""
    menu_actions = {
        "1": download_movie,
        "2": download_series,
        "3": stream_movie,
        "4": stream_series,
        "5": show_homepage,
        "6": show_popular,
        "7": show_mirrors,
    }

    while True:
        try:
            show_main_menu()
            choice = input("\nEnter your choice [0-7]: ").strip()

            if choice == "0":
                clear_screen()
                print("\nThank you for using MovieBox!\n")
                sys.exit(0)
            elif choice in menu_actions:
                menu_actions[choice]()
            else:
                print("\nERROR: Invalid option. Press Enter to try again...")
                input()
        except KeyboardInterrupt:
            clear_screen()
            print("\nExiting MovieBox Menu...\n")
            sys.exit(0)
        except EOFError as e:
            print(f"\nERROR: An error occurred: {e}")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    run_interactive_menu()
