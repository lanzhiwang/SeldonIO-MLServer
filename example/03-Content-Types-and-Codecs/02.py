from PIL import Image
from mlserver_huggingface.codecs import PILImageCodec

im1 = Image.open('01.jpg')

request_input = PILImageCodec.encode_input(name="image1", payload=[im1])
print("request_input:", request_input)
# request_input:
# 	name='image1'
# 	shape=[1, 1]
# 	datatype='BYTES'
# 	parameters=Parameters(
# 		content_type='pillow_image',
# 		headers=None
# 	)
# 	data=TensorData(
# 		__root__=[b'iVBORw0KGgoAAAANSUgfPJRyplzSmEjMGHsjy2EEnkh9/5+ZjtgMlC4MOZCQpdzUDDrbD/UBE5IQmCC']
# 	)
