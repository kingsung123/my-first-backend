import datetime

now = datetime.datetime.now()
print("現在時間：", now)

import csv
import os
from datetime import datetime
from tabulate import tabulate

FILENAME = "expenses.csv"

def show_menu():
    print("\n=== 支出記錄器 ===")
    print("1. 新增支出")
    print("2. 查看紀錄")
    print("3. 離開")

def add_expense():
    item = input("支出項目：")
    amount = input("金額（元）：")
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(FILENAME, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([date, item, amount])
    print("✅ 支出已記錄！")

def view_expenses():
    if not os.path.exists(FILENAME):
        print("⚠️ 尚無支出紀錄。")
        return
    with open(FILENAME, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        data = list(reader)
        if data:
            print("\n🧾 支出紀錄：")
            print(tabulate(data, headers=["日期", "項目", "金額"], tablefmt="grid"))
        else:
            print("⚠️ 支出紀錄為空。")

def main():
    while True:
        show_menu()
        choice = input("請輸入選項（1/2/3）：")
        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            print("👋 再見！")
            break
        else:
            print("❌ 無效選項")

if __name__ == "__main__":
    main()
