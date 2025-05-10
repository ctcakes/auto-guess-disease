import requests
import json
import urllib.parse
import time

#留空则不使用，不使用cookie无法增加次数
COOKIE = ""

def get_profile():
    if not COOKIE:
        print("未设置cookie，跳过获取用户资料")
        return True
        
    url = "https://xiaoce.fun/api/get_profile"
    
    headers = {
        "Cookie": COOKIE
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("用户资料:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get("success") and data.get("data"):
            user_info = data["data"]
            print(f"\n当前登录用户: {user_info.get('userName', '未知')}")
            print(f"用户ID: {user_info.get('userId', '未知')}")
            return True
        else:
            print("无法获取用户资料或未登录")
            return False
    except Exception as e:
        print(f"获取用户资料时出错: {e}")
        return False

def get_disease():
    url = "https://xiaoce.fun/api/v0/quiz/daily/addRecord?type=guess_disease&date=20250510&status=success"
    
    headers = {}
    if COOKIE:
        headers["Cookie"] = COOKIE
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success") and "data" in data and "data" in data["data"]:
            disease = data["data"]["data"]["disease"]
            success_count = data["data"]["success"]
            print(f"\n今天的疾病是: {disease}")
            return disease, success_count
        else:
            print("无法获取疾病信息")
            return None, 0
    except Exception as e:
        print(f"获取疾病时出错: {e}")
        return None, 0

def get_current_date():
    url = "https://xiaoce.fun/api/v0/quiz/daily/getDateV1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success") and "data" in data:
            current_date = data["data"]
            print(f"当前日期: {current_date}")
            return current_date
        else:
            print("无法获取当前日期")
            return None
    except Exception as e:
        print(f"获取日期时出错: {e}")
        return None

def send_message(disease, date):
    url = "https://xiaoce.fun/api/v0/quiz/daily/guessDisease/sendMessage"
    
    encoded_disease = urllib.parse.quote(disease)
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    if COOKIE:
        headers["Cookie"] = COOKIE
    
    data = f"date={date}&chatId=&message={encoded_disease}"
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        result = response.json()
        
        return result
    except Exception as e:
        print(f"发送消息时出错: {e}")
        return None

def add_record(date):
    url = f"https://xiaoce.fun/api/v0/quiz/daily/addRecord?type=guess_disease&date={date}&status=success"
    
    headers = {}
    
    if COOKIE:
        headers["Cookie"] = COOKIE
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success") and "data" in result:
            success_count = result["data"]["success"]
            print(f"成功添加记录！当前成功次数: {success_count}")
            return True, success_count
        else:
            print("添加记录失败")
            return False, 0
    except Exception as e:
        print(f"添加记录时出错: {e}")
        return False, 0

def full_process_mode(interval):
    success_count = 0
    
    while True:
        print(f"\n开始执行 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        disease, current_success = get_disease()
        if not disease:
            print(f"等待 {interval} 秒后重试...")
            time.sleep(interval)
            continue
        
        success_count = current_success
        
        date = get_current_date()
        if not date:
            print(f"等待 {interval} 秒后重试...")
            time.sleep(interval)
            continue
        
        result = send_message(disease, date)
        
        if result and result.get("success"):
            print("成功发送消息！")
            
            print("正在添加记录...")
            success, new_success_count = add_record(date)
            if success:
                success_count = new_success_count
                
            print(f"\n==================================================")
            print(f"当前总成功次数: {success_count}")
            print(f"==================================================")
        
        print(f"等待 {interval} 秒后重新执行...")
        time.sleep(interval)

def direct_mode(interval):
    success_count = 0
    
    while True:
        print(f"\n开始执行 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        date = get_current_date()
        if not date:
            print(f"等待 {interval} 秒后重试...")
            time.sleep(interval)
            continue
        
        print("正在添加记录...")
        success, new_success_count = add_record(date)
        if success:
            success_count = new_success_count
            
        print(f"\n==================================================")
        print(f"当前总成功次数: {success_count}")
        print(f"==================================================")
        
        print(f"等待 {interval} 秒后重新执行...")
        time.sleep(interval)

def answer_only_mode():
    disease, success_count = get_disease()
    if not disease:
        print("无法获取答案，请稍后再试")
        return
    
    date = get_current_date()
    if not date:
        print("无法获取当前日期，请稍后再试")
        return
    
    print("\n==================================================")
    print(f"今日答案: {disease}")
    print(f"当前日期: {date}")
    print(f"当前成功次数: {success_count}")
    print("请手动打开小测并输入此答案")
    print("==================================================")

def main():
    global COOKIE
    
    print("已读取cookie")
    if COOKIE == '':
        print('!!! 您未设置cookie，将无法增加猜对次数！cookie获取方法请看readme.md')
        print("不使用cookie将无法增加猜对次数！")
    
    get_profile()
    
    print("\n请选择模式:")
    print("1. 完整流程 (发送正确消息并添加次数)")
    print("2. 直接模式 (仅添加次数)")
    print("3. 仅显示答案 (不执行任何操作)")
    
    mode = input("请输入模式 (1/2/3): ")
    
    if mode in ["1", "2"]:
        try:
            interval = int(input("请输入执行间隔时间(秒): "))
        except ValueError:
            print("输入无效，使用默认间隔时间1秒")
            interval = 1
    
    if mode == "1":
        print("已选择完整流程模式")
        full_process_mode(interval)
    elif mode == "2":
        print("已选择直接模式")
        direct_mode(interval)
    elif mode == "3":
        print("已选择仅显示答案模式")
        answer_only_mode()
    else:
        print("无效的模式选择，退出程序")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已停止") 