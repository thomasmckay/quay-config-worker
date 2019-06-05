* Quay Config Worker

Quay worker service to allow database config via ansible playbooks.

Config

Config information is loaded in the following order: First '/quay-config-worker/conf/config.yaml' is imported. Next, the environment variable 'OVERRIDE_CONFIG_YAML' is processed, overriding or adding to existing config. Finally, 'OVERRIDE_CONFIG_JSON' is processed as well.

An example of the minimum needed to allow the worker to run is below. Warning: Do not use this minimum when running worker against an existing server with populated database.
```
cat <<EOF > args.json
{
  "SERVER_HOSTNAME": "devel.example.com",
  "DB_URI": "postgresql://quay:quay@devel.example.com:5432/quay",
  "DB_CONNECTION_ARGS": {
    "threadlocals": "true",
    "autorollback": "true"
  }
}
EOF

docker run -it -e "OVERRIDE_CONFIG_JSON=$(<args.json)" -p 8788:8788 -p 8688:8688 quay-config-worker:latest

```

** Development

Setup and run the worker service.
```
cd worker
pip install virtualenv
virtualenv .venv
source .venv/bin/activate
pip install --upgrade pip
```

```
cd worker
pip install -r requirements.txt
make build
```

To confirm that the proper source files are part of the final build, set $QUAYDIR to be the local build dir (created by 'make build' above). Alternatively, point $QUAYDIR to a full checkout of https://github.com/quay/quay.
```
cd worker
export QUAYDIR=../build
export PYTHONPATH=.:$QUAYDIR
export QUAYCONF=<path to /stack>  # Path to location of stack/config.yaml
python ansible_worker.py
```

