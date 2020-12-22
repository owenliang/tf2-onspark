#!/bin/bash

cd src && zip -r src.zip * && mv src.zip .. && cd -

LIB_JVM=/usr/local/jdk/jre/lib/amd64/server/

# --master yarn ：运行到yarn集群，固定写法
# --deploy-mode cluster：AM运行到yarn中，如果改成client则需要确保本地目录有./Python/bin/python3
# --num-executors 1：一个executor容器
# --archives hdfs:///Python.zip#Python：从hdfs集群下载/Python.zip到executor工作目录，并解压到Python目录
# --py-files ./src.zip：项目python源代码，会解压到executor的某目录下并令PYTHONPATH指向该目录
# --conf spark.pyspark.python=./Python/bin/python3：指定使用自行上传的Python
#  --conf spark.executorEnv.LD_LIBRARY_PATH=${LIB_JVM}：依赖libjvm.so
#  --conf spark.dynamicAllocation.enabled=false  禁止spark自动扩容executor数量
#  --conf spark.yarn.maxAppAttempts=1 失败重试1次
spark-submit \
  --master yarn \
  --deploy-mode client \
  --num-executors 5 \
  --executor-cores 2 \
  --executor-memory 8G \
  --archives hdfs:///tf2-onspark/Python.zip#Python \
  --py-files ./src.zip \
  --conf spark.pyspark.python=./Python/bin/python3 \
  --conf spark.executorEnv.LD_LIBRARY_PATH=${LIB_JVM} \
  --conf spark.dynamicAllocation.enabled=false \
  --conf spark.yarn.maxAppAttempts=1 \
  src/train.py \
  --batch_size 32 \
  --shuffle_size 32 \
  --worker_size 5 \
  --epochs 1000 \
  --train_dir hdfs:///tf2-onspark/train \
  --model_dir hdfs:///tf2-onspark/model \
  --tensorboard_dir hdfs:///tf2-onspark/tensorboard