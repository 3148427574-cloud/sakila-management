"""
Sakila DVD 租赁管理系统 — 客户管理模块
"""
import tkinter
import tkinter.ttk
from tkinter.ttk import Treeview
from tkinter.messagebox import showerror, showinfo, askyesno

from db import doSql, querySql

selected_customer_id = None


def load_countries(combo):
    rows = querySql('SELECT country_id, country FROM country ORDER BY country')
    combo['values'] = [f'{r[0]}|{r[1]}' for r in rows]
    combo._map = {f'{r[0]}|{r[1]}': r[0] for r in rows}


def load_cities(combo, country_id):
    rows = querySql(f'SELECT city_id, city FROM city WHERE country_id={country_id} ORDER BY city')
    combo['values'] = [f'{r[0]}|{r[1]}' for r in rows]
    combo._map = {f'{r[0]}|{r[1]}': r[0] for r in rows}


def load_addresses(combo, city_id):
    rows = querySql(f'SELECT address_id, address FROM address WHERE city_id={city_id} ORDER BY address')
    combo['values'] = [f'{r[0]}|{r[1]}' for r in rows]
    combo._map = {f'{r[0]}|{r[1]}': r[0] for r in rows}


def get_combo_id(combo):
    text = combo.get()
    if not text:
        return None
    m = getattr(combo, '_map', {})
    return m.get(text)


