# Install Worktree

This command sets up an isolated worktree environment with custom port configuration.

## Parameters
- Worktree path: {0}
- Server port: {1}
- Client port: {2}

## Read
- .env.sample (from parent repo)
- ./apps/apps/Server/.env.sample (from parent repo)
- ./apps/apps/Client/.env.example (from parent repo)
- .mcp.json (from parent repo)
- playwright-mcp-config.json (from parent repo)

## Steps

1. **Navigate to worktree directory**
   ```bash
   cd {0}
   ```

2. **Create port configuration file**
   Create `.ports.env` with:
   ```
   SERVER_PORT={1}
   CLIENT_PORT={2}
   VITE_SERVER_URL=http://localhost:{1}
   ```

3. **Copy and update .env files**
   - Copy `.env` from parent repo if it exists
   - Append `.ports.env` contents to `.env`
   - Copy `apps/Server/.env` from parent repo if it exists
   - Append `.ports.env` contents to `apps/Server/.env`
   - Copy `apps/Client/.env` from parent repo if it exists
   - Update `VITE_API_URL` in `apps/Client/.env` to use the Server port: `http://localhost:{1}/api`

4. **Copy and configure MCP files**
   - Copy `.mcp.json` from parent repo if it exists
   - Copy `playwright-mcp-config.json` from parent repo if it exists
   - These files are needed for Model Context Protocol and Playwright automation
   
   After copying, update paths to use absolute paths:
   - Get the absolute worktree path: `WORKTREE_PATH=$(pwd)`
   - Update `.mcp.json`:
     - Find the line containing `"./playwright-mcp-config.json"`
     - Replace it with `"${WORKTREE_PATH}/playwright-mcp-config.json"`
     - Use a JSON-aware tool or careful string replacement to maintain valid JSON
   - Update `playwright-mcp-config.json`:
     - Find the line containing `"dir": "./videos"`
     - Replace it with `"dir": "${WORKTREE_PATH}/videos"`
     - Create the videos directory: `mkdir -p ${WORKTREE_PATH}/videos`
   - This ensures MCP configuration works correctly regardless of execution context

5. **Install Server dependencies**
   ```bash
   cd apps/Server && uv sync --all-extras
   ```

6. **Install Client dependencies**
   ```bash
   cd ../apps/Client && npm install
   ```

7. **Setup database**
   ```bash
   cd ../.. && ./scripts/reset_db.sh
   ```

## Error Handling
- If parent .env files don't exist, create minimal versions from .env.sample/.env.example files
- For apps/Client/.env, ensure VITE_API_URL points to the correct Server port
- Ensure all paths are absolute to avoid confusion

## Report
- List all files created/modified (including MCP configuration files)
- Show port assignments
- Confirm dependencies installed
- Note any missing parent .env files (root, Server, Client) that need user attention
- Note any missing MCP configuration files
- Confirm apps/Client/.env has correct VITE_API_URL pointing to worktree Server port
- Show the updated absolute paths in:
  - `.mcp.json` (should show full path to playwright-mcp-config.json)
  - `playwright-mcp-config.json` (should show full path to videos directory)
- Confirm videos directory was created