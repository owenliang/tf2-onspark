#!/bin/bash

cd src && zip -r src.zip * && mv src.zip .. && cd -
cd data && zip -r data.zip * && mv data.zip .. && cd -

TRAIN_NUM_PARTITIONS=5
TEST_NUM_PARTITIONS=5
TRAIN_OUTPUT=/tf2-onspark/train
TEST_OUTPUT=/tf2-onspark/test

# 删除旧输出
hdfs dfs -rm -r ${TRAIN_OUTPUT}
hdfs dfs -rm -r ${TEST_OUTPUT}

# --master yarn ：运行到yarn集群，固定写法
# --deploy-mode cluster：AM运行到yarn中，如果改成client则需要确保本地目录有./Python/bin/python3
# --num-executors 1：一个executor容器
# --archives hdfs:///Python.zip#Python：从hdfs集群下载/Python.zip到executor工作目录，并解压到Python目录
# --py-files ./src.zip：项目python源代码，会解压到executor的某目录下并令PYTHONPATH指向该目录
# --conf spark.pyspark.python=./Python/bin/python3：指定使用自行上传的Python
spark-submit \
  --master yarn \
  --deploy-mode client \
  --num-executors 1 \
  --executor-memory 1G \
  --archives hdfs:///tf2-onspark/Python.zip#Python,data.zip#data \
  --py-files ./src.zip \
  --conf spark.pyspark.python=./Python/bin/python3 \
  --jars hdfs:///tf2-onspark/tensorflow-hadoop-1.10.0.jar \
  src/gen_tfrecords.py \
  --train_csv ./data/train.csv  \
  --test_csv ./data/test.csv \
  --train_num_partitions ${TRAIN_NUM_PARTITIONS} \
  --test_num_partitions ${TEST_NUM_PARTITIONS} \
  --train_output ${TRAIN_OUTPUT} \
  --test_output ${TEST_OUTPUT}