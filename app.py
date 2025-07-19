def show_menu():
    print("===== 命令列記事本 =====")
    print("1. 新增筆記")
    print("2. 查看所有筆記")
    print("3. 離開程式")

def add_note():
    note = input("請輸入筆記內容：")
    with open("notes.txt", "a", encoding="utf-8") as file:
        file.write(note + "\n")
    print("✅ 筆記已儲存！")

def view_notes():
    try:
        with open("notes.txt", "r", encoding="utf-8") as file:
            print("\n📝 所有筆記：")
            print(file.read())
    except FileNotFoundError:
        print("⚠️ 尚未有任何筆記。")

def main():
    while True:
        show_menu()
        choice = input("請選擇操作（1/2/3）：")
        if choice == "1":
            add_note()
        elif choice == "2":
            view_notes()
        elif choice == "3":
            print("👋 再見！")
            break
        else:
            print("❌ 無效的選項，請重新輸入。")

# 程式進入點
if __name__ == "__main__":
    main()
