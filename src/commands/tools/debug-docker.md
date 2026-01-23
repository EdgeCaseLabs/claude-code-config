# Docker Container Debugging Guide

This document outlines a systematic approach for debugging and fixing Docker container issues using an iterative process of observation, diagnosis, and correction.

## The Debug Loop Process

### 1. Observe - Check Container Status
```bash
# List all containers and their status
docker compose ps

# Check which containers are exiting
docker compose ps | grep -E "Exit|Restarting"
```

### 2. Investigate - Examine Logs
```bash
# View logs for a specific service
docker compose logs servicename

# View last 100 lines with timestamps
docker compose logs --tail=100 --timestamps servicename

# Follow logs in real-time
docker compose logs -f servicename

# Search for errors across all services
docker compose logs | grep -E "ERROR|error|Error|failed|Failed|FAILED|Exception|exception"

# Filter for specific error types
docker compose logs servicename | grep -E "NU1301|NU1900|Permission denied|Cannot find|Unable to"
```

### 3. Diagnose - Identify Root Cause

#### Common Error Patterns and Their Meanings

| Error Pattern | Likely Cause | Investigation Commands |
|--------------|--------------|----------------------|
| `NU1301`, `NU1900` | NuGet authentication failure | `docker compose exec servicename printenv \| grep -E "NUGET\|TOKEN\|VSS"` |
| `Permission denied` | File permissions issue | `ls -la /path/to/file` |
| `Cannot find module` | Missing dependencies | `docker compose exec servicename ls -la /app` |
| `Connection refused` | Service not ready or wrong port | `docker compose ps` to check service status |
| `Exit code 1` | Generic failure - check logs | `docker compose logs --tail=200 servicename` |
| `OCI runtime create failed` | Container startup issue | Check Dockerfile CMD/ENTRYPOINT |

### 4. Debug Inside Container
```bash
# Execute commands inside running container
docker compose exec servicename /bin/bash

# For stopped containers, override entrypoint
docker compose run --entrypoint /bin/bash servicename

# Check environment variables
docker compose exec servicename printenv

# Test specific commands
docker compose exec servicename dotnet --version
docker compose exec servicename ls -la /app
```

### 5. Fix - Apply Solutions

#### Fix Categories and Approaches

##### A. Environment Variable Issues
```yaml
# In docker-compose.yml
services:
  myservice:
    environment:
      MY_VAR: value                    # Hardcoded value
      MY_VAR: "${MY_VAR}"              # From .env file with substitution
      MY_VAR:                          # From .env file without substitution
```

##### B. Build Arguments Issues
```yaml
# In docker-compose.yml
services:
  myservice:
    build:
      context: .
      args:
        BUILD_ARG: "${BUILD_ARG}"      # Pass from .env to build
        BUILD_ARG:                      # Alternative syntax
```

##### C. File Permission Issues
```bash
# Fix on host before building
chmod +x script.sh

# Or in Dockerfile
RUN chmod +x /app/script.sh
```

##### D. Dependency Issues
```dockerfile
# In Dockerfile - ensure dependencies are installed
RUN apt-get update && apt-get install -y required-package
```

### 6. Rebuild - Apply Changes
```bash
# Rebuild without cache to ensure changes take effect
docker compose build --no-cache servicename

# Or rebuild all services
docker compose build --no-cache

# For build argument changes, source .env first
source .env && docker compose build --no-cache servicename
```

### 7. Test - Verify Fix
```bash
# Start fresh (removes containers but keeps volumes)
docker compose down
docker compose up servicename

# Complete fresh start (removes everything)
docker compose down -v
docker compose up servicename

# Test with dependencies
docker compose up -d dependency1 dependency2
sleep 10  # Wait for services to be ready
docker compose up servicename
```

### 8. Iterate - Repeat if Necessary
If issues persist, return to step 2 and examine new error messages.

## Debugging Workflow Examples

### Example 1: Service Won't Start
```bash
# 1. Check status
docker compose ps myservice
# Shows: Exit 1

# 2. Check logs
docker compose logs --tail=50 myservice
# Shows: "Error: Cannot find module '/app/index.js'"

# 3. Investigate container filesystem
docker compose run --entrypoint /bin/bash myservice
ls -la /app/
# Missing index.js

# 4. Check Dockerfile
cat Dockerfile
# COPY statement incorrect

# 5. Fix Dockerfile
# Update COPY statement

# 6. Rebuild and test
docker compose build --no-cache myservice
docker compose up myservice
```

