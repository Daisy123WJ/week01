import sys
#验收工具（每个文件都用同一套，最后一天的selfCheck会统一汇总）
_result={"pass":0,"fail":0,"fail_names":[]}

def check(name:str,cond:bool,hint:str="")->None:
    if cond:
        _result["pass"]+=1
        print(f"[OK]【{name}】测试通过")
    else:
        _result["fail"]+=1
        _result["fail_names"].append(name)
        print(f"[FAIL]【{name}】测试失败，{hint}")

def section(title:str)->None:
    print("\n"+"="*68)
    print(title)
    print("="*68)


def summanry_1()->None:
    section("1.变量与类型")
    name="张三"
    age=18
    price=19.9
    is_vip=True
    nothing=None
    print(f"姓名：{name!r},类型：{type(name)}")
    print(f"姓名：{name},类型：{type(name).__name__}")
    print(f"年龄：{age},类型：{type(age).__name__}")
    print(f"价格：{price},类型：{type(price).__name__}")
    print(f"是否VIP：{is_vip},类型：{type(is_vip).__name__}")
    print(f"空值：{nothing},类型：{type(nothing).__name__}")
    x=1
    x="我换成字符串了"
    print(f"x的值：{x!r},类型：{type(x).__name__}")

    print(f"add(1,2)={add(1,2)}")
    print(f"add(1,2)={add('1','2')}")
    check("变量可以重新赋成别的类型",True)
    check("类型注解不强制（add('1','2') 返回 '12'）", add("1", "2") == "12",
      "说明注解被强制执行了？那不符合 Python 行为")
    

def add(a:int,b:int)->int:
    return a+b

