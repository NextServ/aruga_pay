# **Frappe / ERPNext Docker Environment**

A modular, developer-friendly setup for running **Frappe Framework**, **ERPNext**, and **custom apps** using Docker.
Supports:

* Local development
* Multi-bench setups
* Production deployments with Traefik + SSL
* Custom image building from apps.json (including private repos)

---

# **📦 Prerequisites**

Make sure the following are installed:

* **Git**
* **Docker**
* **Docker Compose**

---

# **🚀 How to Use ARUGA ACCOUNTING (Consumers)**

This is the *simple workflow* for anyone who just wants to run the Frappe/ERPNext container.

1. Clone the repo:

   ```bash
   git clone https://github.com/iaiaian1/docker_scripts -b aruga_acct
   ```
2. Build the image (ERPNext + Aruga accounting):

   ```bash
   docker build --no-cache \
             --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
             --build-arg=FRAPPE_BRANCH=version-15 \
             --build-arg=APPS_JSON_BASE64=WwogICAgewogICAgICAgICJ1cmwiOiAiaHR0cHM6Ly9naXRodWIuY29tL2ZyYXBwZS9lcnBuZXh0IiwKICAgICAgICAiYnJhbmNoIjogInZlcnNpb24tMTUiCiAgICB9LAogICAgewogICAgICAgICJ1cmwiOiAiaHR0cHM6Ly9naXRodWIuY29tL05leHRTZXJ2L2FydWdhX2FjY3QiLAogICAgICAgICJicmFuY2giOiAibWFpbiIKICAgIH0KXQ== \
             --tag=servio/aruga_acct:v0.0.1 \
             --file=Dockerfile .
   ```
3. Start the container:

   ```bash
   docker compose -f compose/compose.custom_local.yaml up -d
   ```
4. Create a site:

   ```bash
   docker compose exec backend bench new-site localhost --mariadb-user-host-login-scope='172.%.%.%'
   ```
5. Default MySQL root password when asked:

   ```
   frappe
   ```
6. Set the Administrator password when asked.
7. Open your browser:

   ```
   http://localhost:8080
   ```
8. To install ERPNext and Aruga Accounting
    ```
    docker compose exec backend bench --site localhost install-app erpnext aruga_acct
    ```
---

# **🛠 How This Works (Developers)**

This repository supports **two development paths**:

### **1. Using prebuilt Docker Compose templates and Frappe's Official Image**

* **Generate** a compose file using the provided overrides.
* Run using:

  ```bash
  docker compose -f <compose.yaml> up -d
  ```
* Includes **Frappe + ERPNext** by default.

### **2. Building your own custom Frappe image**

* Define your apps in `apps.json` and encode it
* Read and customize .env
* Build an image containing your custom apps
* Generate a compose file matching your needs
* Run using your own custom Frappe stack

---

# **🏗 Building a Custom Image**

### **Adding Private Repos**

Update your apps.json entry like:

```json
[
    {
        "url": "https://github.com/frappe/erpnext",
        "branch": "version-15"
    },
    {
        "url": "https://<GITHUB_USERNAME>:<GITHUB_TOKEN>@github.com/repository/app_name",
        "branch": "version-15"
    }
]
```

### **Encode apps.json**

```bash
export APPS_JSON_BASE64=$(base64 -w 0 apps.json)
```

or

```bash
APPS_JSON_BASE64=$(base64 -w 0 apps.json)
```

### **Choose the desired Dockerfile**
This repository uses the **"Layered"** Dockerfile.

> Great for production builds when you’re fine with the dependency versions managed by Frappe. Builds much faster since the base layers are already prepared.

**ℹ️ Source: https://github.com/frappe/frappe_docker/blob/main/docs/container-setup/01-overview.md**

### **Build commands**

```bash
docker build --no-cache \
             --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
             --build-arg=FRAPPE_BRANCH=version-15 \
             --build-arg=APPS_JSON_BASE64=WwogICAgewogICAgICAgICJ1cmwiOiAiaHR0cHM6Ly9naXRodWIuY29tL2ZyYXBwZS9lcnBuZXh0IiwKICAgICAgICAiYnJhbmNoIjogInZlcnNpb24tMTUiCiAgICB9LAogICAgewogICAgICAgICJ1cmwiOiAiaHR0cHM6Ly9naXRodWIuY29tL05leHRTZXJ2L2FydWdhX2FjY3QiLAogICAgICAgICJicmFuY2giOiAibWFpbiIKICAgIH0KXQ== \
             --tag=servio/aruga_acct:v0.0.1 \
             --file=Dockerfile .
```

---

# **🧩 Generating a Compose File**

```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.noproxy.yaml \
  config > compose.custom.yaml
```

---

# **🐳 Useful Docker Commands**

### **Create a Site (for compose.local.yaml) V14**

```bash
docker compose exec backend bench new-site localhost --no-mariadb-socket
docker compose exec backend bench --site localhost install-app erpnext
```
### **Create a Site (for compose.local.yaml) V15**

```bash
docker compose exec backend bench new-site localhost --mariadb-user-host-login-scope='172.%.%.%'
docker compose exec backend bench --site localhost install-app erpnext
```

