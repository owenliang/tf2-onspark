import pandas as pd
import tensorflow as tf
from config import model_spec
from copy import deepcopy

def dataframe_to_tfrecords(sess, df, num_partitions, output_dir, include_outputs=False):
    all_feature_spec = deepcopy(model_spec['inputs'])
    if include_outputs:
        all_feature_spec.update(model_spec['outputs'])

    rows = []
    for _, row in df.iterrows():
        rows.append(row)

    def to_example(row):
        feature_dict = {}
        for feature_name, feature_spec in all_feature_spec.items():
            feature_value = row[feature_name]
            if feature_value is None or pd.isna(feature_value):
                feature_value = feature_spec['default']
            if feature_spec['type'] == 'int':
                feature = tf.train.Feature(int64_list=tf.train.Int64List(value=[int(feature_value)]))
            elif feature_spec['type'] == 'float':
                feature = tf.train.Feature(float_list=tf.train.FloatList(value=[float(feature_value)]))
            elif feature_spec['type'] == 'str':
                feature = tf.train.Feature(
                    bytes_list=tf.train.BytesList(value=[str(feature_value).encode('utf-8')]))
            feature_dict[feature_name] = feature
        example = tf.train.Example(features=tf.train.Features(feature=feature_dict))
        return example.SerializeToString(), None

    train_rdd = sess.sparkContext.parallelize(rows, num_partitions).map(to_example)
    train_rdd.saveAsNewAPIHadoopFile(output_dir, 'org.tensorflow.hadoop.io.TFRecordFileOutputFormat',
                                     keyClass="org.apache.hadoop.io.BytesWritable",
                                     valueClass="org.apache.hadoop.io.NullWritable")

def dataset_from_tfrecords(tfrecords_pattern, include_outputs=False):
    all_feature_spec = deepcopy(model_spec['inputs'])
    if include_outputs:
        all_feature_spec.update(model_spec['outputs'])

    feature_dict = {}
    for feature_name, feature_spec in all_feature_spec.items():
        if feature_spec['type'] == 'int':
            feature = tf.io.FixedLenFeature((), tf.int64)
        elif feature_spec['type'] == 'float':
            feature = tf.io.FixedLenFeature((), tf.float32)
        elif feature_spec['type'] == 'str':
            feature = tf.io.FixedLenFeature((), tf.string)
        feature_dict[feature_name] = feature

    def parse_func(s):
        inputs = tf.io.parse_single_example(s, feature_dict)
        outputs = []
        if include_outputs:
            for output_name in model_spec['outputs']:
                outputs.append(inputs[output_name])
                inputs.pop(output_name)
        if include_outputs:
            return inputs, outputs
        return inputs

    dataset = tf.data.Dataset.list_files(tfrecords_pattern).interleave(
        lambda filename: tf.data.TFRecordDataset(filename).map(parse_func)
    )
    return dataset