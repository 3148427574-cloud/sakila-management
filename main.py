"""
Sakila DVD 租赁管理系统 — 主入口
"""
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


class SakilaApp:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.withdraw()  # 先隐藏主窗口，显示登录
        self.staff_info = None
        self._show_login()

    def _show_login(self):
        self.login_win = tkinter.Toplevel(self.root)
        self.login_win.title('Sakila DVD 租赁管理系统 — 登录')
        self.login_win.geometry('400x280+500+300')
        self.login_win.resizable(False, False)
        self.login_win.protocol('WM_DELETE_WINDOW', self._on_close)

        frame = tkinter.Frame(self.login_win)
        frame.pack(expand=True, fill=tkinter.BOTH, padx=30, pady=20)

        tkinter.Label(frame, text='Sakila DVD 租赁管理系统',
                      font=('Arial', 16, 'bold')).pack(pady=(10, 20))

        tkinter.Label(frame, text='用户名：').pack(anchor='w')
        self.entry_user = tkinter.Entry(frame, font=('Arial', 12))
        self.entry_user.pack(fill='x', pady=(2, 10))

        tkinter.Label(frame, text='密码：').pack(anchor='w')
        self.entry_pass = tkinter.Entry(frame, show='*', font=('Arial', 12))
        self.entry_pass.pack(fill='x', pady=(2, 15))
        self.entry_pass.bind('<Return>', lambda e: self._do_login())

        btn_frame = tkinter.Frame(frame)
        btn_frame.pack(fill='x')

        tkinter.Button(btn_frame, text='登录', width=12, height=2,
                       command=self._do_login).pack(side=tkinter.LEFT, padx=5)
        tkinter.Button(btn_frame, text='退出', width=12, height=2,
                       command=self._on_close).pack(side=tkinter.RIGHT, padx=5)

        self.entry_user.focus_set()

    def _do_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username:
            showerror(title='登录失败', message='用户名不能为空')
            return
        if not password:
            showerror(title='登录失败', message='密码不能为空')
            return

        rows = querySql(
            f'SELECT staff_id, first_name, last_name, email, store_id '
            f'FROM staff WHERE username="{username}" AND password="{password}"'
        )
        if not rows:
            showerror(title='登录失败', message='用户名或密码错误')
            return

        self.staff_info = {
            'id': rows[0][0],
            'first_name': rows[0][1],
            'last_name': rows[0][2],
            'email': rows[0][3],
            'store_id': rows[0][4],
        }
        self.login_win.destroy()
        showinfo('登录成功',
                 f'欢迎 {self.staff_info["first_name"]} {self.staff_info["last_name"]} 登录系统')
        self._show_main()

    def _show_main(self):
        self.root.deiconify()
        self.root.geometry('980x720+250+50')
        self.root.title(f'Sakila DVD 租赁管理系统 — '
                        f'{self.staff_info["first_name"]} {self.staff_info["last_name"]}')
        self.root.protocol('WM_DELETE_WINDOW', self._on_close)

        # 状态栏
        self.status_var = tkinter.StringVar(
            value=f'已登录: {self.staff_info["first_name"]} '
                  f'{self.staff_info["last_name"]} (门店 {self.staff_info["store_id"]})')
        status_bar = tkinter.Label(self.root, textvariable=self.status_var,
                                   anchor='w', relief=tkinter.SUNKEN, bg='#f0f0f0')
        status_bar.place(x=0, y=695, width=980, height=25)

        # Notebook
        notebook = Notebook(self.root)
        notebook.place(x=5, y=5, width=970, height=685)

        # 注册各模块
        notebook.add(rental_ui.create_rental_frame(notebook, self.staff_info),
                     text='租赁处理')
        notebook.add(customer_ui.create_customer_frame(notebook), text='客户管理')
        notebook.add(inventory_ui.create_inventory_frame(notebook, self.staff_info),
                     text='库存管理')
        notebook.add(film_ui.create_film_frame(notebook), text='电影管理')
        notebook.add(actor_ui.create_actor_frame(notebook), text='演员管理')

    def _on_close(self):
        self.root.destroy()


if __name__ == '__main__':
    app = SakilaApp()
    app.root.mainloop()
