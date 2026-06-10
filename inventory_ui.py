"""
Sakila DVD 租赁管理系统 — 库存管理模块
"""
import tkinter
import tkinter.ttk
from tkinter.ttk import Treeview
from tkinter.messagebox import showerror, showinfo, askyesno

from db import doSql, querySql

selected_inventory_id = None


def create_inventory_frame(parent, staff_info=None):
    global selected_inventory_id
    frame = tkinter.Frame(parent)

    # --- 查询/添加区 ---
    tkinter.Label(frame, text='影片：').place(x=10, y=10, width=40, height=25)
    combo_film = tkinter.ttk.Combobox(frame, state='readonly')
    combo_film.place(x=50, y=10, width=280, height=25)

    tkinter.Label(frame, text='门店：').place(x=340, y=10, width=40, height=25)
    combo_store = tkinter.ttk.Combobox(frame, state='readonly', values=['1', '2'])
    combo_store.place(x=380, y=10, width=60, height=25)

    # --- 表格 ---
    table_frame = tkinter.Frame(frame)
    table_frame.place(x=10, y=90, width=940, height=580)

    scrollbar = tkinter.Scrollbar(table_frame)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    tree = Treeview(table_frame,
                    columns=('id', 'film', 'store', 'status'),
                    show='headings', yscrollcommand=scrollbar.set)
    tree.column('id', width=70, anchor='center')
    tree.column('film', width=380, anchor='center')
    tree.column('store', width=70, anchor='center')
    tree.column('status', width=80, anchor='center')
    tree.heading('id', text='拷贝ID')
    tree.heading('film', text='影片名')
    tree.heading('store', text='门店')
    tree.heading('status', text='状态')
    tree.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
    scrollbar.config(command=tree.yview)

    def _get_combo_id(combo):
        text = combo.get()
        if not text:
            return None
        m = getattr(combo, '_map', {})
        return m.get(text)

    def bind_data(rows=None):
        for row in tree.get_children():
            tree.delete(row)
        if rows is None:
            rows = querySql(
                'SELECT i.inventory_id, f.title, i.store_id, '
                'CASE WHEN r.rental_id IS NULL THEN "在馆" ELSE "已租出" END '
                'FROM inventory i '
                'JOIN film f ON i.film_id=f.film_id '
                'LEFT JOIN rental r ON i.inventory_id=r.inventory_id AND r.return_date IS NULL '
                'ORDER BY i.inventory_id')
        for i, item in enumerate(rows):
            tree.insert('', i, values=item)

    def tree_click(event):
        global selected_inventory_id
        if not tree.selection():
            return
        item = tree.selection()[0]
        vals = tree.item(item, 'values')
        selected_inventory_id = int(vals[0])

    tree.bind('<ButtonRelease-1>', tree_click)

    def query_click():
        conditions = []
        film_id = _get_combo_id(combo_film)
        if film_id:
            conditions.append(f'i.film_id={film_id}')
        store = combo_store.get()
        if store:
            conditions.append(f'i.store_id={store}')

        base = ('SELECT i.inventory_id, f.title, i.store_id, '
                'CASE WHEN r.rental_id IS NULL THEN "在馆" ELSE "已租出" END '
                'FROM inventory i '
                'JOIN film f ON i.film_id=f.film_id '
                'LEFT JOIN rental r ON i.inventory_id=r.inventory_id AND r.return_date IS NULL')
        if conditions:
            sql = base + ' WHERE ' + ' AND '.join(conditions) + ' ORDER BY i.inventory_id'
        else:
            sql = base + ' ORDER BY i.inventory_id'
        bind_data(querySql(sql))

    def add_click():
        film_id = _get_combo_id(combo_film)
        if not film_id:
            showerror(title='很抱歉', message='必须选择影片')
            return
        store = combo_store.get()
        if not store:
            showerror(title='很抱歉', message='必须选择门店')
            return
        doSql(f'INSERT INTO inventory(film_id, store_id) VALUES({film_id}, {store})')
        showinfo('恭喜', '拷贝添加成功')
        bind_data()

    def delete_click():
        global selected_inventory_id
        if selected_inventory_id is None:
            showerror(title='很抱歉', message='请先在表格中选择一条记录')
            return
        status = None
        for item in tree.selection():
            vals = tree.item(item, 'values')
            status = vals[3]
        if status == '已租出':
            showerror(title='很抱歉', message='该拷贝正在租出中，无法删除')
            return
        if askyesno('请确认', f'确定要删除拷贝 #{selected_inventory_id} 吗？') == tkinter.YES:
            # 删除关联的 rental 和 payment 记录
            rentals = querySql(
                f'SELECT rental_id FROM rental WHERE inventory_id={selected_inventory_id}')
            for r in rentals:
                doSql(f'DELETE FROM payment WHERE rental_id={r[0]}')
                doSql(f'DELETE FROM rental WHERE rental_id={r[0]}')
            doSql(f'DELETE FROM inventory WHERE inventory_id={selected_inventory_id}')
            showinfo('恭喜', '拷贝删除成功')
            selected_inventory_id = None
            bind_data()

    button_query = tkinter.Button(frame, text='查询', command=query_click)
    button_query.place(x=70, y=50, width=80, height=28)
    button_add = tkinter.Button(frame, text='新增拷贝', command=add_click)
    button_add.place(x=180, y=50, width=80, height=28)
    button_delete = tkinter.Button(frame, text='删除', command=delete_click)
    button_delete.place(x=290, y=50, width=80, height=28)

    # 初始化
    film_rows = querySql('SELECT film_id, title FROM film ORDER BY title')
    combo_film['values'] = [f'{r[0]}|{r[1]}' for r in film_rows]
    combo_film._map = {f'{r[0]}|{r[1]}': r[0] for r in film_rows}

    bind_data()
    return frame
