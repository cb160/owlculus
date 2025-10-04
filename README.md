# Owlculus

<p align="center">
  <img src="https://i.imgur.com/Cuf4hMK.png" />
</p>

Owlculus is a comprehensive OSINT case management platform built for solo work or investigative teams. Manage cases,
collaborate, and run OSINT tools directly in your browser.

**100% free and open-source forever, no matter what.**

> **Active Development**: Note that Owlculus is under active development. Run `git pull` in the repo root regularly for
> updates. Never deploy the "
> dev" branch to production!

## Features

- **Case Management**: Create and track cases with customizable report numbering
- **Multi-User Collaboration**: Role-based access controls (Admin, Investigator, Analyst)
- **Entity System**: Track individual people, companies, domains, IP addresses, and vehicles each with dedicated
  notetaking
- **Evidence Management**: Organized file storage with folder templates and integration with the browser extension
- **OSINT Plugin Ecosystem**: Run popular open-source and custom OSINT tools right in your browser
- **Cross-Case Correlation**: Discover connections between investigations with the Correlation Scan plugin
- **Automated Hunts**: Multi-step OSINT workflows for comprehensive research (WIP)
- **Browser Extension**: Capture web pages as HTML or screenshots as you investigate and save directly to case evidence
- **RESTful API**: Complete API backend for easy automation and integrations

## Running Locally (Docker or Podman)

Owlculus ships with Docker Compose manifests that also work with Podman. The `Makefile` and helper scripts auto-detect
whichever engine you have installed, so the same commands work across platforms.

### Prerequisites

- Docker with Compose v2 **or** Podman 4.4+ (which includes `podman compose`)
- `make` (pre-installed on most macOS/Linux distros; install via `sudo apt install make` inside WSL)

For Windows users without Docker Desktop, you can run everything inside WSL using Podman:

```bash
sudo apt update
sudo apt install podman podman-compose
podman --version
```

If you are using Podman on Windows outside of WSL, initialise the Podman machine once:

```bash
podman machine init
podman machine start
```

### Quickstart

```bash
git clone https://github.com/be0vlk/owlculus.git
cd owlculus

# Start the development stack (auto-detects docker or podman)
make start-dev

# Visit the frontend (default): http://localhost:5173
# API (default): http://localhost:8000
```

To stop the stack run `make stop`. If compose detection fails for your setup, override it explicitly:

```bash
COMPOSE_CMD="podman compose" make start-dev
```

The same `COMPOSE_CMD` variable works with helper scripts, including `./scripts/run_test_data.sh`.

### Running Podman Rootful on WSL

WSL currently lacks the `tun` kernel module, so rootless Podman networking is unreliable. Run the stack with rootful
permissions instead:

```bash
sudo podman system migrate   # once, ensures root storage is initialised
sudo COMPOSE_CMD="podman compose" make start-dev
```

If you only need the backend/frontend (for example when using an external database), you can skip dependencies:

```bash
sudo COMPOSE_CMD="podman compose" podman compose up --no-deps backend frontend
```

### Using an External PostgreSQL

You can point Owlculus at a PostgreSQL instance that lives outside your container host (for example, a Flux-managed
Bitnami deployment on your Raspberry Pi cluster). Update environment variables before starting the stack:

```bash
export POSTGRES_HOST=192.168.1.50        # Cluster node or load balancer
export POSTGRES_PORT=31432               # NodePort or load balancer port
export POSTGRES_USER=owlculus
export POSTGRES_PASSWORD=gGiknNX7MbKfc8rQCXlt2ThUl
export POSTGRES_DB=owlculus

sudo COMPOSE_CMD="podman compose" podman compose up --no-deps backend frontend db-init
```

With Flux, add the `clusters/my-cluster/apps/owlculus-postgres` kustomization and the Bitnami chart will provision a
stateful PostgreSQL with persistent storage and a NodePort (31432 by default).

## Documentation
The information you need to get started is hosted right here on GitHub in the [Wiki](https://github.com/be0vlk/owlculus/wiki) but if you need any additional guidance, please feel free to open a [Discussion](https://github.com/be0vlk/owlculus/discussions)

## Contributing
GitHub Issues and Pull Requests always welcome! Oh and make sure to at least read the CONTRIBUTING.md readme first for some basic guidelines.

If you find the app useful and feel so inclined, please consider fueling my future coding sessions with a donation
below. Anything and everything helps and is greatly appreciated :)

<a href="https://www.buymeacoffee.com/be0vlk" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
