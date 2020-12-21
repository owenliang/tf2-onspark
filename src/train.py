import argparse
from pyspark.context import SparkContext
from pyspark.conf import SparkConf
from tensorflowonspark import TFCluster

def main_fun(args, ctx):
    pass

conf = SparkConf().setAppName("tf2-onspark-training")
sc = SparkContext(conf=conf)

parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", help="number of records per batch", type=int, default=64)
parser.add_argument("--buffer_size", help="size of shuffle buffer", type=int, default=10000)
parser.add_argument("--cluster_size", help="number of nodes in the cluster", type=int)
parser.add_argument("--epochs", help="number of epochs", type=int, default=3)
parser.add_argument("--images_labels", help="HDFS path to MNIST image_label files in parallelized format")
parser.add_argument("--model_dir", help="path to save model/checkpoint", default="mnist_model")
parser.add_argument("--export_dir", help="path to export saved_model", default="mnist_export")
parser.add_argument("--tensorboard", help="launch tensorboard process", action="store_true")

args = parser.parse_args()
print("args:", args)

cluster = TFCluster.run(sc, main_fun, args, args.cluster_size, num_ps=0, tensorboard=args.tensorboard, input_mode=TFCluster.InputMode.TENSORFLOW, master_node='chief')
cluster.shutdown()