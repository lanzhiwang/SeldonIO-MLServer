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
# inference_request:
# {
#     'inputs': [
#         {
#             'name': 'args',
#             'shape': [1],
#             'datatype': 'BYTES',
#             'data': ['this is a test']
#         }
#     ]
# }


response = requests.post(
    "http://localhost:8080/v2/models/transformer/infer", json=inference_request
).json()

print(response)
# {
#     'model_name': 'transformer',
#     'id': '4ad7ec9a-4f8b-43dc-9eae-9aca81377840',
#     'parameters': {},
#     'outputs': [
#         {
#             'name': 'output',
#             'shape': [1, 1],
#             'datatype': 'BYTES',
#             'parameters': {'content_type': 'hg_jsonlist'},
#             'data': [
#                 '{
#                     "generated_text": "this is a test of the function I put in the \\"Test.\\" If I wasn\'t there then the function for that function would have been called; if you got the test I would have called it; if I didn\'t call the function in the"
#                 }'
#             ]
#         }
#     ]
# }
