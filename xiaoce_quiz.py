import requests
import json
import urllib.parse
import time

# 直接在代码中定义cookie
COOKIE = "Hm_lvt_367e22c6d5b5a12a4d06746488e29b3f=1746840306,1746850535,1746860406; HMACCOUNT=67C6860B919428D5; fun_ticket=yFpAtY_8mqNIsf2JLunIksLkNHQ2yFcsvPp3D95zjcwlWueLheuocWgosUOrlmaEIOLRGw-a7YuEt3I_sieVaQ; SESSION=OTM3ZjhmYWYtZWNjMS00YTE3LWI1OTYtNzExNDk0NjMzOTQy; Hm_lpvt_367e22c6d5b5a12a4d06746488e29b3f=1746861616"

def get_profile():
    """获取用户资料信息"""
    url = "https://xiaoce.fun/api/get_profile"
    
    # 设置请求头
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
    """获取当天的疾病信息"""
    url = "https://xiaoce.fun/api/v0/quiz/daily/addRecord?type=guess_disease&date=20250510&status=success"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
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
    """获取当前日期"""
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

def send_message(disease, date, cookie):
    """发送疾病信息"""
    url = "https://xiaoce.fun/api/v0/quiz/daily/guessDisease/sendMessage"
    
    # URI编码疾病名称
    encoded_disease = urllib.parse.quote(disease)
    
    # 设置请求头和cookie
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": cookie
    }
    
    # 设置请求参数
    data = f"date={date}&chatId=&message={encoded_disease}"
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        result = response.json()
        
        return result
    except Exception as e:
        print(f"发送消息时出错: {e}")
        return None

def add_record(date, cookie):
    """添加记录"""
    url = f"https://xiaoce.fun/api/v0/quiz/daily/addRecord?type=guess_disease&date={date}&status=success"
    
    # 设置请求头
    headers = {
        "Cookie": cookie
    }
    
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
    """完整流程模式"""
    success_count = 0
    
    while True:
        print(f"\n开始执行 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 获取疾病信息
        disease, current_success = get_disease()
        if not disease:
            print(f"等待 {interval} 秒后重试...")
            time.sleep(interval)
            continue
        
        success_count = current_success
        
        # 获取当前日期
        date = get_current_date()
        if not date:
            print(f"等待 {interval} 秒后重试...")
            time.sleep(interval)
            continue
        
        # 发送消息
        result = send_message(disease, date, COOKIE)
        
        # 如果成功，输出成功信息
        if result and result.get("success"):
            print("成功发送消息！")
            
            # 执行一次后，请求添加记录接口
            print("正在添加记录...")
            success, new_success_count = add_record(date, COOKIE)
            if success:
                success_count = new_success_count
                
            print(f"\n==================================================")
            print(f"当前总成功次数: {success_count}")
            print(f"==================================================")
        
        # 等待下一次执行
        print(f"等待 {interval} 秒后重新执行...")
        time.sleep(interval)

def direct_mode(interval):
    """直接添加记录模式"""
    success_count = 0
    
    while True:
        print(f"\n开始执行 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 获取当前日期
        date = get_current_date()
        if not date:
            print(f"等待 {interval} 秒后重试...")
            time.sleep(interval)
            continue
        
        # 直接添加记录
        print("正在添加记录...")
        success, new_success_count = add_record(date, COOKIE)
        if success:
            success_count = new_success_count
            
        print(f"\n==================================================")
        print(f"当前总成功次数: {success_count}")
        print(f"==================================================")
        
        # 等待下一次执行
        print(f"等待 {interval} 秒后重新执行...")
        time.sleep(interval)

def main():
    # 首先获取用户资料
    print("正在获取用户资料...")
    if not get_profile():
        print("无法获取用户资料，请检查Cookie是否有效")
        return
    
    # 选择模式
    print("\n请选择模式:")
    print("1. 完整流程 (发送正确消息并添加次数)")
    print("2. 直接模式 (仅添加次数)")
    
    mode = input("请输入模式 (1/2): ")
    
    # 询问间隔时间
    try:
        interval = int(input("请输入执行间隔时间(秒): "))
    except ValueError:
        print("输入无效，使用默认间隔时间1秒")
        interval = 1
    
    # 根据选择的模式执行
    if mode == "1":
        print("已选择完整流程模式")
        full_process_mode(interval)
    elif mode == "2":
        print("已选择直接模式")
        direct_mode(interval)
    else:
        print("无效的模式选择，退出程序")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已停止") 