### Example 2: Authentication Failure
```bash
# 1. Check logs
docker compose logs myservice | grep -i auth
# Shows: "Authentication failed"

# 2. Check environment variables
docker compose exec myservice printenv | grep -i token
# TOKEN not set

# 3. Check docker-compose.yml
grep -A5 "environment:" docker-compose.yml
# Missing TOKEN variable

# 4. Add to docker-compose.yml
# environment:
#   AUTH_TOKEN: "${AUTH_TOKEN}"

# 5. Verify .env file
grep AUTH_TOKEN .env
# Ensure token exists

# 6. Restart with new config
source .env && docker compose up myservice
```

## Quick Debug Commands Reference

```bash
# Service status and health
docker compose ps
docker compose ps --services --filter "status=running"
docker compose ps --services --filter "status=exited"

# Logs investigation
docker compose logs --tail=100 servicename
docker compose logs --follow servicename
docker compose logs servicename 2>&1 | grep -i error
docker compose logs --since "10m" servicename

# Container inspection
docker compose exec servicename printenv | sort
docker compose exec servicename cat /etc/os-release
docker compose exec servicename df -h
docker compose exec servicename ps aux

# Network debugging
docker compose exec servicename ping otherservice
docker compose exec servicename netstat -tuln
docker compose exec servicename curl http://otherservice:port/health

# File system checks
docker compose exec servicename ls -la /app
docker compose exec servicename find / -name "*.log" 2>/dev/null
docker compose exec servicename cat /app/config.json

# Process debugging
docker compose top servicename
docker compose exec servicename top

# Resource usage
docker stats servicename
docker compose exec servicename free -h
```

## Debug Checklist

When a container fails to start or crashes:

1. ✅ **Check exit code**: `docker compose ps servicename`
2. ✅ **Read recent logs**: `docker compose logs --tail=100 servicename`
3. ✅ **Search for errors**: `docker compose logs servicename | grep -i error`
4. ✅ **Verify environment**: `docker compose exec servicename printenv`
5. ✅ **Check file permissions**: `docker compose exec servicename ls -la /app`
6. ✅ **Test dependencies**: Can the service reach databases/other services?
7. ✅ **Verify configuration**: Are config files present and valid?
8. ✅ **Check resources**: `docker stats` - enough memory/CPU?
9. ✅ **Review Dockerfile**: Correct base image? All files copied?
10. ✅ **Test locally**: Can you run the app outside Docker?

## Common Fixes Reference

| Problem | Solution |
|---------|----------|
| Service exits immediately | Check CMD/ENTRYPOINT in Dockerfile, verify executable exists |
| Permission denied | `chmod +x` files before COPY or RUN chmod in Dockerfile |
| Cannot connect to database | Ensure depends_on, check connection string, verify network |
| Environment variable not set | Check .env file, docker-compose.yml environment section |
| Package not found | Rebuild with --no-cache, check package manager configuration |
| Port already in use | Change port mapping in docker-compose.yml |
| Out of memory | Increase Docker memory limits or optimize application |
| SSL/TLS errors | Update certificates, check HTTPS settings |
| Timezone issues | Set TZ environment variable |
| Locale errors | Set LANG and LC_ALL environment variables |

## Best Practices

1. **Always check logs first** - They usually contain the specific error
2. **Use --no-cache when rebuilding** - Ensures fresh build after fixes
3. **Test incrementally** - Fix one issue at a time
4. **Document fixes** - Add comments in Dockerfile/docker-compose.yml
5. **Version control everything** - Track what changes fixed issues
6. **Use health checks** - Add healthcheck to docker-compose.yml
7. **Set resource limits** - Prevent runaway containers
8. **Use specific image tags** - Avoid unexpected updates with 'latest'
9. **Keep containers focused** - One service per container
10. **Log verbosely during debug** - Increase log levels temporarily

## Emergency Recovery

If everything is broken:
```bash
# Stop everything
docker compose down -v

# Clean up Docker system
docker system prune -a --volumes

# Rebuild everything fresh
docker compose build --no-cache
docker compose up
```

## Tips for Efficient Debugging

- Use `docker compose logs -f servicename &` to tail logs in background while working
- Create a debug compose file: `docker-compose.debug.yml` with extra logging
- Use `--scale servicename=0` to disable problematic services temporarily
- Keep a working configuration backup before making changes
- Use Docker Desktop's GUI for quick container inspection
- Set up log aggregation for multi-container debugging
- Use `docker compose config` to validate YAML syntax before running