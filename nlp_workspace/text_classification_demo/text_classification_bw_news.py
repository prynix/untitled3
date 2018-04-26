#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
# Created by yaochao at 2018/4/11


import pymysql
import random
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
import gensim
import numpy as np
from keras.layers import Embedding, Dropout, Conv1D, MaxPool1D, Flatten, Dense
from keras.models import Sequential
from keras.utils import plot_model
import matplotlib.pyplot as plt
from keras.callbacks import TensorBoard

MYSQL_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'passwd': 'toor',
    'db': 'datasets',
    'charset': 'utf8',
    'cursorclass': pymysql.cursors.DictCursor
}
TAGS = {'高血压': 1, '糖尿病': 2, '儿童': 3, '孕产妇': 4, '中药': 5, '养生': 6}
MAX_SEQUENCE_LENGTH = 200
EMBEDDING_DIM = 100
TRAIN_SPLIT = 0.6
VALIDATION_SPLIT = 0.2
TEST_SPLIT = 0.2
W2V_MODEL = '/Users/yaochao/python/datasets/downloads/cn.cbow.dim300.bin'
W2V_MODEL2 = '/Users/yaochao/python/datasets/haodf_chats_detail_1000W_pre.csv.w2v_model'
TRAINED_MODEL = 'cnn.w2v.model'


def plot_history(history, pre_filename=''):
    # 训练过程可视化
    loss = history.history['loss']
    acc = history.history['acc']
    val_loss = history.history['val_loss']
    val_acc = history.history['val_acc']
    print(loss)
    print(acc)
    print(val_loss)
    print(val_acc)

    fig1 = plt.figure(1)
    plt.plot(acc)
    plt.plot(val_acc)
    plt.title('model accuracy')
    plt.xlabel('epoch')
    plt.ylabel('accuracy')
    plt.legend(['acc', 'val_acc'], loc='lower right')
    fig1.savefig(pre_filename + '_acc.png')

    fig2 = plt.figure(2)
    plt.title('model loss')
    plt.plot(loss)
    plt.plot(val_loss)
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.legend(['loss', 'val_loss'], loc='upper right')
    fig2.savefig(pre_filename + '_loss.png')


def get_texts_labels():
    '''
    load texts and labels.
    :return:
    '''
    items = []
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    for tag in TAGS.keys():
        sql = 'select content_fenci, news_tags from bw_news where content_fenci is not null and news_tags=%s and status=1 limit 2000'
        cursor.execute(sql, tag)
        items += cursor.fetchall()
    random.shuffle(items)
    random.shuffle(items)
    print('1.一共有{}条数据'.format(len(items)))
    texts = [x['content_fenci'] for x in items]
    labels = [TAGS[x['news_tags']] for x in items]
    return texts, labels


def texts_labels_tokenizer(texts, labels):
    '''
    convert text to tokenized-text（a sequence by int symbol）
    :return:
    '''
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    word_index = tokenizer.word_index
    print('2.一共找到{}个不同的词'.format(len(word_index)))
    sequences = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
    # sequences = pad_sequences(sequences)
    labels = to_categorical(labels)
    print('sequences的shape:{}'.format(sequences.shape))
    print('labels的shape:{}'.format(labels.shape))
    return sequences, labels, word_index


def texts_labels_slicer(texts, labels):
    '''
    slice to three parts: train, validate, and test.
    [train:validate:text] [0.6:0.2:0.2]
    :return:
    '''
    part1 = int(len(texts) * TRAIN_SPLIT)
    part2 = int(len(texts) * (TRAIN_SPLIT + VALIDATION_SPLIT))
    train_texts = texts[:part1]
    validate_texts = texts[part1:part2]
    test_texts = texts[part2:]
    train_labels = labels[:part1]
    validate_labels = labels[part1:part2]
    test_labels = labels[part2:]
    print('train: ', len(train_texts))
    print('validate: ', len(validate_texts))
    print('test: ', len(test_texts))
    return train_texts, train_labels, validate_texts, validate_labels, test_texts, test_labels


def load_w2v_as_embedding(word_index, input_length):
    '''
    use w2v as embedding
    '''
    # w2v_model = gensim.models.KeyedVectors.load_word2vec_format(W2V_MODEL, binary=True, unicode_errors='ignore')
    w2v_model = gensim.models.Word2Vec.load(W2V_MODEL2)
    embedding_metrix = np.zeros((len(word_index) + 1, EMBEDDING_DIM))
    not_in_w2v = 0
    for word, index in word_index.items():
        if word in w2v_model:
            embedding_metrix[index] = np.asarray(w2v_model[word])  # TODO
        else:
            not_in_w2v += 1
    print('{}个词不在w2v模型中'.format(not_in_w2v))
    embedding_layer = Embedding(input_dim=len(word_index) + 1, output_dim=EMBEDDING_DIM, input_length=input_length,
                                weights=[embedding_metrix],
                                trainable=False)
    return embedding_layer


def train_model_cnn_w2v(word_index, input_length, labels, x_train, y_train, x_validate, y_validate):
    '''
    constructure and train model
    '''
    embedding_layer = load_w2v_as_embedding(word_index=word_index, input_length=input_length)  # 使用word2vec的向量模型来构造embedding_layer
    # embedding_layer = Embedding(input_dim=len(word_index) + 1, output_dim=EMBEDDING_DIM, input_length=input_length) # 不使用word2vec的向量模型来构造embedding_layer

    model = Sequential()
    model.add(embedding_layer)
    model.add(Dropout(rate=0.2))
    model.add(Conv1D(filters=250, kernel_size=3, strides=1, padding='valid', activation='relu'))
    model.add(MaxPool1D(pool_size=3))
    model.add(Flatten())
    model.add(Dense(units=EMBEDDING_DIM, activation='relu'))
    model.add(Dense(units=labels.shape[1], activation='softmax'))
    model.summary()
    plot_model(model, to_file='bwnews_model.png', show_shapes=True)
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['acc'])
    print(model.metrics_names)

    # 如果 validation_split 设置，会从训练数据分割后面0.2的数据做为验证数据集。
    # 启动 TensorBoard，在fit中的callbacks=[tb]
    # tb = TensorBoard(log_dir='/Users/yaochao/logs', histogram_freq=0, write_graph=True, write_images=True)
    # history = model.fit(x=x_train, y=y_train, validation_split=0.2, epochs=3, batch_size=128)
    history = model.fit(x=x_train, y=y_train, validation_data=(x_validate, y_validate), epochs=10, batch_size=100)
    plot_history(history, pre_filename='bwnews_cnn_w2v')
    # model.save(TRAINED_MODEL)
    return model


def evaluate_model(model, x_test, y_test):
    '''
    test model
    '''
    return model.evaluate(x=x_test, y=y_test)


def main():
    '''
    使用预训练的w2v模型来构造embedding_layer。
    :return:
    '''
    # 1. 加载文本，标签
    texts, labels = get_texts_labels()
    # 2. 单词映射，单词tokenize化
    sequences, labels, word_index = texts_labels_tokenizer(texts, labels)
    # 3. 数据分割为，训练集，验证集，测试集
    x_train, y_train, x_validate, y_validate, x_test, y_test = texts_labels_slicer(sequences, labels)
    # 4. 构造模型，训练模型
    model = train_model_cnn_w2v(word_index, MAX_SEQUENCE_LENGTH, labels, x_train, y_train, x_validate, y_validate)
    # 5. 评估验证模型
    loss, accuracy = evaluate_model(model, x_test, y_test)
    print(loss, accuracy)


if __name__ == '__main__':
    main()
