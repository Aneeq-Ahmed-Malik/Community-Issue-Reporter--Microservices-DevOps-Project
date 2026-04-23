# Community Issue Reporter - Microservices DevOps Project

This project implements a complete deployment pipeline for a multi-user microservices application on AWS EC2.

## Problem Solved

Residents need a simple shared platform to report neighborhood issues (potholes, broken lights, waste collection delays), track status, and receive updates.

## Microservices

1. **auth-service**: User registration, login, and user lookup.
2. **issue-service**: Create/list/update issues and comments.
3. **notification-service**: Receives and stores notifications when issue events occur.

## Assignment Coverage

- **Docker**: One Dockerfile per microservice.
- **Terraform**: Provisions AWS VPC, subnet, routing, security group, and EC2 host.
- **Ansible**: Configures EC2 with Docker, kind, kubectl, and ArgoCD.
- **Kubernetes**: Deployment + Service for each microservice.
- **CI/CD (GitHub Actions + ArgoCD)**: Build and push Docker images on code changes, update image tags in manifests, and let ArgoCD auto-sync cluster state from repo.

## Repository Structure

```text
Project_3/
  services/
    auth-service/
    issue-service/
    notification-service/
  terraform/
  automation/ansible/
  k8s/
  .github/workflows/ci-cd.yml
```

## Prerequisites

- AWS account with permissions to create VPC/EC2/Security Groups
- Terraform >= 1.5
- Ansible >= 2.14
- Docker Hub account
- GitHub repository with Actions enabled

## 1. Local Run (Optional Smoke Test)

```bash
docker compose up --build
```

Endpoints:

- Auth: `http://localhost:8001`
- Issue: `http://localhost:8002`
- Notification: `http://localhost:8003`

## 2. Provision Infrastructure (Terraform)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
terraform init
terraform plan
terraform apply
```

After apply, note outputs:

- `ec2_public_ip`
- `ansible_inventory_host`

## 3. Configure EC2 Host (Ansible)

1. Copy inventory template and update host details:
  Use `automation/ansible/inventories/hosts.ini.example` as the template and save it as `hosts.ini`.

2. Set your Git repo URL in:
  Update `automation/ansible/group_vars/all.yml` (`repo_url`).

3. Run playbook:

```bash
cd automation/ansible
export ANSIBLE_ROLES_PATH="$PWD/roles"
ansible-playbook -i inventories/hosts.ini playbooks/site.yml
```

## 4. Kubernetes Deployment

Manifests are in `k8s/` and include:

- namespace
- service deployments/services
- ArgoCD application manifest

NodePort exposure on EC2:

- Issue API: `30080`
- Auth API: `30081`

## 5. CI/CD Setup

Set GitHub repository secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Workflow file:

- `.github/workflows/ci-cd.yml`

Pipeline behavior:

1. Builds and pushes all three service images.
1. Updates image tags in Kubernetes deployment manifests.
1. Commits manifest updates back to `main`.
1. ArgoCD auto-syncs updated manifests.

## 6. ArgoCD Setup Notes

Update repo URL placeholders in:

- `k8s/argocd/application.yaml`
- `automation/ansible/group_vars/all.yml`

Access ArgoCD on EC2 (example):

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

## Minimal API Flow Example

1. Register user:

```http
POST /users/register
```

1. Create issue with `reporter_id`:

```http
POST /issues
```

1. Update issue status:

```http
PATCH /issues/{issue_id}/status
```

1. Check generated notifications:

```http
GET /notifications?user_id={user_id}
```

## Notes

- This is a functional project scaffold focused on deployment pipeline completeness.
- Data is in-memory for demo simplicity. For production, replace with managed persistence (RDS/DynamoDB).
