if __name__=="__main__":
    stack=[]
    #push 入栈，末尾添加O(1)
    stack.append(100)
    stack.append(200)
    stack.append(300)
    print("栈：",stack)

    #pop 出栈（取出栈顶最后一个）
    top=stack.pop()
    print(f"弹出栈顶元素：{top},剩余栈{stack} 【O(1)】")