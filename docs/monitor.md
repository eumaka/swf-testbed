# Monitor Integration

The SWF Monitor provides web interface and API services for the testbed.

## Starting the Monitor

### Dual Server Configuration

The monitor runs on two ports for different purposes:

```bash
# Start monitor with both HTTP and HTTPS
../swf-monitor/start_django_dual.sh
```

This creates:
- **HTTP Server (port 8002)**: REST logging from agents (no authentication required)
- **HTTPS Server (port 8443)**: Authenticated API calls (STF files, workflows, runs)

### Environment Configuration

Required environment variables in `~/.env`:

```bash
# Monitor URLs for different purposes
export SWF_MONITOR_URL=https://localhost:8443      # Authenticated API calls
export SWF_MONITOR_HTTP_URL=http://localhost:8002  # REST logging (no auth)

# Authentication token for API calls
export SWF_API_TOKEN=your_token_here
```

## Web Interface Access

- **Dashboard**: http://localhost:8002/ (main monitoring interface)
- **STF Files**: http://localhost:8002/stf-files/ (file tracking)
- **Workflows**: http://localhost:8002/workflows/ (processing status)
- **Admin Interface**: http://localhost:8002/admin/ (Django admin)

## API Endpoints

### Authenticated APIs (HTTPS - port 8443)

Require `Authorization: Token <token>` header:

- `POST /api/runs/` - Create run records
- `POST /api/stf-files/` - Register STF files
- `POST /api/workflows/` - Create workflow records
- `POST /api/workflow-stages/` - Track processing stages

### REST Logging (HTTP - port 8002)

No authentication required:
- `POST /api/logs/` - Agent logging endpoint

## Getting API Token

From the monitor server:
```bash
cd ../swf-monitor/src
python manage.py get_token <username>
```

## SSL Certificate Setup

The startup script automatically creates self-signed certificates for development:
- `ssl_cert.pem` - SSL certificate
- `ssl_key.pem` - Private key

For production, replace with proper certificates.

## Troubleshooting

### Common Issues

1. **"Connection refused"** - Monitor not started
   ```bash
   ../swf-monitor/start_django_dual.sh
   ```

2. **"HTTPS timeout"** - Wrong port or SSL issues
   - Check HTTPS server is running on port 8443
   - Verify SSL certificates exist

3. **"401 Unauthorized"** - Missing or invalid API token
   - Set `SWF_API_TOKEN` environment variable
   - Get new token with `manage.py get_token`

4. **"Empty STF files page"** - Agents not calling API
   - Verify monitor is serving HTTPS on 8443
   - Check agent logs for API call failures
   - Ensure `SWF_MONITOR_URL` points to HTTPS endpoint

### Port Configuration Issues

**Problem**: STF files not appearing despite agents running
**Cause**: Port/protocol mismatch between agent configuration and monitor
**Solution**: Ensure environment variables match actual server configuration:
- `SWF_MONITOR_URL` → HTTPS port (8443) for API calls
- `SWF_MONITOR_HTTP_URL` → HTTP port (8002) for logging

## Integration with Agents

Agents automatically use the correct endpoints:
- **REST logging**: Uses `SWF_MONITOR_HTTP_URL` (HTTP, no auth)
- **API calls**: Uses `SWF_MONITOR_URL` (HTTPS, token auth)
- **Proxy bypass**: Automatic for localhost connections

See [Agent System](agents.md) for more details on agent configuration.