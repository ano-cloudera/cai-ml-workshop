"""
Script 9: Call the KServe V2 inference endpoint for the credit_risk_model
Registered Model / Model Endpoint.

Unlike cml_model.py's accessKey-based predict endpoint, a Model Endpoint
created from the AI Registry speaks the KServe V2 (Open Inference) protocol:
requests carry a named tensor with an explicit shape/datatype. Rather than
guess the tensor name Triton assigned to the (-1, 8) TensorSpec declared in
08_register_in_ai_registry.py, this script reads it from the endpoint's own
metadata first, then builds the inference request from that.

Requires:
    pip install open-inference-openapi

BASE_URL / MODEL_NAME are read from env vars — copy them from the
endpoint's own page (Model Endpoints -> credit-risk-model -> Endpoint
Base URL / Model ID). They are workspace- and deployment-specific, so
they are not hardcoded here.

Run from a CML session terminal (reads the session's JWT from /tmp/jwt):
    export REGISTRY_ENDPOINT_URL=https://<workspace>/namespaces/serving-default/endpoints/<endpoint-name>
    export REGISTRY_MODEL_NAME=<model-id-from-endpoint-page>
    python 09_test_registry_endpoint.py
"""

import json
import os

import httpx
from open_inference.openapi.client import InferenceRequest, OpenInferenceClient

BASE_URL = os.environ.get("REGISTRY_ENDPOINT_URL")
MODEL_NAME = os.environ.get("REGISTRY_MODEL_NAME")
if not BASE_URL or not MODEL_NAME:
    raise SystemExit(
        "ERROR: REGISTRY_ENDPOINT_URL and/or REGISTRY_MODEL_NAME not set. "
        "Copy both from the endpoint's own page (Model Endpoints -> "
        "credit-risk-model -> Endpoint Base URL / Model ID), e.g.:\n"
        "  export REGISTRY_ENDPOINT_URL=https://<workspace>/namespaces/serving-default/endpoints/<endpoint-name>\n"
        "  export REGISTRY_MODEL_NAME=<model-id>"
    )

# loan_purpose pre-encoded per the mapping 08_register_in_ai_registry.py
# prints after registering (e.g. home -> 3). Update if your run differs.
FEATURES = [10000, 90000, 780, 10, 0.15, 5, 0, 3]

api_key = json.load(open("/tmp/jwt"))["access_token"]
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
httpx_client = httpx.Client(headers=headers)
client = OpenInferenceClient(base_url=BASE_URL, httpx_client=httpx_client)

client.check_server_readiness()

metadata = json.loads(client.read_model_metadata(MODEL_NAME).json())
print("Model metadata:")
print(json.dumps(metadata, indent=2))

input_spec = metadata["inputs"][0]
print(
    f"\nDetected input tensor: name={input_spec['name']!r} "
    f"shape={input_spec['shape']} datatype={input_spec['datatype']}"
)

pred = client.model_infer(
    MODEL_NAME,
    request=InferenceRequest(
        inputs=[
            {
                "name": input_spec["name"],
                "shape": [1, len(FEATURES)],
                "datatype": input_spec["datatype"],
                "data": FEATURES,
            }
        ]
    ),
)

print("\nInference response:")
print(json.dumps(json.loads(pred.json()), indent=2))
