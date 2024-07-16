# codespaces

```bash
@lanzhiwang ➜ /workspaces/SeldonIO-MLServer (learn-1.5.0) $ pwd
/workspaces/SeldonIO-MLServer

@lanzhiwang ➜ /workspaces/SeldonIO-MLServer (learn-1.5.0) $ python -m venv .env

@lanzhiwang ➜ /workspaces/SeldonIO-MLServer (learn-1.5.0) $ source .env/bin/activate

(.env) @lanzhiwang ➜ /workspaces/SeldonIO-MLServer (learn-1.5.0) $ pwd
/workspaces/SeldonIO-MLServer

(.env) @lanzhiwang ➜ /workspaces/SeldonIO-MLServer (learn-1.5.0) $

(.env) @lanzhiwang ➜ /workspaces/SeldonIO-MLServer (learn-1.5.0) $ pip install -e .

(.env) @lanzhiwang ➜ /workspaces/SeldonIO-MLServer (learn-1.5.0) $ pip install -e ./runtimes/sklearn/

(.env) @lanzhiwang ➜ /workspaces/SeldonIO-MLServer (learn-1.5.0) $ mlserver start ./example/01-Serving-Scikit-Learn-models/

(.env) @lanzhiwang ➜ /workspaces/SeldonIO-MLServer (learn-1.5.0) $ pip install requests==2.32.3

(.env) @lanzhiwang ➜ /workspaces/SeldonIO-MLServer (learn-1.5.0) $ python ./example/01-Serving-Scikit-Learn-models/client.py


```