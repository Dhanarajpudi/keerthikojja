# IT Service Desk – DevOps Practical (Q3 + Q4)

Flask ticketing app with SQLite persistence, Docker, Jenkins CI/CD, GitHub and AWS EC2.

## 1. Local deployment on Mac

Install/start Docker Desktop, then run:

```bash
docker --version
docker compose version
docker compose up -d --build
docker ps
curl http://localhost:5000/health
```

Open http://localhost:5000. Create a sample ticket:

```bash
curl -X POST http://localhost:5000/api/tickets -H 'Content-Type: application/json' -d '{"title":"Wi-Fi issue","description":"Cannot connect to office Wi-Fi","requester":"Demo User"}'
curl http://localhost:5000/api/tickets
```

Stop: `docker compose down`. Ticket data remains in the named volume. `docker compose down -v` deletes that volume and its data.

## 2. Push to GitHub

Create an empty GitHub repo named `it-service-desk-devops`, then:

```bash
git init
git add .
git commit -m "Initial IT Service Desk application"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/it-service-desk-devops.git
git push -u origin main
```

Replace the placeholder username.

## 3. AWS EC2 test server

Launch Ubuntu 24.04 LTS EC2. A 2 vCPU / 4 GiB instance is a more comfortable lab size for Jenkins and Docker together; check AWS pricing before launching.

Security group inbound: SSH 22 from your IP, Jenkins 8080 from your IP, app 5000 from your IP (or use an SSH tunnel).

Connect with `ssh -i YOUR_KEY.pem ubuntu@YOUR_EC2_PUBLIC_IP`.

Install Docker:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git python3 python3-venv
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager
sudo docker run --rm hello-world
```

Install Jenkins LTS by following the current official Ubuntu instructions: https://www.jenkins.io/doc/book/installing/linux/ (Jenkins Java/repository requirements can change).

After installation:

```bash
sudo systemctl enable --now jenkins
sudo usermod -aG docker jenkins
sudo mkdir -p /opt/it-service-desk/data
sudo chown -R jenkins:jenkins /opt/it-service-desk
sudo systemctl restart jenkins
sudo -u jenkins docker ps
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Docker group membership grants root-equivalent privileges. Use this only on a trusted lab instance.

Open `http://YOUR_EC2_PUBLIC_IP:8080`, unlock Jenkins, install suggested plugins including Pipeline and Git.

## 4. Create Jenkins Pipeline job

1. New Item → `IT-Service-Desk-Pipeline` → Pipeline.
2. Pipeline Definition: Pipeline script from SCM.
3. SCM: Git.
4. Repository URL: `https://github.com/YOUR_GITHUB_USERNAME/it-service-desk-devops.git`.
5. Branch: `*/main`; Script Path: `Jenkinsfile`.
6. Save → Build Now.

For a private repository, configure Git credentials in Jenkins. Never hardcode tokens in the Jenkinsfile.

## 5. Verify on EC2

```bash
docker ps
docker image ls
curl http://localhost:5000/health
docker logs it-service-desk-test --tail 100
sudo systemctl status docker --no-pager
sudo systemctl status jenkins --no-pager
sudo journalctl -u jenkins -n 100 --no-pager
sudo journalctl -u docker -n 50 --no-pager
ls -ld /opt/it-service-desk /opt/it-service-desk/data
id jenkins
groups jenkins
```

Open `http://YOUR_EC2_PUBLIC_IP:5000`.

## 6. Q3/Q4 demonstration checklist

- [ ] App runs locally and creates/lists/updates tickets.
- [ ] Docker image builds and container health check passes.
- [ ] GitHub stores source, Dockerfile and Jenkinsfile.
- [ ] Jenkins checks out code and runs unit tests.
- [ ] Jenkins builds and tags image using its build number.
- [ ] Jenkins smoke-tests the image and deploys to test container.
- [ ] EC2 application responds on port 5000.
- [ ] SQLite data persists in the mounted host directory.
- [ ] Show Linux users, permissions, service status and logs.

This is a classroom lab, not production-hardened. Production requires HTTPS, authentication, authorization, secret management, backups, monitoring, image scanning and restricted network access. Do not expose Jenkins or an unauthenticated demo app publicly.
