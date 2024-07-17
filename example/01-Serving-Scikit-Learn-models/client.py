import requests


# Original source code and more details can be found in:
# https://scikit-learn.org/stable/auto_examples/classification/plot_digits_classification.html

# Import datasets, classifiers and performance metrics
from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split

# The digits dataset
digits = datasets.load_digits()

# To apply a classifier on this data, we need to flatten the image, to
# turn the data in a (samples, feature) matrix:
n_samples = len(digits.images)
data = digits.images.reshape((n_samples, -1))

# Create a classifier: a support vector classifier
classifier = svm.SVC(gamma=0.001)

# Split data into train and test subsets
X_train, X_test, y_train, y_test = train_test_split(
    data, digits.target, test_size=0.5, shuffle=False)

# We learn the digits on the first half of the digits
# classifier.fit(X_train, y_train)

print("X_test:", X_test)
# X_test: [[ 0.  0.  1. ... 12.  1.  0.]
#  [ 0.  0.  6. ...  6.  0.  0.]
#  [ 0.  0.  0. ...  2.  0.  0.]
#  ...
#  [ 0.  0.  1. ...  6.  0.  0.]
#  [ 0.  0.  2. ... 12.  0.  0.]
#  [ 0.  0. 10. ... 12.  1.  0.]]

x_0 = X_test[0:1]
print("x_0:", x_0)
# x_0: [[ 0.  0.  1. 11. 14. 15.  3.  0.  0.  1. 13. 16. 12. 16.  8.  0.  0.  8.
#   16.  4.  6. 16.  5.  0.  0.  5. 15. 11. 13. 14.  0.  0.  0.  0.  2. 12.
#   16. 13.  0.  0.  0.  0.  0. 13. 16. 16.  6.  0.  0.  0.  0. 16. 16. 16.
#    7.  0.  0.  0.  0. 11. 13. 12.  1.  0.]]

inference_request = {
    "inputs": [
        {
          "name": "predict",
          "shape": x_0.shape,
          "datatype": "FP32",
          "data": x_0.tolist()
        }
    ]
}
print("inference_request:", inference_request)
# inference_request:
# {
#     'inputs': [
#         {
#             'name': 'predict',
#             'shape': (1, 64),
#             'datatype': 'FP32',
#             'data': [
#                 [0.0, 0.0, 1.0, 11.0, 14.0, 15.0, 3.0, 0.0, 0.0, 1.0, 13.0, 16.0, 12.0, 16.0, 8.0, 0.0, 0.0, 8.0, 16.0, 4.0, 6.0, 16.0, 5.0, 0.0, 0.0, 5.0, 15.0, 11.0, 13.0, 14.0, 0.0, 0.0, 0.0, 0.0, 2.0, 12.0, 16.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 16.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 16.0, 16.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 11.0, 13.0, 12.0, 1.0, 0.0]
#             ]
#         }
#     ]
# }

endpoint = "http://localhost:8080/v2/models/mnist-svm/versions/v0.1.0/infer"
response = requests.post(endpoint, json=inference_request)

print(response.json())
# {
#     'model_name': 'mnist-svm',
#     'model_version': 'v0.1.0',
#     'id': '516e7dc1-b1c0-48e5-9a3e-d391e7657c68',
#     'parameters': {},
#     'outputs': [
#         {
#             'name': 'predict',
#             'shape': [1, 1],
#             'datatype': 'INT64',
#             'parameters': {
#                 'content_type': 'np'
#             },
#             'data': [8]
#         }
#     ]
# }
