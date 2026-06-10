"""
Sakila DVD 租赁管理系统 — 演员管理模块
"""
import tkinter
import tkinter.ttk
from tkinter.ttk import Treeview
from tkinter.messagebox import showerror, showinfo, askyesno

from db import doSql, querySql

selected_actor_id = None


def create_actor_frame(parent):
    global selected_actor_id
    frame = tkinter.Frame(parent)

    # --- 表单 ---
    tkinter.Label(frame, text='名：').place(x=10, y=10, width=40, height=25)
    entry_first = tkinter.Entry(frame)
    entry_first.place(x=50, y=10, width=160, height=25)

    tkinter.Label(frame, text='姓：').place(x=220, y=10, width=40, height=25)
    entry_last = tkinter.Entry(frame)
    entry_last.place(x=260, y=10, width=160, height=25)

    # --- 演员表格 ---
    bottom_frame = tkinter.Frame(frame)
    bottom_frame.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True, padx=5, pady=5)

    table_frame = tkinter.Frame(bottom_frame)
    table_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=(0, 3))

    scrollbar = tkinter.Scrollbar(table_frame)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    tree = Treeview(table_frame,
                    columns=('id', 'first', 'last'),
                    show='headings', yscrollcommand=scrollbar.set)
    tree.column('id', width=60, anchor='center')
    tree.column('first', width=150, anchor='center')
    tree.column('last', width=150, anchor='center')
    tree.heading('id', text='ID')
    tree.heading('first', text='名')
    tree.heading('last', text='姓')
    tree.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
    scrollbar.config(command=tree.yview)

    # --- 参演作品区 ---
    film_label = tkinter.LabelFrame(bottom_frame, text='参演作品')
    film_label.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=True, padx=(3, 0))

    film_tree = Treeview(film_label,
                         columns=('fid', 'ftitle', 'fyear', 'frating'),
                         show='headings', height=24)
    film_tree.column('fid', width=50, anchor='center')
    film_tree.column('ftitle', width=220, anchor='center')
    film_tree.column('fyear', width=60, anchor='center')
    film_tree.column('frating', width=60, anchor='center')
    film_tree.heading('fid', text='ID')
    film_tree.heading('ftitle', text='片名')
    film_tree.heading('fyear', text='年份')
    film_tree.heading('frating', text='分级')
    film_tree.pack(fill=tkinter.BOTH, expand=True, padx=3, pady=3)

    def bind_data(rows=None):
        for row in tree.get_children():
            tree.delete(row)
        if rows is None:
            rows = querySql('SELECT actor_id, first_name, last_name FROM actor ORDER BY actor_id')
        for i, item in enumerate(rows):
            tree.insert('', i, values=item)

    def load_actor_films(actor_id):
        for row in film_tree.get_children():
            film_tree.delete(row)
        rows = querySql(
            f'SELECT f.film_id, f.title, f.release_year, f.rating '
            f'FROM film f JOIN film_actor fa ON f.film_id=fa.film_id '
            f'WHERE fa.actor_id={actor_id} ORDER BY f.title')
        for item in rows:
            film_tree.insert('', tkinter.END, values=item)

    def tree_click(event):
        global selected_actor_id
        if not tree.selection():
            return
        item = tree.selection()[0]
        vals = tree.item(item, 'values')
        selected_actor_id = int(vals[0])
        entry_first.delete(0, tkinter.END)
        entry_first.insert(0, vals[1])
        entry_last.delete(0, tkinter.END)
        entry_last.insert(0, vals[2])
        load_actor_films(selected_actor_id)

    tree.bind('<ButtonRelease-1>', tree_click)

    def clear_form():
        global selected_actor_id
        selected_actor_id = None
        entry_first.delete(0, tkinter.END)
        entry_last.delete(0, tkinter.END)
        for row in film_tree.get_children():
            film_tree.delete(row)

    def query_click():
        conditions = []
        fn = entry_first.get().strip()
        if fn:
            conditions.append(f'first_name LIKE "%{fn}%"')
        ln = entry_last.get().strip()
        if ln:
            conditions.append(f'last_name LIKE "%{ln}%"')
        if conditions:
            sql = 'SELECT actor_id, first_name, last_name FROM actor WHERE ' + \
                  ' AND '.join(conditions) + ' ORDER BY actor_id'
        else:
            sql = 'SELECT actor_id, first_name, last_name FROM actor ORDER BY actor_id'
        bind_data(querySql(sql))

    def add_click():
        fn = entry_first.get().strip()
        if not fn:
            showerror(title='很抱歉', message='必须输入名')
            return
        ln = entry_last.get().strip()
        if not ln:
            showerror(title='很抱歉', message='必须输入姓')
            return
        doSql(f'INSERT INTO actor(first_name, last_name) VALUES("{fn}", "{ln}")')
        showinfo('恭喜', '演员添加成功')
        clear_form()
        bind_data()

    def edit_click():
        global selected_actor_id
        if selected_actor_id is None:
            showerror(title='很抱歉', message='请先在表格中选择一条记录')
            return
        fn = entry_first.get().strip()
        if not fn:
            showerror(title='很抱歉', message='必须输入名')
            return
        ln = entry_last.get().strip()
        if not ln:
            showerror(title='很抱歉', message='必须输入姓')
            return
        doSql(f'UPDATE actor SET first_name="{fn}", last_name="{ln}" WHERE actor_id={selected_actor_id}')
        showinfo('恭喜', '演员修改成功')
        clear_form()
        bind_data()

    def delete_click():
        global selected_actor_id
        if selected_actor_id is None:
            showerror(title='很抱歉', message='请先在表格中选择一条记录')
            return
        films = querySql(f'SELECT COUNT(*) FROM film_actor WHERE actor_id={selected_actor_id}')
        name = f'{entry_first.get()} {entry_last.get()}'
        msg = f'确定要删除演员"{name}"吗？'
        if films and films[0][0] > 0:
            msg += f'\n\n该演员参演了{films[0][0]}部影片，关联将一并删除。'
        if askyesno('请确认', msg) == tkinter.YES:
            doSql(f'DELETE FROM film_actor WHERE actor_id={selected_actor_id}')
            doSql(f'DELETE FROM actor WHERE actor_id={selected_actor_id}')
            showinfo('恭喜', '演员删除成功')
            clear_form()
            bind_data()

    button_query = tkinter.Button(frame, text='查询', command=query_click)
    button_query.place(x=70, y=50, width=80, height=28)
    button_add = tkinter.Button(frame, text='添加', command=add_click)
    button_add.place(x=180, y=50, width=80, height=28)
    button_edit = tkinter.Button(frame, text='修改', command=edit_click)
    button_edit.place(x=290, y=50, width=80, height=28)
    button_delete = tkinter.Button(frame, text='删除', command=delete_click)
    button_delete.place(x=400, y=50, width=80, height=28)

    bind_data()
    return frame
