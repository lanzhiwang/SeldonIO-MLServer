import pandas as pd

from mlserver.codecs import PandasCodec

dataframe = pd.DataFrame({'First Name': ["Joanne", "Michael"], 'Age': [34, 22]})

inference_request = PandasCodec.encode_request(dataframe)
print("inference_request:", inference_request)

raw_request = inference_request.dict()
print("raw_request:", raw_request)

# response = requests.post("localhost:8080/v2/models/foo/infer", json=raw_request)

# raw_response will be a dictionary (loaded from the response's JSON),
# therefore we can pass it as the InferenceResponse constructors' kwargs
# raw_response = response.json()
# inference_response = InferenceResponse(**raw_response)

# inference_request:
# 	id=None
# 	parameters=Parameters(
# 		content_type='pd',
# 		headers=None
# 	)
# 	inputs=[
# 		RequestInput(
# 			name='First Name',
# 			shape=[2, 1],
# 			datatype='BYTES',
# 			parameters=Parameters(
# 				content_type='str',
# 				headers=None
# 			),
# 			data=TensorData(
# 				__root__=[b'Joanne', b'Michael']
# 			)
# 		),
# 		RequestInput(
# 			name='Age',
# 			shape=[2, 1],
# 			datatype='INT64',
# 			parameters=None,
# 			data=TensorData(
# 				__root__=[34, 22]
# 			)
# 		)
# 	]
# 	outputs=None

# raw_request:
# {
# 	'parameters': {'content_type': 'pd'},
# 	'inputs': [
# 		{
# 			'name': 'First Name',
# 			'shape': [2, 1],
# 			'datatype': 'BYTES',
# 			'parameters': {'content_type': 'str'},
# 			'data': [b'Joanne', b'Michael']
# 		},
# 		{
# 			'name': 'Age',
# 			'shape': [2, 1],
# 			'datatype': 'INT64',
# 			'data': [34, 22]
# 		}
# 	]
# }


