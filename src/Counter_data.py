from collections import Counter,defaultdict,deque
import itertools

if __name__=="__main__":
    # ================1.Counter 统计计数（频次归一化，课程重点）=============
    print("====1.Counter频次统计+归一化============")
    data_list=["苹果","香蕉","苹果","橙子","香蕉","苹果","苹果"]
    #--统计所有元素出现次数
    cnt=Counter(data_list)
    total=sum(cnt.values())

    for k,v in cnt.items():
        ratio=v/total
        #f-string 格式输出
        print(f"水果【{k}】:出现{v}次，占比{ratio:.2f}")
# 一句话：把列表丢给Counter,一行完成频次统计，使用：词频，用户行为统计，投票结果统计

    d=defaultdict(int)
    words=["cat","dog","cat","bird","dog","cat"]    
    for w in words:
        d[w]+=1
    for k,v in d.items():
        print(f"单词【{k}】:出现{v}次")   
   
   # 一句话：key不存在时，自动从默认值开始计数，
   # 适用：分组统计，累加求和，按类别收集数据

    dq=deque([100,200,300])
    print("入列：",dq) 
    first=dq.popleft()
    print(f"出队元素：{first},剩余队列{dq} 【O(1)】")

    dq.appendleft(99)
    print("在头部插入后，队列信息为：",dq)     

    dq.append(400)
    print("在尾部插入后，队列信息为：",dq)

    #一句话：deque 擅长队列、栈和滑动窗口，
    # 适用：任务队列，消息缓冲，最近N条积累

    for i in itertools.product([1,2],("A","B")):
        print(i)

    cnt=itertools.count(start=10,step=5)
    print(next(cnt))
    print(next(cnt))    

#一句话：itertools 帮你高效生成组和和序列。
# 适用：排列组合，测试用例生成，循环计数

name="Alice"
age=18
score=95.666
print(f"姓名：{name},年龄：{age}")
print(f"分数：{score:.2f}")
print(f"明年年龄：{age+1}")  #总宽度10，保留两位小数
    