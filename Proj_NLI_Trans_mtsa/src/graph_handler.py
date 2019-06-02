import tensorflow as tf
import os
import logging as log


class GraphHandler(object):
    def __init__(self, model_obj, cfg):
        self.model_obj = model_obj
        self.cfg = cfg
        self.saver = tf.train.Saver(max_to_keep=3)
        self.writer = None

    def initialize(self):
        # gpu and its memory manager
        os.environ['CUDA_VISIBLE_DEVICES'] = str(self.cfg['gpu'])
        # create session
        sess = tf.Session(config=self.sess_config_gene(self.cfg['gpu_mem']))
        # init variables
        sess.run(tf.global_variables_initializer())
        # restore
        if self.cfg['load_model']:
            self.load_ckpt(sess)
        # add summary
        if self.cfg['mode'] == 'train':
            self.writer = tf.summary.FileWriter(
                logdir=self.cfg['summary_dir'], graph=tf.get_default_graph())
        return sess

    def add_summary(self, summary, global_step):
        if summary is not None and global_step is not None:
            self.writer.add_summary(summary, global_step)

    def add_summaries(self, summaries, global_step):
        for summary in summaries:
            self.add_summary(summary, global_step)

    def save_ckpt(self, sess, global_step=None):
        log.info('saving ckpt...')
        self.saver.save(sess, self.cfg['ckpt_path'], global_step)

    def load_ckpt(self, sess):
        log.info('loading ckpt...')
        if os.path.isdir(self.cfg['params.load_path']):
            ckpt_file_path = tf.train.latest_checkpoint(
                self.cfg['load_path']
            )
        else:
            ckpt_file_path = self.cfg['load_path']
        try:
            self.saver.restore(sess, ckpt_file_path)
            log.info('success to restore')
        except tf.errors.NotFoundError:
            log.info('failure to restore')
            if self.cfg['mode'] != 'train':
                raise FileNotFoundError('cannot find model file')

    @staticmethod
    def sess_config_gene(gpu_mem):
        if gpu_mem is None:
            gpu_options = tf.GPUOptions(allow_growth=True)
            graph_config = tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True)
        elif gpu_mem < 1.:
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_mem)
            graph_config = tf.ConfigProto(gpu_options=gpu_options)
        else:
            gpu_options = tf.GPUOptions()
            graph_config = tf.ConfigProto(gpu_options=gpu_options)
        return graph_config
