from pyspark.sql import SparkSession
from dataset import dataframe_to_tfrecords
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--train_csv', help='train csv文件名')
parser.add_argument('--test_csv', help='test csv文件名')
parser.add_argument('--train_num_partitions', help='train tfrecords文件分片个数', type=int)
parser.add_argument('--test_num_partitions', help='test tfrecords文件分片个数', type=int)
parser.add_argument('--train_output', help='保存train tfrecords的目录')
parser.add_argument('--test_output', help='保存test tfrecords的目录')
args = parser.parse_args()

sess = SparkSession.builder.appName('gen_tfrecords').enableHiveSupport().getOrCreate()

dataframe_to_tfrecords(sess, pd.read_csv(args.train_csv), args.train_num_partitions, args.train_output, include_outputs=True)
dataframe_to_tfrecords(sess, pd.read_csv(args.test_csv), args.test_num_partitions, args.test_output, include_outputs=False)