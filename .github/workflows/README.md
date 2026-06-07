# CI/CD Pipeline

## How it works

```
git push origin main
        │
        ▼
┌─────────────────┐
│   JOB 1: test   │  Runs pytest with a real Postgres service container
└────────┬────────┘
         │ passes
         ▼
┌─────────────────┐
│   JOB 2: build  │  Builds backend + frontend Docker images
│                 │  Pushes to ghcr.io (GitHub Container Registry)
└────────┬────────┘
         │ pushed
         ▼
┌─────────────────┐
│  JOB 3: deploy  │  SSH into Droplet → git pull → docker compose up
└─────────────────┘
```

## Required GitHub Secrets

Go to: **GitHub repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret name       | Value                                        |
|-------------------|----------------------------------------------|
| `DROPLET_IP`      | Your DigitalOcean Droplet IP address         |
| `SSH_PRIVATE_KEY` | Your private SSH key (see below)             |

### How to get SSH_PRIVATE_KEY

**Option A — Use existing key (if you already SSH into the Droplet):**
```bash
# On your local machine, print your private key:
cat ~/.ssh/id_rsa
# or
cat ~/.ssh/id_ed25519
```
Copy the entire output including `-----BEGIN ... KEY-----` lines.

**Option B — Generate a new dedicated key for CI:**
```bash
# On your local machine:
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy -N ""

# Add the PUBLIC key to the Droplet:
ssh-copy-id -i ~/.ssh/github_deploy.pub root@YOUR_DROPLET_IP
# or manually: cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys on the Droplet

# Copy the PRIVATE key value to GitHub secret:
cat ~/.ssh/github_deploy
```

Paste the private key as the `SSH_PRIVATE_KEY` secret value.