def create_customer_frame(parent):
    global selected_customer_id
    frame = tkinter.Frame(parent)

    # --- 表单 ---
    tkinter.Label(frame, text='名：').place(x=10, y=10, width=40, height=25)
    entry_first = tkinter.Entry(frame)
    entry_first.place(x=50, y=10, width=130, height=25)

    tkinter.Label(frame, text='姓：').place(x=190, y=10, width=40, height=25)
    entry_last = tkinter.Entry(frame)
    entry_last.place(x=230, y=10, width=130, height=25)

    tkinter.Label(frame, text='邮箱：').place(x=370, y=10, width=40, height=25)
    entry_email = tkinter.Entry(frame)
    entry_email.place(x=410, y=10, width=200, height=25)

    tkinter.Label(frame, text='门店：').place(x=620, y=10, width=40, height=25)
    combo_store = tkinter.ttk.Combobox(frame, state='readonly', values=['1', '2'])
    combo_store.place(x=660, y=10, width=60, height=25)

    tkinter.Label(frame, text='活跃：').place(x=730, y=10, width=40, height=25)
    combo_active = tkinter.ttk.Combobox(frame, state='readonly', values=['是', '否'])
    combo_active.place(x=770, y=10, width=60, height=25)

    # 地址联动
    tkinter.Label(frame, text='国家：').place(x=10, y=45, width=40, height=25)
    combo_country = tkinter.ttk.Combobox(frame, state='readonly')
    combo_country.place(x=50, y=45, width=180, height=25)
    combo_country.bind('<<ComboboxSelected>>',
                       lambda e: load_cities(combo_city, get_combo_id(combo_country)))

    tkinter.Label(frame, text='城市：').place(x=240, y=45, width=40, height=25)
    combo_city = tkinter.ttk.Combobox(frame, state='readonly')
    combo_city.place(x=280, y=45, width=180, height=25)
    combo_city.bind('<<ComboboxSelected>>',
                    lambda e: load_addresses(combo_address, get_combo_id(combo_city)))

    tkinter.Label(frame, text='地址：').place(x=470, y=45, width=40, height=25)
    combo_address = tkinter.ttk.Combobox(frame, state='readonly')
    combo_address.place(x=510, y=45, width=250, height=25)

    # --- 表格 ---
    table_frame = tkinter.Frame(frame)
    table_frame.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True, padx=5, pady=5)

    scrollbar = tkinter.Scrollbar(table_frame)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    tree = Treeview(table_frame,
                    columns=('id', 'name', 'email', 'addr', 'city', 'country', 'store', 'active'),
                    show='headings', yscrollcommand=scrollbar.set)
    tree.column('id', width=50, anchor='center')
    tree.column('name', width=130, anchor='center')
    tree.column('email', width=180, anchor='center')
    tree.column('addr', width=180, anchor='center')
    tree.column('city', width=120, anchor='center')
    tree.column('country', width=100, anchor='center')
    tree.column('store', width=50, anchor='center')
    tree.column('active', width=50, anchor='center')
    tree.heading('id', text='ID')
    tree.heading('name', text='姓名')
    tree.heading('email', text='邮箱')
    tree.heading('addr', text='地址')
    tree.heading('city', text='城市')
    tree.heading('country', text='国家')
    tree.heading('store', text='门店')
    tree.heading('active', text='活跃')
    tree.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
    scrollbar.config(command=tree.yview)

    def bind_data(rows=None):
        for row in tree.get_children():
            tree.delete(row)
        if rows is None:
            rows = querySql(
                'SELECT c.customer_id, c.first_name, c.last_name, c.email, '
                'a.address, ci.city, co.country, c.store_id, c.active '
                'FROM customer c '
                'JOIN address a ON c.address_id=a.address_id '
                'JOIN city ci ON a.city_id=ci.city_id '
                'JOIN country co ON ci.country_id=co.country_id '
                'ORDER BY c.customer_id')
        for i, item in enumerate(rows):
            formatted = list(item)
            formatted[1] = f'{item[1]} {item[2]}'  # full name
            formatted[8] = '是' if item[8] else '否'
            tree.insert('', i, values=formatted)

    def tree_click(event):
        global selected_customer_id
        if not tree.selection():
            return
        item = tree.selection()[0]
        vals = tree.item(item, 'values')
        selected_customer_id = int(vals[0])

        entry_first.delete(0, tkinter.END)
        entry_last.delete(0, tkinter.END)
        entry_email.delete(0, tkinter.END)
        combo_store.set('')
        combo_active.set('')

        row = querySql(
            f'SELECT c.first_name, c.last_name, c.email, c.store_id, c.active, '
            f'a.address_id, a.address, ci.city_id, ci.city, co.country_id, co.country '
            f'FROM customer c '
            f'JOIN address a ON c.address_id=a.address_id '
            f'JOIN city ci ON a.city_id=ci.city_id '
            f'JOIN country co ON ci.country_id=co.country_id '
            f'WHERE c.customer_id={selected_customer_id}')
        if not row:
            return
        r = row[0]
        entry_first.insert(0, r[0])
        entry_last.insert(0, r[1])
        entry_email.insert(0, r[2] if r[2] else '')
        combo_store.set(str(r[3]))

        # Set country
        country_display = f'{r[9]}|{r[10]}'
        if country_display in (combo_country._map or {}):
            combo_country.set(country_display)
            load_cities(combo_city, r[9])
            city_display = f'{r[7]}|{r[8]}'
            if city_display in (combo_city._map or {}):
                combo_city.set(city_display)
                load_addresses(combo_address, r[7])
                addr_display = f'{r[5]}|{r[6]}'
                if addr_display in (combo_address._map or {}):
                    combo_address.set(addr_display)

        combo_active.set('是' if r[4] else '否')

    tree.bind('<ButtonRelease-1>', tree_click)

    def clear_form():
        global selected_customer_id
        selected_customer_id = None
        entry_first.delete(0, tkinter.END)
        entry_last.delete(0, tkinter.END)
        entry_email.delete(0, tkinter.END)
        combo_store.set('')
        combo_active.set('')
        combo_country.set('')
        combo_city.set('')
        combo_address.set('')

    def query_click():
        conditions = []
        fn = entry_first.get().strip()
        if fn:
            conditions.append(f'c.first_name LIKE "%{fn}%"')
        ln = entry_last.get().strip()
        if ln:
            conditions.append(f'c.last_name LIKE "%{ln}%"')
        email = entry_email.get().strip()
        if email:
            conditions.append(f'c.email LIKE "%{email}%"')
        store = combo_store.get()
        if store:
            conditions.append(f'c.store_id={store}')
        active = combo_active.get()
        if active:
            conditions.append(f'c.active={1 if active == "是" else 0}')

        base = ('SELECT c.customer_id, c.first_name, c.last_name, c.email, '
                'a.address, ci.city, co.country, c.store_id, c.active '
                'FROM customer c '
                'JOIN address a ON c.address_id=a.address_id '
                'JOIN city ci ON a.city_id=ci.city_id '
                'JOIN country co ON ci.country_id=co.country_id')
        if conditions:
            sql = base + ' WHERE ' + ' AND '.join(conditions) + ' ORDER BY c.customer_id'
        else:
            sql = base + ' ORDER BY c.customer_id'
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
        email = entry_email.get().strip()
        store = combo_store.get()
        if not store:
            showerror(title='很抱歉', message='必须选择门店')
            return
        active_val = '1' if combo_active.get() == '是' else '0'
        addr_id = get_combo_id(combo_address)
        if not addr_id:
            showerror(title='很抱歉', message='必须选择地址')
            return

        sql = (f'INSERT INTO customer(first_name, last_name, email, address_id, '
               f'store_id, active, create_date) '
               f'VALUES("{fn}", "{ln}", "{email}", {addr_id}, '
               f'{store}, {active_val}, NOW())')
        doSql(sql)
        showinfo('恭喜', '客户添加成功')
        clear_form()
        bind_data()

    def edit_click():
        global selected_customer_id
        if selected_customer_id is None:
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
        email = entry_email.get().strip()
        store = combo_store.get()
        if not store:
            showerror(title='很抱歉', message='必须选择门店')
            return
        active_val = '1' if combo_active.get() == '是' else '0'
        addr_id = get_combo_id(combo_address)
        if not addr_id:
            showerror(title='很抱歉', message='必须选择地址')
            return

        sql = (f'UPDATE customer SET first_name="{fn}", last_name="{ln}", '
               f'email="{email}", address_id={addr_id}, store_id={store}, '
               f'active={active_val} WHERE customer_id={selected_customer_id}')
        doSql(sql)
        showinfo('恭喜', '客户修改成功')
        clear_form()
        bind_data()

    def delete_click():
        global selected_customer_id
        if selected_customer_id is None:
            showerror(title='很抱歉', message='请先在表格中选择一条记录')
            return
        # 检查未归还租赁
        rentals = querySql(
            f'SELECT COUNT(*) FROM rental '
            f'WHERE customer_id={selected_customer_id} AND return_date IS NULL')
        if rentals and rentals[0][0] > 0:
            showerror(title='很抱歉', message='该客户有未归还的租赁记录，无法删除')
            return
        name = f'{entry_first.get()} {entry_last.get()}'
        if askyesno('请确认', f'确定要删除客户"{name}"吗？') == tkinter.YES:
            doSql(f'DELETE FROM customer WHERE customer_id={selected_customer_id}')
            showinfo('恭喜', '客户删除成功')
            clear_form()
            bind_data()

    button_query = tkinter.Button(frame, text='查询', command=query_click)
    button_query.place(x=70, y=85, width=80, height=28)
    button_add = tkinter.Button(frame, text='添加', command=add_click)
    button_add.place(x=180, y=85, width=80, height=28)
    button_edit = tkinter.Button(frame, text='修改', command=edit_click)
    button_edit.place(x=290, y=85, width=80, height=28)
    button_delete = tkinter.Button(frame, text='删除', command=delete_click)
    button_delete.place(x=400, y=85, width=80, height=28)

    # 初始化数据
    load_countries(combo_country)
    bind_data()

    return frame
