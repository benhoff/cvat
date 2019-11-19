# Runner script

docker run -p 8500:8500 -p 8501:8501 --mount type=bind,source=/Users/hoff/swdev/nci-cvat/utils/tf_serving/models/ssdlite_mobilenet_v2_coco/,target=/models/ssdlite_mobilenet_v2_coco -e MODEL_NAME=ssdlite_mobilenet_v2_coco -t tensorflow/serving
