# Runner script

```
docker run -p 8500:8500 -p 8501:8501 --mount type=bind,source=/home/hoff/swdev/cvat/utils/tf_serving/models/rcnn,target=/models/rcnn -e MODEL_NAME=rcnn -t tensorflow/serving
```
