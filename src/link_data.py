#================2.单项链表===========
class Node:
    def __init__(self,data):
        self.data=data
        self.next=None

class SingleLinkedList:
    def __init__(self):
        self.head=None

    #头部新增节点O(1)
    def add_head(self,data):
        new_node=Node(data)
        new_node.next=self.head
        self.head=new_node

    #遍历查找，最坏O(n)，必须从头一个个找
    def find(self,target):
        cur=self.head
        idx=0
        while cur:
            if cur.data==target:
                return idx
            cur=cur.next
            idx+=1
        return -1 

    # 打印链表
    def print_list(self):
        res=[]
        cur=self.head
        while cur:
            res.append(str(cur.data))
            cur=cur.next
        print("链表：","->".join(res))
if __name__=="__main__":
    link=SingleLinkedList()
    link.add_head(10)
    link.add_head(20)               
    link.add_head(30)               
    link.add_head(40) 
    link.print_list()
    print(f"查找10，位置：{link.find(10)} 【最坏O(n)】")              



