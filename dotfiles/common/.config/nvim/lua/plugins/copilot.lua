return {
  -- Official GitHub Copilot
  {
    "github/copilot.vim",
    enabled = false,
    event = "InsertEnter",
    cmd = "Copilot",
    config = function()
      -- Enable Copilot for all filetypes (overrides any defaults)
      vim.g.copilot_filetypes = { ["*"] = true }
    end,
  },
}
