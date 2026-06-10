"""
Sakila DVD 租赁管理系统 — 主入口
"""
import hashlib
import tkinter
import tkinter.ttk
from tkinter.ttk import Notebook
from tkinter.messagebox import showerror, showinfo

from db import querySql
import film_ui
import actor_ui
import customer_ui
import rental_ui
import inventory_ui


def run():
    root = tkinter.Tk()
    root.title('Sakila DVD 租赁管理系统 — 登录')
    root.geometry('400x280+500+300')
    root.resizable(False, False)

    staff_info = {}

    def clear_root():
        for w in root.winfo_children():
            w.destroy()

    def show_main():
        clear_root()
        root.geometry('980x720+250+50')
        root.title(f'Sakila DVD 租赁管理系统 — '
                   f'{staff_info["first_name"]} {staff_info["last_name"]}')
        root.resizable(True, True)

        status_var = tkinter.StringVar(
            value=f'已登录: {staff_info["first_name"]} '
                  f'{staff_info["last_name"]} (门店 {staff_info["store_id"]})')
        status_bar = tkinter.Label(root, textvariable=status_var,
                                   anchor='w', relief=tkinter.SUNKEN, bg='#f0f0f0')
        status_bar.place(x=0, y=695, width=980, height=25)

        notebook = Notebook(root)
        notebook.place(x=5, y=5, width=970, height=685)

        notebook.add(rental_ui.create_rental_frame(notebook, staff_info), text='租赁处理')
        notebook.add(customer_ui.create_customer_frame(notebook), text='客户管理')
        notebook.add(inventory_ui.create_inventory_frame(notebook, staff_info), text='库存管理')
        notebook.add(film_ui.create_film_frame(notebook), text='电影管理')
        notebook.add(actor_ui.create_actor_frame(notebook), text='演员管理')

    def do_login():
        username = entry_user.get().strip()
        password = entry_pass.get().strip()

        if not username:
            showerror(title='登录失败', message='用户名不能为空')
            return

        if password:
            pw_sql = f'password="{hashlib.sha1(password.encode()).hexdigest()}"'
        else:
            pw_sql = 'password IS NULL'

        rows = querySql(
            f'SELECT staff_id, first_name, last_name, email, store_id '
            f'FROM staff WHERE username="{username}" AND {pw_sql}'
        )
        if not rows:
            showerror(title='登录失败', message='用户名或密码错误')
            return

        staff_info['id'] = rows[0][0]
        staff_info['first_name'] = rows[0][1]
        staff_info['last_name'] = rows[0][2]
        staff_info['email'] = rows[0][3]
        staff_info['store_id'] = rows[0][4]

        showinfo('登录成功',
                 f'欢迎 {staff_info["first_name"]} {staff_info["last_name"]} 登录系统')
        show_main()

    # --- 登录界面 ---
    frame = tkinter.Frame(root)
    frame.pack(expand=True, fill=tkinter.BOTH, padx=30, pady=20)

    tkinter.Label(frame, text='Sakila DVD 租赁管理系统',
                  font=('Arial', 16, 'bold')).pack(pady=(10, 20))

    tkinter.Label(frame, text='用户名：').pack(anchor='w')
    entry_user = tkinter.Entry(frame, font=('Arial', 12))
    entry_user.pack(fill='x', pady=(2, 10))

    tkinter.Label(frame, text='密码：').pack(anchor='w')
    entry_pass = tkinter.Entry(frame, show='*', font=('Arial', 12))
    entry_pass.pack(fill='x', pady=(2, 15))
    entry_pass.bind('<Return>', lambda e: do_login())

    btn_frame = tkinter.Frame(frame)
    btn_frame.pack(fill='x')

    tkinter.Button(btn_frame, text='登录', width=12, height=2,
                   command=do_login).pack(side=tkinter.LEFT, padx=5)
    tkinter.Button(btn_frame, text='退出', width=12, height=2,
                   command=root.destroy).pack(side=tkinter.RIGHT, padx=5)

    entry_user.focus_set()
    root.mainloop()


if __name__ == '__main__':
    run()