def summanry_2()->None:
    section("2.数值运算")
    print(f"7/2={7/2} <- 真除法，永远返回float (c# 里 7/2=3)")
    print(f"7//2={7//2} <- 整除(地板除)，返回整数 (c# 里 7/2=3)")
    print(f"7%2={7%2} <- 取余数，返回余数 (与c# 里一致)")
    print(f"2**10={2**10} <- 幂运算，返回2的10次方 (对应c#Math.Pow(2,10))")
    print(f"divmod(7,2)={divmod(7,2)} <- 返回商和余数的元组 (对应c# Math.DivRem(7,2))")

    big=2**100 #python 整数无溢出（c# long 会溢出，得用BigInteger）
    print(f"2**100={big} <- 任意精读整数，不用BigInteger）")

    check("7/2是浮点除法",7/2==3.5)
    check("7//2是整除",7//2==3)
    check("7%2是取余数",7%2==1)
    check("2**100得出的结果是整数不会溢出",2**100==1267650600228229401496703205376)
    check("divmod(7,2)返回商和余数",divmod(7,2)==(3,1))

def summanry_3()->None:
    section("3.字符串")
    s="Python for CSarp Dev"
    s1="1234567890abcdefghijklmnopqrstuvwxyz"
    print(f"s1[1:6]={s1[1:6]!r} <- 从索引1（包含1）开始截取，取到索引6之前的字符，不包含索引6")
    print(f"s[0:6]={s[0:6]!r} <- 切片，取前6个字符")
    print(f"s[:6]={s[:6]!r} <- 切片，取前6个字符")
    print(f"s[6:]={s[6:]!r} <- 切片，从第6个字符开始到末尾，包含索引6")
    print(f"s[-4:]={s[-4:]!r} <- 负数索引，从右往左截取，取末尾4个字符")
    print(f"s[::-1]={s[::-1]!r} <- 负数索引，从右往左截取，反转，从末尾截取不包含索引-1的字符")
    raw=" 1001,张三,西安 "
    a=raw.replace(",","|")
    print(f"replace处理字符串：{a} <- 把逗号替换成竖线")
    b=raw.strip()
    print(f"strip处理字符串：{b} <- 去掉首尾空格")
    parts=[p.strip() for p in raw.split(",")]
    print(f"split+strip处理字符串：{parts} <- 先按逗号分割，再去掉每个元素的首尾空格")
    print(f"'|'.join(...)-> {'|'.join(parts)} <- 再用竖线把列表拼接成字符串")

    #字符串不可变：任何 “修改”都是生成新对象
    print(f"replace返回新串(原串没有变):{s.replace("CSarp","C#")} /原始字符串仍是：{s!r} ")
    #多行字符串
    sql="""
    select city,sum(amount) 
    from orders 
    group by city
    """
    print(f"三行字符串length={len(sql.strip().splitlines())}行")

    check("负索引可用",s[-1]=="v")
    check("切片反转正确",s[::-1]==s[::-1][::-1][::-1])
    check("join 拼接正确","|".join(parts)=="1001|张三|西安")

def summanry_4()->None:
    section("4.容器：list/tuple/dict/set")

    #--- list:有序，可变-------[C#]List<T>
    nums=[3,1,4,1,5,9,2,6]
    print(f"list :{nums}")
    nums.append(7)
    nums.remove(1)
    print(f"append/remove->{nums}")
    print(f"sorted()返回新列表：{sorted(nums)} <-Linq orderby，但立刻执行")
   
    nums.sort(reverse=False) #升序排序，返回None(C# 的list.sort也是原地，但返回void)
    print(f"升序排序sort():{nums}")

    nums.sort(reverse=True) #降序排序，返回None(C# 的list.sort也是原地，但返回void)
    print(f"降序排序sort():{nums}")
    #----tuple:不可变---------【C#】 ValueTuple/readnly
    point=(3,5)
    lat,lon=point #解构，跟C#一样
    print(f"tuple解构：lat={lat},lon={lon}")
    #point[0]=99  #取消注释会TypeError，这是“不可变”的意义

    #------dict:键值对------------[C#]Dictionary<Tkey,TValue>(但保序)
    user={"id":1001,"name":"张三","city":"西安"}
    user["level"]="A" #
    print(f"dic:{user}")
    print(f"取不存在的键要用get:{user.get('phone','未填写')}<- 直接user['phone'] 会KeyError")

    for k,v in user.items():
        print(f"{k}={v}")

    #---set 去重集合------c# hashset<T>
    tags={"python","backend","python"}
    print(f"set自动去重：{tags}")
    print(f"集合交并差：{tags & {'python','ai'}}/{tags|{'ai'}}")

    tags1={"1","2","3","1","4","2","6"}
    print(f"python中，数组重试时会自动去重：{tags1}")
    check("list append +sorted正常",nums==[9,7,6,5,4,3,2,1])
    check("tuple 可以解构",lat==3 and lon==5)
    check("dict.get有兜底",user.get("phone","未填写")=="未填写")
    check("set 去重后只有2个元素",len(tags)==2)
def summanry_5()->None:
    section("5.引用语义")
    #大部分python 对象都是引用类型，赋值不复制
    a=[1,2,3]
    b=a # 不是复制，b和a 指向同一个list
    b.append(4)
    print(f"a={a}  <= a也被改了")

    c=a[:] #浅拷贝 这才是"复制"
    c.append(99)
    print(f"a={a}/c={c} <- 切片复制后互不影响")

    origin=[1,2]
    add_item(origin,3)
    print(f"origin={origin} ")
    reassign(origin)
    print(f"origin={origin} <- add_item生效了,reassign没生效")

    print(f"bad()连续调用：{bad()}{bad()}{bad()} <- 默认值只创建一次")
    check("赋值是同一个对象",a==[1,2,3,4])
    check("切片拷贝互不影响",99 not in a)
    check("函数内append不影响外部",origin==[1,2,3])
    check("重新绑定不影响外部(origin里没有0)",0 not in origin)
    check("默认参数陷阱现象存在",bad()==[1,1,1,1])


def reassign(lst:list)->None:
    lst=[0]  #只改了函数内的局部名字，外面不受影响
def add_item(lst:list,item)->None:
    lst.append(item) #会改到外面
def bad(items=[]):
    items.append(1)
    return items

def summanry_6()->None:
    section("6.缩进即语法")
    total=0
    for n in range(1,6):
        total+=n
        print(f" 累加到{n}->{total}")
    print(f"1+...+5={total} <- 缩进决定了哪些行在循环里(C# 靠花括号)")   
    if total==15:
        print(" 缩进正确，if体在4个空格内")
    check("循环累加结果正确",total==15)  

def summanry_7()->None:
    section("7.Day1 自检结果")
    total_checks=_result["pass"]+_result["fail"]
    print(f" 通过{_result['pass']}/{total_checks}")
    if _result["fail"]:
        print(f" 待修：{_result['fail_names']}")
        print(" ->先别往下走，把上面FAIL的项改对再继续")
    else:
        print(f"-->全通过，请再手册Day1验收菜单上打勾")
print(" 下一步:手改5个值重跑一遍---改 name/price/nums/point/user，观察输出变化")

if __name__=="__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')  # 设置标准输出流的编码为 UTF-8
        summanry_1()
        summanry_2()
        summanry_3()
        summanry_4()
        summanry_5()
        summanry_6()
        summanry_7()
    except Exception as e:
        pass
