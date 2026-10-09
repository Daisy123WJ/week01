arr=[10,20,30,40]
print("原始列表：",arr)

#1.按下标取值 O(1)
print("获取索引为0对应的值为：",arr[0])


#2.末尾追加元素 O(1)
arr.append(50)


print("在末尾追加50后，数组信息为：",arr)


#3.向中间元素 O(n) ,后面元素全部后移
arr.insert(2,99)

print("insert(2,99)后，数组信息为：",arr)

#4.遍历元素 （找目标值，最坏O(n)）
def find_val(arr,target):
    for item in arr:
        if item==target:
            return True
    return False

# 列表list (python 内置，最常用)
if __name__=="__main__":
    
     val=find_val(arr,20)  
     print(f"找到20的位置：{val}【最坏O(0)】")
