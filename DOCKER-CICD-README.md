# QuickBite: Docker & CI/CD Guide

This guide covers two ways to run the QuickBite Orders API, from the most basic
to the most automated. Follow them in order — each one builds on the last.

1. **Docker Container** — packaging the app so it runs identically anywhere
2. **CI/CD with GitHub Actions** — automatically testing, building, and publishing on every push

> **Before the seminar:** test both sections yourself in a fresh Codespace,
> in this exact order.

---

## 1. Running QuickBite in a Docker Container

### Step 1 — Create `.dockerignore` (repo root)
```
__pycache__
*.pyc
.git
.pytest_cache
logs/*.log
.devcontainer
```

### Step 2 — Create `Dockerfile` (repo root, same level as `requirements.txt`)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN mkdir -p logs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 3 — Build the image
```bash
docker build -t quickbite-orders:latest .
```
This reads the Dockerfile top to bottom — installs Python, installs
dependencies, copies the code in, and packages it all into one image.

### Step 4 — Run the container
```bash
docker run -d --name quickbite -p 8000:8000 quickbite-orders:latest
```
- `-d` runs it in the background
- `--name quickbite` gives it a friendly name
- `-p 8000:8000` maps the Codespace's port 8000 to the container's port 8000

### Step 5 — Confirm it's running
```bash
docker ps
```
`quickbite` should be listed with status `Up`.

### Step 6 — Watch its logs
```bash
docker logs -f quickbite
```

### Step 7 — Test it
In a second terminal:
```bash
curl localhost:8000/health
```
Watch the log stream update live in the first terminal.

### Step 8 — Show it's isolated
```bash
docker exec -it quickbite bash
ls
cat app/main.py
exit
```
**Teaching point:** this just opened a shell *inside* the running container —
a separate, isolated Linux environment. The same container run on a laptop, a
company server, or a Codespace behaves identically. That's the promise of
Docker: "works on my laptop" stops being an excuse.

### Step 9 — Stop and clean up
```bash
docker stop quickbite
docker rm quickbite
```

---

## 2. CI/CD Pipeline with GitHub Actions

Automatically tests and builds the code every time it's pushed — no manual
steps needed.

### Step 1 — Create the workflow folder
```bash
mkdir -p .github/workflows
```

### Step 2 — Create `.github/workflows/ci-cd.yml`
```yaml
name: QuickBite CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest -v

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t quickbite-orders:${{ github.sha }} .

      - name: Confirm image built
        run: docker images | grep quickbite-orders
```

**What this does:**
- `test` job — checks out the code, installs dependencies, runs `pytest`. If
  any test fails, the pipeline stops here and `build` never runs.
- `build` job — only runs if `test` passes (`needs: test`), then builds the
  Docker image using the same `Dockerfile` from Section 2. This confirms the
  image builds cleanly, without pushing it anywhere yet.

### Step 3 — Commit and push
```bash
git add .
git commit -m "Add CI/CD pipeline"
git push
```

### Step 4 — Watch it run
Go to the repo on GitHub.com → **Actions** tab → click into the running
workflow to watch each step execute in real time.

### Step 5 — Live demo: break it on purpose
In `tests/test_orders.py`, temporarily change:
```python
assert data["total"] == 498
```
to:
```python
assert data["total"] == 999
```

Push it:
```bash
git add .
git commit -m "Break a test on purpose"
git push
```

Go to the Actions tab — the pipeline turns **red** at the `test` step, and
`build` never runs. This is the exact lesson: a broken test stops broken code
from being shipped.

**Fix it back**, push again, watch it turn green.

---

## 3. Deploying the Image: Build in CI, Deploy in Codespace

GitHub Actions can't reach into a live Codespace directly — the runner and the
codespace are separate machines with no network path between them. The
standard, real-world pattern instead: CI **builds and pushes** the image to a
registry, and a separate **deploy step pulls and runs it** wherever it's
needed — in this case, the student's own Codespace, standing in for "a
server." This is exactly how CI/CD works in production: Actions never SSHs
into a live server directly; it pushes an image, and the server pulls it.

### Step 1 — Update the workflow to push to GHCR

Replace the `build` job in `.github/workflows/ci-cd.yml` with:

```yaml
name: QuickBite CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest -v

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository_owner }}/quickbite-orders:latest
            ghcr.io/${{ github.repository_owner }}/quickbite-orders:${{ github.sha }}
```

- `permissions: packages: write` lets this workflow publish to GitHub's
  built-in container registry (GHCR) — `secrets.GITHUB_TOKEN` is auto-provided
  for every workflow run, no extra secret needed.
- `build-and-push` logs in to `ghcr.io`, then builds and pushes the image,
  tagged both `latest` and with the commit SHA.

### Step 2 — Push and watch it publish
```bash
git add .
git commit -m "Push image to GHCR in CI"
git push
```
Go to the **Actions** tab, watch `build-and-push` succeed.

### Step 3 — Make the package visible (one-time, per repo)
GHCR packages are private by default, even in a public repo. To fix this:
- Go to the GitHub profile → **Packages** tab → click `quickbite-orders`
- Click **Package settings** (bottom right)
- Under **Danger Zone**, click **Change visibility** → set to **Public**

### Step 4 — Deploy: pull and run in the Codespace
```bash
docker pull ghcr.io/YOUR-GITHUB-USERNAME/quickbite-orders:latest
docker run -d --name quickbite-deployed -p 8000:8000 ghcr.io/YOUR-GITHUB-USERNAME/quickbite-orders:latest
```

Test it:
```bash
curl localhost:8000/health
```

**Teaching point:** this image was never built on this machine. It was built
by GitHub's servers when the code was pushed, and stored in a registry. Just
now, the exact same image was pulled and run here. This is precisely how a
real deployment works — laptop, company server, or Codespace, same image,
same behavior, every time.

### Step 5 — Clean up
```bash
docker stop quickbite-deployed
docker rm quickbite-deployed
```

---

## Notes

- **Fully automatic deploy** (CI triggering the pull-and-run step itself,
  rather than typing it manually) needs a self-hosted GitHub Actions runner
  inside each student's Codespace. This adds real setup and security overhead
  for a 2-day seminar and isn't worth it — the manual pull step above teaches
  the same "CI publishes, deploy pulls" concept without the added risk.
- **Verify before the seminar:** confirm `docker/build-push-action@v6` and
  `docker/login-action@v3` work cleanly with the Codespace's Docker-in-Docker
  setup (the `moby: false` fix), and confirm the `pytest.ini` fix
  (`pythonpath = .`) is already in the repo so `pytest` runs clean in CI.
