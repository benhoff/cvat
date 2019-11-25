# Runner script

```
docker run -p 8500:8500 -p 8501:8501 --mount type=bind,source=/home/hoff/swdev/cvat/utils/tf_serving/models/rcnn,target=/models/rcnn -e MODEL_NAME=rcnn -t tensorflow/serving
```

https://stackoverflow.com/questions/53035896/serving-multiple-tensorflow-models-using-docker?noredirect=1#comment92983141_53035896
https://stackoverflow.com/questions/45749024/how-can-i-use-tensorflow-serving-for-multiple-models
