#!/bin/bash
curl https://mise.run/bash | sh
NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)" >> ~/.bashrc
source ~/.bashrc
mise install