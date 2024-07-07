import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
import ctypes
import winreg

CONFIG_FILE = "config.json"

INTERNET_SETTINGS = winreg.OpenKey(
    winreg.HKEY_CURRENT_USER,
    r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
    0,
    winreg.KEY_ALL_ACCESS,
)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return {"proxies": [], "current_proxy": get_system_proxy()}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def get_system_proxy():
    try:
        proxy_server, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, "ProxyServer")
        proxy_enable, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, "ProxyEnable")
        if proxy_enable:
            return proxy_server
        else:
            return "无代理"
    except FileNotFoundError:
        return "无代理"


def set_system_proxy(proxy):
    try:
        winreg.SetValueEx(INTERNET_SETTINGS, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(INTERNET_SETTINGS, "ProxyServer", 0, winreg.REG_SZ, proxy)
        refresh_internet_settings()
        config["current_proxy"] = proxy
        save_config(config)
        messagebox.showinfo("代理设置", f"代理已切换到 {proxy}")
    except Exception as e:
        messagebox.showerror("错误", f"无法设置代理: {e}")


def disable_proxy():
    try:
        winreg.SetValueEx(INTERNET_SETTINGS, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        refresh_internet_settings()
        config["current_proxy"] = "无代理"
        save_config(config)
        messagebox.showinfo("代理设置", "代理已禁用")
    except Exception as e:
        messagebox.showerror("错误", f"无法禁用代理: {e}")


def refresh_internet_settings():
    internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
    internet_set_option(0, 37, 0, 0)
    internet_set_option(0, 39, 0, 0)


def switch_proxy():
    selected_proxy = proxy_listbox.get(tk.ACTIVE)
    if selected_proxy == "移除代理":
        disable_proxy()
    else:
        set_system_proxy(selected_proxy)


def add_proxy():
    new_proxy = simpledialog.askstring("添加代理", "输入新的代理地址 (格式: host:port)")
    if new_proxy:
        config["proxies"].append(new_proxy)
        update_proxy_listbox()
        save_config(config)


def delete_proxy():
    selected_proxy = proxy_listbox.get(tk.ACTIVE)
    if selected_proxy in config["proxies"]:
        config["proxies"].remove(selected_proxy)
        update_proxy_listbox()
        save_config(config)


def edit_proxy():
    selected_proxy = proxy_listbox.get(tk.ACTIVE)
    if selected_proxy:
        new_proxy = simpledialog.askstring(
            "编辑代理", "编辑代理地址", initialvalue=selected_proxy
        )
        if new_proxy:
            index = config["proxies"].index(selected_proxy)
            config["proxies"][index] = new_proxy
            update_proxy_listbox()
            save_config(config)


def update_proxy_listbox():
    proxy_listbox.delete(0, tk.END)
    for proxy in config["proxies"]:
        proxy_listbox.insert(tk.END, proxy)
    proxy_listbox.insert(tk.END, "移除代理")  # 添加禁用代理的选项


def view_current_proxy():
    current_proxy = get_system_proxy()
    messagebox.showinfo("当前代理", f"当前代理: {current_proxy}")


# 读取配置
config = load_config()

app = tk.Tk()
app.title("HttpProxySwitcher")

frame = tk.Frame(app)
frame.pack(pady=10)

proxy_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=40)
proxy_listbox.pack(side=tk.LEFT, padx=10)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
proxy_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=proxy_listbox.yview)

button_frame = tk.Frame(app)
button_frame.pack(pady=10)

view_button = tk.Button(button_frame, text="查看当前代理", command=view_current_proxy)
view_button.pack(side=tk.LEFT, padx=5)

add_button = tk.Button(button_frame, text="添加代理", command=add_proxy)
add_button.pack(side=tk.LEFT, padx=5)

edit_button = tk.Button(button_frame, text="编辑代理", command=edit_proxy)
edit_button.pack(side=tk.LEFT, padx=5)

delete_button = tk.Button(button_frame, text="删除代理", command=delete_proxy)
delete_button.pack(side=tk.LEFT, padx=5)

switch_button = tk.Button(app, text="切换代理", command=switch_proxy)
switch_button.pack(pady=10)

info_label = tk.Label(
    app,
    text="HttpProxySwitcher v1.0 2024/07/07\nCopyright 2024 earthjasonlin\n保留所有权利。\n本程序仅作为交流学习使用",
    justify="center",
    anchor="center",
)
info_label.pack(pady=10, padx=20, fill="x")

# 自动调整窗口大小
app.update_idletasks()
app.minsize(app.winfo_reqwidth(), app.winfo_reqheight())
app.resizable(False, False)

# 更新列表框
update_proxy_listbox()

app.mainloop()
