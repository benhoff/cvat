import rq

import grpc

import tensorflow as tf
from tensorflow_serving.apis import prediction_service_pb2_grpc
from tensorflow_serving.apis import predict_pb2

from cvat.apps.engine.log import slogger
from cvat.apps.engine.models import Task as TaskModel
from cvat.apps.engine.serializers import LabeledDataSerializer

from cvat.apps.auto_annotation.image_loader import ImageLoader
from cvat.apps.auto_annotation.model_manager import get_image_data as _get_image_loader
from cvat.apps.auto_annotation.model_loader import load_labelmap
from cvat.apps.auto_annotation.inference import Results

from cvat.apps.engine.annotation import put_task_data, patch_task_data

from .models import TFAnnotationModel as _TFModel

def do_inference_and_update_rq_worker(task_id: int, model_id: int):
    try:
        job = rq.get_current_job()
        job.meta['progress'] = 0
        job.save_meta()

        db_task = TaskModel.objects.get(pk=task_id)
        model = _TFModel.objects.get(pk=model_id)
        result = None
        # FIXME: Fix log
        slogger.glob.info("auto annotation with openvino toolkit for task {}".format(task_id))

        image_loader: ImageLoader = _get_image_loader(db_task.get_data_dirname())

        result = do_inference(image_loader, model.model_name, model.signature_name)

        if result is None:
            slogger.glob.info("auto annotation for task {} canceled by user".format(task_id))
            return

        serializer = LabeledDataSerializer(data = result)
        if serializer.is_valid(raise_exception=True):
            if reset:
                put_task_data(task_id, user, result)
            else:
                patch_task_data(task_id, user, result, "create")

        slogger.glob.info("auto annotation for task {} done".format(task_id))
    except Exception as e:
        try:
            slogger.task[task_id].exception("exception was occurred during auto annotation of the task", exc_info=True)
        except Exception as ex:
            slogger.glob.exception("exception was occurred during auto annotation of the task {}: {}".format(task_id, str(ex)), exc_info=True)
            raise ex

        raise e

# Note:     request.model_spec.signature_name = 'predict_images'
# https://github.com/tensorflow/serving/blob/master/tensorflow_serving/example/mnist_client.py
def do_inference(image_loader: ImageLoader, model_name: str, signature_name: str):
    channel = grpc.insecure_channel(hostport)
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    for frame in image_loader:
        # orig_rows, orig_cols = frame.shape[:2]
        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name
        tensor = tf.contrib.util.make_tensor_proto(frame, shape=[1]+list(frame.shape))
        request.inputs['input'].CopyFrom(tensor)
        response = stub.predict(request, 30.0)
