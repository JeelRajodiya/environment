#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../dotfiles" && pwd)"
packages=(common agents)

case "$(uname)" in
    Linux) packages+=(linux) ;;
    Darwin) packages+=(macos) ;;
    *) echo "Unsupported OS: $(uname)" >&2; exit 1 ;;
esac

command -v stow >/dev/null || {
    echo "GNU Stow is required. Run bin/bootstrap.sh first." >&2
    exit 1
}

# Codex discovers symlinked skill directories, but not the SKILL.md file links
# created inside real directories by Stow's --no-folding mode.
skill_roots=(.agents/skills .codex/skills)
for root in "${skill_roots[@]}"; do
    source_root="$DOTFILES_DIR/agents/$root"
    [ -d "$source_root" ] || continue
    for source_skill in "$source_root"/*; do
        [ -d "$source_skill" ] || continue
        target_skill="$HOME/$root/$(basename "$source_skill")"
        if [ -L "$target_skill" ] && [ "$(realpath "$target_skill")" = "$source_skill" ]; then
            rm "$target_skill"
        fi
    done
done

# Remove dangling or obsolete symlinks pointing to this repo before stowing
while IFS= read -r -d '' link; do
    target="$(readlink "$link")"
    case "$target" in
        "$DOTFILES_DIR"/*|*linuxConfig/dotfiles*|*linuxConfig/ubuntu*)
            if [ ! -e "$link" ]; then
                rm "$link"
            fi
            ;;
    esac
done < <(
    find "$HOME" -maxdepth 1 -type l -print0
    for dir in .ssh .config .agents .claude .codex .pi "Library/Application Support/k9s" "Library/Application Support/lazygit"; do
        [ ! -d "$HOME/$dir" ] || find "$HOME/$dir" -maxdepth 2 -type l -print0
    done
    [ ! -L "$HOME/.local/share/plasma" ] || printf '%s\0' "$HOME/.local/share/plasma"
)

stow --no-folding --dir="$DOTFILES_DIR" --target="$HOME" "${packages[@]}"

for root in "${skill_roots[@]}"; do
    source_root="$DOTFILES_DIR/agents/$root"
    [ -d "$source_root" ] || continue
    for source_skill in "$source_root"/*; do
        [ -d "$source_skill" ] || continue
        target_skill="$HOME/$root/$(basename "$source_skill")"
        [ -d "$target_skill" ] || continue
        [ -L "$target_skill" ] && continue

        while IFS= read -r -d '' path; do
            relative="${path#"$target_skill"/}"
            expected="$source_skill/$relative"
            if [ -d "$path" ] && [ ! -L "$path" ]; then
                [ -d "$expected" ] || { echo "Unmanaged skill directory: $path" >&2; exit 1; }
            elif [ ! -L "$path" ] || [ "$(realpath "$path")" != "$(realpath "$expected")" ]; then
                echo "Unmanaged skill file: $path" >&2
                exit 1
            fi
        done < <(find "$target_skill" -mindepth 1 -print0)

        rm -rf "$target_skill"
        ln -s "$source_skill" "$target_skill"
    done
done
echo "Already linked: ${packages[*]}"
