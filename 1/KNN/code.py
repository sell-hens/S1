#  请在此处编写代码，实现使用 KNN 算法分类
# ====================Begin===================
# 导入必要的库
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def   run_knn_person_classification(train_size,random_state):

    # ==================== 1. 数据加载 ====================
    data = pd.read_csv("500_Person_Gender_Height_Weight_Index.csv")


    # ==================== 3. 将 Gender 编码为数值 ====================
    encoder = LabelEncoder()
    data['Gender'] = encoder.fit_transform(data['Gender'])  
    #GEnder 列变成0/1
    
    # ==================== 2. 生成自变量和因变量 ====================
    X = data[['Height','Weight','Gender']]
    y = data['Index']

    # ==================== 4. 数据集划分 ====================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        train_size=0.8,
        random_state=42,
        stratify=y  # 分层划分保证每个类别比例相同
    )

    # ==================== 5. 特征标准化 ====================
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ==================== 6. KNN 模型训练 ====================
    model = KNeighborsClassifier(
        n_neighbors = 5,
        metric='minkowski',#一种距离计算方式
        weights='uniform',#uniform代表来自所有邻居的权重相同
        p= 2,
        algorithm='auto'
    )
    model.fit(X_train_scaled,y_train)
    
    # ==================== 7. 模型预测与评估 ====================
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted")
    recall = recall_score(y_test, y_pred, average="weighted")
    f1 = f1_score(y_test, y_pred, average="weighted")

# ====================End===================
    return float(accuracy), float(precision), float(recall), float(f1)

