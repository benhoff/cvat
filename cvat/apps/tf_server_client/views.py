import json

from django.http import HttpRequest

import django_rq

from cvat.apps.authentication.decorators import login_required
from cvat.apps.engine.log import slogger

from .models import TFAnnotationModel

@permission_required(perm=["engine.task.change"],
    fn=objectgetter(TaskModel, "tid"), raise_exception=True)
# FIXME: need to do something about this
# @permission_required(perm=["auto_annotation.model.access"],
#     fn=objectgetter(AnnotationModel, "mid"), raise_exception=True)
def start_annotation(request: 'django.http.HttpRequest', model_id, task_id):
    slogger.glob.info("TF auto annotation create request for task {} via DL model {}".format(task_id, model_id))
    try:
        queue = django_rq.get_queue("low")
        job = queue.fetch_job("auto_annotation.run.{}".format(tid))

        if job is not None and (job.is_started or job.is_queued):
            raise Exception("The process is already running")

        db_task = TaskModel.objects.get(pk=tid)
        data = json.loads(request.body.decode('utf-8'))

        should_reset = data['reset']
        user_defined_label_mapping = data['labels']

        tf_model = TFAnnotationModel.objects.get(pk=model_id)

        model_name = dl_model.model_name
        labelmap_file = dl_model.labelmap_file.name
        convertation_file_path = dl_model.interpretation_file.name

        # NOTE: This could be pulled into a method for auto_annotation super model
        # https://github.com/opencv/cvat/blob/1487ceafb9d872a2afd3ad1b50a0c783efdb2808/cvat/apps/auto_annotation/views.py#L193
        db_labels = db_task.label_set.prefetch_related("attributespec_set").all()
        db_attributes = {db_label.id:
            {db_attr.name: db_attr.id for db_attr in db_label.attributespec_set.all()} for db_label in db_labels}
        db_labels = {db_label.name:db_label.id for db_label in db_labels}

        model_labels = {value: key for key, value in load_labelmap(labelmap_file).items()}

        labels_mapping = {}
        for user_model_label, user_db_label in user_defined_labels_mapping.items():
            if user_model_label in model_labels and user_db_label in db_labels:
                labels_mapping[int(model_labels[user_model_label])] = db_labels[user_db_label]

        if not labels_mapping:
            raise Exception("No labels found for annotation")

        # Ref: https://github.com/tensorflow/serving/blob/2e87e9413dcd5a2743d9af95875ffa330d366b89/tensorflow_serving/example/mnist_client.py#L124
        rq_id="auto_annotation.run.{}".format(tid)
        # FIXME: Method doesn't exist
        queue.enqueue_call(func=model_manager.run_inference_thread,
            args=(
                task_id,
                model_name,
                labels_mapping,
                db_attributes,
                convertation_file_path,
                should_reset,
                request.user,
                restricted,
            ),
            job_id = rq_id,
            timeout=604800)     # 7 days

    except Exception as ex:
        try:
            slogger.task[tid].exception("exception was occurred during annotation request", exc_info=True)
        except Exception as logger_ex:
            slogger.glob.exception("exception was occurred during create auto annotation request for task {}: {}".format(tid, str(logger_ex)), exc_info=True)
        return HttpResponseBadRequest(str(ex))

    # FIXME
    return None
def delete_model(request, model_id):
    pass


def cancel(request: 'django.http.HttpRequest', tid):
    pass
