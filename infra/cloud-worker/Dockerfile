FROM mcr.microsoft.com/dotnet/sdk:8.0-bookworm-slim AS xmla-build
WORKDIR /src
COPY infra/xmla-reader/ /src/
RUN dotnet publish Dia.XmlaReader.csproj -c Release -o /publish --self-contained false

FROM mcr.microsoft.com/dotnet/runtime:8.0-bookworm-slim AS xmla-runtime

FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DIA_LIVE_ACCESS_DISABLED=1
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl git unixodbc libgssapi-krb5-2 libicu72 \
    && curl --fail --silent --show-error --location https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -o /tmp/microsoft.deb \
    && dpkg -i /tmp/microsoft.deb \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/* /tmp/microsoft.deb
WORKDIR /app
COPY --from=xmla-runtime /usr/share/dotnet /usr/share/dotnet
RUN ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet
COPY --from=xmla-build /publish/ /opt/dia/xmla-reader/
RUN dotnet /opt/dia/xmla-reader/Dia.XmlaReader.dll --self-test
COPY scripts/requirements-*.txt /app/scripts/
RUN pip install --no-cache-dir -r scripts/requirements-lineage.txt -r scripts/requirements-llm.txt \
    -r scripts/requirements-replay.txt -r scripts/requirements-cloud-worker.txt
COPY scripts/ /app/scripts/
COPY acceptance/ /app/acceptance/
COPY infra/scripts/ /app/infra/scripts/
COPY apps/investigator-workspace/ /app/apps/investigator-workspace/
COPY image-source-manifest.json /app/image-source-manifest.json
RUN groupadd --gid 10001 dia && useradd --uid 10001 --gid dia --no-create-home dia \
    && mkdir /results /work /inputs /app/.local && chown dia:dia /results /work /inputs /app/.local
USER 10001:10001
ENTRYPOINT ["python", "/app/scripts/cloud_offline_worker.py"]
