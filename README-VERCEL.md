Deploying Saraah to Vercel (Docker)

1) Create a Git repository and push this workspace to GitHub.

2) In Vercel, "New Project" → Import from GitHub, select the repo.

3) Set Build & Output (Vercel will detect Dockerfile). Add any Environment Variables required (e.g., `GENIE_API_KEY`).

4) Optional: use Vercel CLI to deploy directly:

```bash
# Install Vercel CLI
npm i -g vercel
# Log in
vercel login
# Deploy from the project folder
vercel --prod
```

Notes:
- The Dockerfile runs Streamlit on `$PORT` (default 8080). Vercel will set the port when running the container.
- If you need background workers or persistent filesystem, prefer a platform like Render or Fly.
