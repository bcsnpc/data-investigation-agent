FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DIA_LIVE_ACCESS_DISABLED=1
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl git unixodbc libgssapi-krb5-2 \
    && curl --fail --silent --show-error --location https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -o /tmp/microsoft.deb \
    && dpkg -i /tmp/microsoft.deb \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/* /tmp/microsoft.deb
WORKDIR /app
COPY scripts/requirements-*.txt /app/scripts/
RUN pip install --no-cache-dir -r scripts/requirements-lineage.txt -r scripts/requirements-llm.txt \
    -r scripts/requirements-replay.txt -r scripts/requirements-cloud-worker.txt
COPY scripts/ /app/scripts/
COPY acceptance/ /app/acceptance/
COPY infra/scripts/ /app/infra/scripts/
COPY image-source-manifest.json /app/image-source-manifest.json
RUN groupadd --gid 10001 dia && useradd --uid 10001 --gid dia --no-create-home dia \
    && mkdir /results && chown dia:dia /results
USER 10001:10001
ENTRYPOINT ["python", "/app/scripts/cloud_offline_worker.py"]
