FROM tensorflow/serving

COPY ./models/rcnn/ /models/rcnn
COPY ./models/saved_model_half_plus_two_cpu /models/half_plus_two
COPY ./models/resnet /models/resnet

COPY ./config.conf /config/config.conf