### **Create a Site (custom domain)**

```bash
docker compose exec backend bench new-site test.local --mariadb-user-host-login-scope='172.%.%.%'
docker compose exec backend bench --site test.local install-app erpnext
```

### **Updating a Container**

```bash
docker compose -f compose/compose.local.yaml pull
docker compose -f compose/compose.local.yaml up -d --remove-orphans
docker compose -f compose/compose.local.yaml up -d --force-recreate --remove-orphans
```

### **Copy file/folder**

**Local → Container**

```bash
docker compose cp db.sql backend:home/frappe/frappe-bench
```

**Container → Local**

```bash
docker compose cp backend:home/frappe/frappe-bench/sites/common_site_config.json .
```

**Copy logs**

```bash
docker compose -f pwd.yml cp backend:/home/frappe/frappe-bench/logs/ ./debug-logs/
```

**Copy site files**

```bash
docker compose -f pwd.yml cp backend:/home/frappe/frappe-bench/sites/mysite.com ./backup/
```

**Increase and max_allowed_packet for big restores**

```bash
docker exec -it docker_scripts-db-1 mariadb --user=root --password=frappe --execute="SET GLOBAL max_allowed_packet = 268435456;"

docker exec -it docker_scripts-db-1 mariadb --user=root --password=frappe --execute="SHOW VARIABLES LIKE 'max_allowed_packet';"
```

---

# **📐 Docker Compose Templates**

Use override files to produce the exact stack you need.

## **Local Development**

**Port-based, HTTP, cron included**

```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.noproxy.yaml \
  -f overrides/compose.backup-cron.yaml \
  config > compose/compose.local.yaml
```

**HTTP Proxy (requires hosts file)**

```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.proxy.yaml \
  -f overrides/compose.backup-cron.yaml \
  config > compose/compose.local_proxy.yaml
```

**HTTP Proxy (requires hosts file) + multi-bench**

```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.multi-bench.yaml \
  -f overrides/compose.mariadb-shared.yaml \
  -f overrides/compose.traefik.yaml \
  -f overrides/compose.backup-cron.yaml \
  config > compose/compose.local_multi_proxy.yaml
```

---

# **⚠️ WIP - 🔐 Production / SSL / HTTPS**

### **Single Site + SSL**

```bash
docker compose --env-file .env \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.backup-cron.yaml \
  config > compose/compose.https.yaml
```

### **Multiple Sites + SSL**

Combine:

```bash
WIP
```

---

# **⚠️ WIP - 🌐 Shared Apps Mode**

Apps get their own volume, useful for multi-project dev.

```bash
docker compose --env-file .env \
  -f compose_shared_apps.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.noproxy.yaml \
  -f overrides/compose.backup-cron.yaml \
  config > compose/compose.shared_local.yaml
```

---

# **⚠️ WIP - 📄 Override Files Reference**

| Override File                      | Purpose                       | When to Use                      | Key Services / Changes     |
| ---------------------------------- | ----------------------------- | -------------------------------- | -------------------------- |
| **compose.backup-cron.yaml**       | Automated backups             | Need automatic DB + files backup | backup-cron service        |
| **compose.custom-domain-ssl.yaml** | Custom domain + SSL           | Production                       | Traefik + cert resolver    |
| **compose.custom-domain.yaml**     | Custom HTTP domain            | Local testing                    | VIRTUAL_HOST settings      |
| **compose.https.yaml**             | Force HTTPS                   | Using Traefik + SSL              | Redirect middleware        |
| **compose.mariadb-secrets.yaml**   | Secrets-based DB passwd       | Swarm / secure deployments       | Uses Docker secrets        |
| **compose.mariadb-shared.yaml**    | Shared MariaDB across benches | Multi-site hosting               | Shared DB host             |
| **compose.mariadb.yaml**           | MariaDB service               | Default setups                   | mariadb:10.6               |
| **compose.multi-bench-ssl.yaml**   | Multi-site SSL                | Multi-tenant prod                | Traefik SSL routing        |
| **compose.multi-bench.yaml**       | Multiple benches              | Dev multi-bench                  | Multiple backends          |
| **compose.noproxy.yaml**           | Remove Traefik                | Classic port-based dev           | Exposes ports 8000/9000    |
| **compose.postgres.yaml**          | PostgreSQL support            | Using Postgres                   | postgres:15                |
| **compose.proxy.yaml**             | Enable Traefik (HTTP only)    | Reverse proxy dev                | web entrypoint             |
| **compose.redis.yaml**             | Redis services                | Queue, Cache, SocketIO           | redis-queue/cache/socketio |
| **compose.traefik-ssl.yaml**       | Traefik + Let’s Encrypt SSL   | Production HTTPS                 | websecure entrypoint       |
| **compose.traefik.yaml**           | Base Traefik Config           | Proxy setups                     | Traefik dashboard          |

---

# **📚 Reference**

Official Frappe Docker documentation:
[https://github.com/frappe/frappe_docker/](https://github.com/frappe/frappe_docker/)
