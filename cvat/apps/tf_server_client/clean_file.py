import grpc

import tensorflow as tf
from tensorflow_serving.apis import prediction_service_pb2_grpc
from tensorflow_serving.apis import predict_pb2


def do_inference(image_loader: 'ImageLoader', model_name: str, signature_name: str, hostport: str, wait_time: float):
    print(model_name, signature_name, hostport)
    channel = grpc.insecure_channel('localhost' + hostport)
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    for frame in image_loader:
        # orig_rows, orig_cols = frame.shape[:2]
        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name
        # tensor = tf.contrib.util.make_tensor_proto(frame, shape=[1]+list(frame.shape))
        tensor = tf.contrib.util.make_tensor_proto(frame, shape=[1])
        # NOTE that the resnet example sets this as 'rcnn'
        request.inputs['inputs'].CopyFrom(tensor)
        response = stub.Predict(request, wait_time)
