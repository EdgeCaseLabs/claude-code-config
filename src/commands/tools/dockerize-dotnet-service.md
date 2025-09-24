---
description: "Dockerize a .NET service using established patterns from previous work"
argument-hint: "[service_path] | (no args to guide through the process)"
---

# Dockerize .NET Service

Help me dockerize a .NET service using the patterns we've established. Based on our previous work with FlightManagerService, SimAlarmAdapter, and ATC Turbulance, perform these steps:

## 1. Configuration Setup
- Create `appsettings.docker.json` with empty strings for Docker environment variable overrides
- Include common sections like ConnectionStrings, App, MessageBroker, MonOrch, Seq
- Use empty values that will be populated by environment variables

## 2. Program.cs Updates  
- Modify to use `AcmsCommon.Utility.ConfigLoader.GetConfiguration(args)`
- Replace `WebApplication.CreateBuilder(args)` with `WebApplication.CreateBuilder()` to avoid loading default appsettings
- Clear configuration sources and add only ConfigLoader configuration
- Add explicit Kestrel HTTP-only configuration to prevent HTTPS certificate errors:
  ```csharp
  builder.Services.Configure<KestrelServerOptions>(options => {
      options.Listen(System.Net.IPAddress.Any, PORT);
  });
  builder.WebHost.UseUrls("http://*:PORT");
  ```

## 3. Project File Updates
- Add appsettings.docker.json to .csproj with `CopyToOutputDirectory=PreserveNewest`

## 4. Dockerfile Creation
- Use `airstriptech.azurecr.io/airstrip/base-dotnet-8.0:v1.0.0` as base image
- Handle spaces in service paths using array syntax: `COPY ["path with spaces", "/app/destination"]`
- Include Azure DevOps token mounting for NuGet feeds
- Set appropriate ASPNETCORE_URLS for HTTP-only

## 5. CADT Template Integration
- Add service to CADT compose template with proper environment variables:
  - `ASPNETCORE_URLS: "http://*:PORT"`
  - `ASPNETCORE_FORWARDEDHEADERS_ENABLED: "true"`
  - `ConnectionStrings__AcmsDatabase: "{{ DOCKER_AAM_CONNECTION_STRING }}"`
  - `ConnectionStrings__nats: "{{ DOCKER_NATS_CONNECTION_STRING }}"`
  - `App__MessageBrokerUrl: "{{ DOCKER_NATS_CONNECTION_STRING }}"`
  - `MessageBroker__BrokerUri: "{{ DOCKER_NATS_CONNECTION_STRING }}"`
  - `MonOrch__BrokerUri: "{{ DOCKER_NATS_CONNECTION_STRING }}"`
  - `MonOrch__NatsMonitoringAddress: "http://nats:8222"`

## Key Patterns to Follow:
- **HTTP-only by default** to avoid certificate issues in containers
- **Empty config values** in appsettings.docker.json for environment override
- **ConfigLoader pattern** for consistent configuration loading
- **Array syntax** in Dockerfiles for paths with spaces
- **Template variables** in CADT for environment-specific values

If no service path is provided, ask me which service I want to dockerize and guide me through the process step by step.