# 用列表嵌套字典构建电影库
movie_database = [
    {"title": "流浪地球2", "type": "科幻", "rating": 8.3, "year": 2023},
    {"title": "你好，李焕英", "type": "喜剧", "rating": 8.1, "year": 2021},
    {"title": "满江红", "type": "悬疑", "rating": 7.6, "year": 2023},
    {"title": "人生大事", "type": "剧情", "rating": 7.3, "year": 2022},
    {"title": "疯狂的石头", "type": "喜剧", "rating": 8.6, "year": 2006},
    {"title": "星际穿越", "type": "科幻", "rating": 9.4, "year": 2014},
    {"title": "唐人街探案3", "type": "喜剧", "rating": 5.3, "year": 2021}
]

# 获取用户偏好:用户的电影类型偏好和最低评分要求
'''这个函数仅仅接受两个输入值'''
def get_user_preference():
    # 输入喜欢的电影类型（如：喜剧/科幻/悬疑）
    user_type = input()
    #数据容器 + 类型转换（处理用户输入的字符串为浮点数）
    while True:  # 循环：确保用户输入合法的评分
        try:
            # 输入可接受的最低评分（如：8.0）
            min_rating = float(input())
            if 0 <= min_rating <= 10:
                break
            else:
                print("评分需在0-10之间,请重新输入!")
        except ValueError:
            print("请输入数字（如8.0）,不要输入文字!")
    return user_type, min_rating

# 根据用户偏好筛选电影
'''这个函数逐个比较（双重条件），并返回一个列表包含符合条件的电影'''
def recommend_movies(user_type, min_rating, movie_db):
    """
    :param user_type: 用户喜欢的类型
    :param min_rating: 最低评分要求
    :param movie_db: 电影库数据
    :return: 符合条件的电影列表
    """
    # 请在此处编写代码
    # ====================Begin====================
    recommended = []
    for i in movie_db:
        if user_type == i['type'] and min_rating <= i['rating'] :
            recommended.append(i)


    # ====================end=====================
    return recommended

# 输出推荐结果
'''逐个输出符合条件的电影'''
def show_recommendation(recommended):
    """展示推荐结果"""
    print("===== 为你推荐的电影 ======")

    # 请在此处编写代码
    # ====================Begin====================
    if not recommended:  # 条件判断：无推荐的情况
        print("暂无符合你偏好的电影！")
    else:

        for i in range(len(recommend)):
            print(f"{i+1}. 标题：{recommend[i]['title']} | 类型：{recommend[i]['type']} | 评分：{recommend[i]['rating']} | 年份：{recommend[i]['year']}")

    # ====================end=====================

# 主程序入口
if __name__ == "__main__":

    # 请在此处编写代码
    # ====================Begin====================
    user_type,min_rating =get_user_preference()'''接受用户输入'''
    recommend = recommend_movies(user_type, min_rating, movie_database)'''查询电影库，筛选符合条件的电影'''
    show_recommendation(recommend)'''根据这个列表来输出结果'''
    # ====================end=====================