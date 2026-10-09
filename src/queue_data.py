from collections import deque
if __name__=="__main__":
    q=deque()
    #入队，尾部添加O(1)
    q.append(1)
    q.append(2)
    q.append(3)
    print("队列：",q)

    #出队，取出最前面元素O(1)
    first=q.popleft()
    print(f"出队元素：{first},剩余队列{q} 【O(1)】")
