"""
Sakila DVD 租赁管理系统 — 主入口
"""
import hashlib
import tkinter
import tkinter.ttk
from tkinter.ttk import Notebook
from tkinter.messagebox import showerror, showinfo

from db import querySql, doSql
import film_ui
import actor_ui
import customer_ui
import rental_ui
import inventory_ui


def run():
    root = tkinter.Tk()
    root.title('Sakila DVD 租赁管理系统 — 登录')
    root.geometry('420x330+500+300')
    root.resizable(False, False)

    staff_info = {}

    def clear_root():
        for w in root.winfo_children():
            w.destroy()

    # ============ 登录页 ============
    def show_login():
        clear_root()
        root.geometry('420x330+500+300')
        root.title('Sakila DVD 租赁管理系统 — 登录')
        root.resizable(False, False)

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
        entry_pass.bind('<Return>', lambda e: do_login(entry_user, entry_pass))

        btn_frame = tkinter.Frame(frame)
        btn_frame.pack(fill='x')

        tkinter.Button(btn_frame, text='登录', width=10, height=2,
                       command=lambda: do_login(entry_user, entry_pass)
                       ).pack(side=tkinter.LEFT, padx=3)
        tkinter.Button(btn_frame, text='注册', width=10, height=2,
                       command=show_register).pack(side=tkinter.LEFT, padx=3)
        tkinter.Button(btn_frame, text='退出', width=10, height=2,
                       command=root.destroy).pack(side=tkinter.RIGHT, padx=3)

        entry_user.focus_set()

    # ============ 注册页 ============
    def show_register():
        clear_root()
        root.geometry('420x470+500+200')
        root.title('Sakila DVD 租赁管理系统 — 注册')
        root.resizable(False, False)

        frame = tkinter.Frame(root)
        frame.pack(expand=True, fill=tkinter.BOTH, padx=30, pady=15)

        tkinter.Label(frame, text='员工注册',
                      font=('Arial', 14, 'bold')).pack(pady=(5, 10))

        fields = {}
        for label, key in [('用户名：', 'username'), ('密码：', 'password'),
                           ('确认密码：', 'confirm'), ('名：', 'first_name'),
                           ('姓：', 'last_name'), ('邮箱：', 'email')]:
            tkinter.Label(frame, text=label).pack(anchor='w')
            show = '*' if 'assword' in label else ''
            ent = tkinter.Entry(frame, font=('Arial', 11), show=show)
            ent.pack(fill='x', pady=(1, 6))
            fields[key] = ent

        tkinter.Label(frame, text='门店：').pack(anchor='w')
        combo_store = tkinter.ttk.Combobox(frame, state='readonly', values=['1', '2'])
        combo_store.pack(fill='x', pady=(1, 8))
        combo_store.set('1')

        def do_register():
            vals = {k: e.get().strip() for k, e in fields.items()}
            store = combo_store.get()

            # 验证
            if not vals['username']:
                showerror(title='注册失败', message='用户名不能为空')
                return
            if not vals['password']:
                showerror(title='注册失败', message='密码不能为空')
                return
            if vals['password'] != vals['confirm']:
                showerror(title='注册失败', message='两次密码不一致')
                return
            if not vals['first_name']:
                showerror(title='注册失败', message='名不能为空')
                return
            if not vals['last_name']:
                showerror(title='注册失败', message='姓不能为空')
                return
            if not vals['email']:
                showerror(title='注册失败', message='邮箱不能为空')
                return

            # 检查用户名是否已存在
            exist = querySql(
                f'SELECT 1 FROM staff WHERE username="{vals["username"]}"')
            if exist:
                showerror(title='注册失败', message='用户名已被占用')
                return

            pw_hash = hashlib.sha1(vals['password'].encode()).hexdigest()
            max_id = querySql('SELECT MAX(staff_id) FROM staff')[0][0] or 0
            new_id = max_id + 1

            doSql(
                f'INSERT INTO staff(staff_id, first_name, last_name, email, '
                f'username, password, store_id, active) '
                f'VALUES({new_id}, "{vals["first_name"]}", "{vals["last_name"]}", '
                f'"{vals["email"]}", "{vals["username"]}", "{pw_hash}", {store}, 1)')
            showinfo('注册成功', f'员工 {vals["first_name"]} {vals["last_name"]} 注册成功，请登录')
            show_login()

        btn_frame = tkinter.Frame(frame)
        btn_frame.pack(fill='x', pady=(5, 0))
        tkinter.Button(btn_frame, text='注册', width=10, height=2,
                       command=do_register).pack(side=tkinter.LEFT)
        tkinter.Button(btn_frame, text='返回', width=10, height=2,
                       command=show_login).pack(side=tkinter.RIGHT)

        fields['username'].focus_set()

    # ============ 登录逻辑 ============
    def do_login(entry_user, entry_pass):
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
            f'FROM staff WHERE username="{username}" AND active=1 AND {pw_sql}'
        )
        if not rows:
            showerror(title='登录失败', message='用户名或密码错误，或账号已停用')
            return

        staff_info['id'] = rows[0][0]
        staff_info['first_name'] = rows[0][1]
        staff_info['last_name'] = rows[0][2]
        staff_info['email'] = rows[0][3]
        staff_info['store_id'] = rows[0][4]

        showinfo('登录成功',
                 f'欢迎 {staff_info["first_name"]} {staff_info["last_name"]} 登录系统')
        show_main()

    # ============ 主界面 ============
    def show_main():
        clear_root()
        root.geometry('980x770+250+40')
        root.title(f'Sakila DVD 租赁管理系统 — '
                   f'{staff_info["first_name"]} {staff_info["last_name"]}')
        root.resizable(True, True)

        status_var = tkinter.StringVar(
            value=f'已登录: {staff_info["first_name"]} '
                  f'{staff_info["last_name"]} (门店 {staff_info["store_id"]})')
        status_bar = tkinter.Label(root, textvariable=status_var,
                                   anchor='w', relief=tkinter.SUNKEN, bg='#f0f0f0')
        status_bar.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        notebook = Notebook(root)
        notebook.pack(fill=tkinter.BOTH, expand=True, padx=5, pady=5)

        notebook.add(rental_ui.create_rental_frame(notebook, staff_info), text='租赁处理')
        notebook.add(customer_ui.create_customer_frame(notebook), text='客户管理')
        notebook.add(inventory_ui.create_inventory_frame(notebook, staff_info), text='库存管理')
        notebook.add(film_ui.create_film_frame(notebook), text='电影管理')
        notebook.add(actor_ui.create_actor_frame(notebook), text='演员管理')

    show_login()
    root.mainloop()


if __name__ == '__main__':
    run()
