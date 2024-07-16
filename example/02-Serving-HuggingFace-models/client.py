import requests

inference_request = {
    "inputs": [
        {
            "name": "args",
            "shape": [1],
            "datatype": "BYTES",
            "data": ["this is a test"],
        }
    ]
}

response = requests.post(
    "https://expert-goldfish-7jw97qw597cwxp-8080.app.github.dev/v2/models/transformer/infer", json=inference_request
).json()

print(response)
# {'model_name': 'transformer', 'id': 'c779a7ef-c419-401a-9b4d-a986b3d6556a', 'parameters': {}, 'outputs': [{'name': 'output', 'shape': [1, 1], 'datatype': 'BYTES', 'parameters': {'content_type': 'hg_jsonlist'}, 'data': ['{"generated_text": "this is a test of the concept you should be able to see in your browser is some very useful technique.\\n\\nMy demo also features some very easy examples of how to code. The idea is that we create the first test in Javascript, we"}']}]}
