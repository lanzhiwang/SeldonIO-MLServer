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
print("inference_request:", inference_request)

response = requests.post(
    "http://localhost:8080/v2/models/transformer/infer", json=inference_request
).json()

print(response)
