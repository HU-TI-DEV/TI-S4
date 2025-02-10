echo "Installing post compose dependencies"
pwd
curl -fsSL https://bun.sh/install | bash
echo 'export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.zshrc
source ~/.bashrc
cd _slidev
bun install
cd slidev-theme-ti
bun install
bunx playwright install chromium
