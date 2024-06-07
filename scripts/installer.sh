#!/bin/bash
# installer script for the application
# mostly used for linux os
# desktop at: https://github.com/AndreWohnsland/TimeTracker/blob/master/scripts/timetracker.desktop
# icon at: https://github.com/AndreWohnsland/TimeTracker/blob/master/ui/clock.png

# retuns the latest release tag
get_latest_release_tag() {
  curl -L \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    https://api.github.com/repos/AndreWohnsland/TimeTracker/releases/latest |
    grep '"tag_name":' |
    sed -E 's/.*"([^"]+)".*/\1/'
}

# download the latest release for the corresponding os
download_latest_release() {
  sudo curl -o /usr/bin/timetracker https://github.com/AndreWohnsland/TimeTracker/releases/latest/download/timetracker_ubuntu
  sudo curl -o /usr/share/pixmaps/timetracker.png https://raw.githubusercontent.com/AndreWohnsland/TimeTracker/master/ui/clock.png
  sudo curl -o /usr/share/applications/timetracker.desktop https://raw.githubusercontent.com/AndreWohnsland/TimeTracker/master/scripts/timetracker.desktop
}

# install the application
install() {
  download_latest_release
  sudo chmod +x /usr/bin/timetracker
}

# execute the installer
install
