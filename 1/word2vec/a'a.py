from gensim.models.word2vec import Word2Vec
import jieba

class TrainWord2Vec:
    def __init__(self, stopwords_file,
                 num_features=50,
                 min_word_count=1,
                 context=5,
                 incremental=False,
                 old_path=None):
        self.stopwords = self._get_stopwords(stopwords_file)
        self.num_features = num_features
        self.min_word_count = min_word_count
        self.context = context
        self.incremental = incremental
        self.old_path = old_path
    def _get_stopwords(self, file_path):#得到 一些无关紧要的词token
        stopwords = set()
        with open(file_path, 'r') as infile:
            for line in infile:
                line = line.rstrip('')
            if line:
                stopwords.add(line.lower())
        return stopwords

    def get_text(self, content_file):
        corpus = []
        for line in open(content_file, 'r', encoding='utf-8'):    
                curr_words = []
                for word in jieba.cut(line.strip().split('	')[0]):
                    if word not in self.stopwords:
                        curr_words.append(word)
                corpus.append(curr_words)
        print(corpus)
        return corpus
    def update_model(self, text):#模型的更新
        model = Word2Vec.load(self.old_path)
        model.build_vocab(text, update=True)
        model.train(sentences=text,
                    total_examples=model.corpus_count,
                    epochs=model.iter)
        return model

    def run(self, content_file, save_path):
        text = self.get_text(content_file)
        if self.incremental:
            model = self.update_model(text)
        else:
            model = self.get_model(text)
        model.save(save_path + "/word2vec_new.model")










from gensim.models import Word2Vec
import numpy as np
import jieba
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

class LrW2vModel(object):
    def __init__(self, w2v, labels):
        self.w2v = self._load_w2v(w2v)
        self.class_list = [x.strip() for x in open(labels, encoding='utf-8').readlines()]
        self.model = LogisticRegression(multi_class='multinomial', solver='lbfgs')
    def _compute_doc_vec_single(self, article):#变成向量
        vec = np.zeros((self.w2v.layer1_size,), dtype=np.float32)
        n = 0
        for word in article:
            if word in self.w2v:
                vec += self.w2v[word]
                n += 1
        return vec / n
    def _compute_doc_vec(self, articles):#循环使用前置函数
        return np.row_stack([self._compute_doc_vec_single(x) for x in articles])     
    
    
    def train(self, data):
        articles, labels = self._get_text_label(data)
        x = self._compute_doc_vec(articles)
        self.model.fit(x, labels)

    def evaluate(self, data):
        articles, labels = self._get_text_label(data)
        x = self._compute_doc_vec(articles)
        y_pred = self.model.predict(x)
        return classification_report(y_pred=y_pred,
                                    y_true=labels,
                                    labels=[0,1,2,3,4,5,6,7],
                                    target_names=self.class_list)
    





    
if __name__ == '__main__':
    train_data='95598_1/train.txt'
    dev_data = '95598_1/test.txt'
    w2v = 'vectors/word2vec_new.model'
    labels = '95598_1/class.txt'
    model = LrW2vModel(w2v,labels,model_type='lr')
    model.train(train_data)
    print(model.evaluate(dev_data))
    print("\n==========切换为 SVM 模型==========")
    model = LrW2vModel(w2v,labels,model_type='lr')
    model.train(train_data)
    print(model.evaluate(dev_data))