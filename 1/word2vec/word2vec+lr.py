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
    def _compute_doc_vec_single(self, article):
        vec = np.zeros((self.w2v.layer1_size,), dtype=np.float32)
        n = 0
        for word in article:
            if word in self.w2v:
                vec += self.w2v[word]
                n += 1
        return vec / n

    def _compute_doc_vec(self, articles):
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