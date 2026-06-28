# Agent Instructions

## Default Conda Environment
- Environment name: `rc-llm-eval`
- Environment path: `/home/xuelin/miniconda3/envs/rc-llm-eval`
- Prefer running Python commands with `conda run -n rc-llm-eval ...` or `/home/xuelin/miniconda3/envs/rc-llm-eval/bin/python`.

<!-- codex-agent-runtime:start -->

## Runtime Ports And Database Configuration

- Keep this section aligned with the root README when database names, ports, or service defaults change.
- Do not copy secrets from local `.env` files into commits; document only placeholders or compose defaults.

### Database
- Primary database: PostgreSQL.
- Default database name: `oralsea_chinese`.
- Default Compose host and port: `127.0.0.1:5432` mapped from the `postgres` service.
- Default Compose credentials for local development: `POSTGRES_USER=oralsea`, `POSTGRES_PASSWORD=oralsea_dev`.
- Node backend example URL: `postgres://oralsea:oralsea_dev@127.0.0.1:5432/oralsea_chinese`.
- If `DATABASE_URL` is not configured, the Node backend can fall back to JSON seed data for smoke testing.

### Default Ports
- Node business backend: `3100` from `backend_node/.env.example`.
- FastAPI AI service: `8001` (`AI_SERVICE_URL=http://127.0.0.1:8001`).
- Admin web Vite dev server: `5173`.
- PostgreSQL: `5432`.

### Notes For Codex Agents
- Do not copy local `.env` credentials into documentation; use `.env.example` and Compose defaults only.
- Before committing, check `git status --short --branch` and avoid staging unrelated runtime artifacts.

### Source Files Checked
- `docker-compose.yml`
- `backend_node/.env.example`
- `docs/deployment.md`
- `docs/api-design.md`

<!-- codex-agent-runtime:end -->

## GitHub Commit Language

- Use English for all GitHub commit messages and pull/push related commit notes.
