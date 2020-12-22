import argparse
from pyspark.context import SparkContext
from pyspark.conf import SparkConf
from tensorflowonspark import TFCluster, compat
import tensorflow as tf
from model import build_model
from dataset import dataset_from_tfrecords
import time

MODEL_VERSION = 0

def main_fun(args, ctx):
    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()

    with strategy.scope():
        wide_deep_model = build_model()

    dataset = dataset_from_tfrecords(args.train_dir + '/part*', include_outputs=True)
    dataset = dataset.batch(args.batch_size * args.worker_size).shuffle(args.shuffle_size)

    tensorboard_dir = args.tensorboard_dir if ctx.job_name == 'chief' else './tensorboard'
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir='{}/{}'.format(tensorboard_dir, MODEL_VERSION), histogram_freq=1)
    wide_deep_model.fit(dataset, epochs=args.epochs, callbacks=[tensorboard_callback])

    model_dir = args.model_dir if ctx.job_name == 'chief' else './model'
    wide_deep_model.save('{}/{}'.format(model_dir, MODEL_VERSION), save_format='tf', include_optimizer=False)

parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", help="number of records per batch", type=int)
parser.add_argument("--shuffle_size", help="size of shuffle buffer", type=int)
parser.add_argument("--worker_size", help="number of nodes in the cluster", type=int)
parser.add_argument("--epochs", help="number of epochs", type=int)
parser.add_argument("--train_dir", help="HDFS path to training tfrecords files in parallelized format")
parser.add_argument("--model_dir", help="hdfs path to save model")
parser.add_argument("--tensorboard_dir", help="hdfs path to tensorboard logs")

args = parser.parse_args()
print("args:", args)

MODEL_VERSION = int(time.time())

conf = SparkConf().setAppName("tf2-onspark-training")
sc = SparkContext(conf=conf)
cluster = TFCluster.run(sc, main_fun, args, args.worker_size, num_ps=0, tensorboard=False, input_mode=TFCluster.InputMode.TENSORFLOW, master_node='chief')
cluster.shutdown()

print('model version={}'.format(MODEL_VERSION))