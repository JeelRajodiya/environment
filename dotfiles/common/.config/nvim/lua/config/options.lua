-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

local o = vim.opt

-- Enable true color support
o.termguicolors = true

o.tabstop = 4
o.shiftwidth = 4
o.expandtab = true
o.smartindent = true

o.encoding = "utf-8"
o.fileencoding = "utf-8"

-- disable word wrap:
o.wrap = false
o.virtualedit = ""
o.mousescroll = "ver:1,hor:1"
o.sidescroll = 10
o.sidescrolloff = 10
o.scrolloff = 8
o.cursorline = true
o.cursorlineopt = "number"

o.number = true
o.relativenumber = true

-- shell and search settings
o.shell = "zsh"
o.ignorecase = true
o.smartcase = true
o.clipboard = "unnamedplus"
o.laststatus = 3

o.guicursor =
  "n-v-c:block-blinkwait700-blinkon400-blinkoff250,i:ver25-blinkwait700-blinkon400-blinkoff250,r:hor20-blinkwait700-blinkon400-blinkoff250"

-- Neovide GUI settings (only apply when running inside Neovide)
if vim.g.neovide then
  -- Scroll: near-instant, no delay
  vim.g.neovide_scroll_animation_length = 0.0
  vim.g.neovide_scroll_animation_far_lines = 0

  -- Transparency: match Ghostty (90% opacity, gray tint, blur)
  vim.g.neovide_opacity = 0.9
  vim.g.neovide_normal_opacity = 1.0
  vim.g.neovide_window_blurred = true

  -- Window padding
  vim.g.neovide_padding_top = 10
  vim.g.neovide_padding_bottom = 10
  vim.g.neovide_padding_left = 10
  vim.g.neovide_padding_right = 10

  -- Misc
  vim.g.neovide_hide_mouse_when_typing = true
  vim.g.neovide_refresh_rate = 120
  vim.g.neovide_cursor_smooth_blink = true
  vim.g.neovide_floating_shadow = false
  vim.g.neovide_floating_corner_radius = 0.3
  vim.g.neovide_show_border = false
end

-- Disable inline virtual text (applied via autocmd to override LazyVim defaults)
vim.api.nvim_create_autocmd("LspAttach", {
  callback = function()
    vim.diagnostic.config({
      virtual_text = false,
      float = {
        border = "rounded",
        source = true,
      },
      signs = true,
      underline = true,
    })
  end,
  once = true,
})
