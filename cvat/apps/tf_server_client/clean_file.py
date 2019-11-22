import grpc

import tensorflow as tf
from tensorflow_serving.apis import prediction_service_pb2_grpc
from tensorflow_serving.apis import predict_pb2


def do_inference(image_loader: 'ImageLoader', model_name: str, signature_name: str, restricted=False):
    channel = grpc.insecure_channel(hostport)
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    for frame in image_loader:
        # orig_rows, orig_cols = frame.shape[:2]
        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name
        tensor = tf.contrib.util.make_tensor_proto(frame, shape=[1]+list(frame.shape))
        request.inputs['input'].CopyFrom(tensor)
        response = stub.predict(request, 30.0)
