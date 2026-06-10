"""
Sakila DVD 租赁管理系统 — 租赁处理模块
"""
import tkinter
import tkinter.ttk
from tkinter.ttk import Treeview
from tkinter.messagebox import showerror, showinfo, askyesno

from db import doSql, querySql

selected_customer_id = None
selected_inventory_id = None
selected_rental_id = None


def create_rental_frame(parent, staff_info=None):
    global selected_customer_id, selected_inventory_id, selected_rental_id

    if staff_info is None:
        staff_info = {'id': 1, 'store_id': 1}

    frame = tkinter.Frame(parent)

    # ======== 区域1: 客户选择 ========
    cust_frame = tkinter.LabelFrame(frame, text='选择客户')
    cust_frame.place(x=10, y=5, width=450, height=280)

    tkinter.Label(cust_frame, text='搜索(姓名/邮箱)：').place(x=5, y=5, width=120, height=25)
    entry_cust_search = tkinter.Entry(cust_frame)
    entry_cust_search.place(x=125, y=5, width=200, height=25)
    entry_cust_search.bind('<Return>', lambda e: search_customers())

    def search_customers():
        kw = entry_cust_search.get().strip()
        if not kw:
            rows = querySql(
                'SELECT customer_id, CONCAT(first_name, " ", last_name), email '
                'FROM customer ORDER BY customer_id LIMIT 100')
        else:
            rows = querySql(
                f'SELECT customer_id, CONCAT(first_name, " ", last_name), email '
                f'FROM customer WHERE first_name LIKE "%{kw}%" OR last_name LIKE "%{kw}%" '
                f'OR email LIKE "%{kw}%" ORDER BY customer_id LIMIT 100')
        for r in cust_tree.get_children():
            cust_tree.delete(r)
        for item in rows:
            cust_tree.insert('', tkinter.END, values=item)

    cust_tree = Treeview(cust_frame,
                         columns=('cid', 'cname', 'cemail'),
                         show='headings', height=8)
    cust_tree.column('cid', width=60, anchor='center')
    cust_tree.column('cname', width=170, anchor='center')
    cust_tree.column('cemail', width=200, anchor='center')
    cust_tree.heading('cid', text='ID')
    cust_tree.heading('cname', text='客户名')
    cust_tree.heading('cemail', text='邮箱')
    cust_tree.place(x=5, y=35, width=435, height=210)

    def cust_click(event):
        global selected_customer_id
        if not cust_tree.selection():
            return
        item = cust_tree.selection()[0]
        vals = cust_tree.item(item, 'values')
        selected_customer_id = int(vals[0])
        lbl_cust.config(text=f'已选客户: {vals[1]}')

    cust_tree.bind('<ButtonRelease-1>', cust_click)

    lbl_cust = tkinter.Label(cust_frame, text='已选客户: (未选择)', fg='gray')
    lbl_cust.place(x=5, y=252)

    # ======== 区域2: 可用拷贝 (租出) ========
    rent_frame = tkinter.LabelFrame(frame, text='租出操作 — 可用拷贝')
    rent_frame.place(x=470, y=5, width=480, height=280)

    inv_tree = Treeview(rent_frame,
                        columns=('iid', 'ftitle', 'rate'),
                        show='headings', height=7)
    inv_tree.column('iid', width=60, anchor='center')
    inv_tree.column('ftitle', width=300, anchor='center')
    inv_tree.column('rate', width=80, anchor='center')
    inv_tree.heading('iid', text='拷贝ID')
    inv_tree.heading('ftitle', text='影片名')
    inv_tree.heading('rate', text='日租金')
    inv_tree.place(x=5, y=5, width=465, height=190)

    def inv_click(event):
        global selected_inventory_id
        if not inv_tree.selection():
            return
        item = inv_tree.selection()[0]
        vals = inv_tree.item(item, 'values')
        selected_inventory_id = int(vals[0])

    inv_tree.bind('<ButtonRelease-1>', inv_click)

    def load_available():
        for r in inv_tree.get_children():
            inv_tree.delete(r)
        store_id = staff_info.get('store_id', 1)
        rows = querySql(
            f'SELECT i.inventory_id, f.title, f.rental_rate '
            f'FROM inventory i '
            f'JOIN film f ON i.film_id=f.film_id '
            f'WHERE i.store_id={store_id} '
            f'AND i.inventory_id NOT IN ('
            f'  SELECT inventory_id FROM rental WHERE return_date IS NULL'
            f') '
            f'ORDER BY f.title')
        for item in rows:
            inv_tree.insert('', tkinter.END, values=item)

    tkinter.Button(rent_frame, text='刷新可用拷贝', command=load_available).place(x=5, y=200)

    def rent_out():
        global selected_customer_id, selected_inventory_id
        if selected_customer_id is None:
            showerror(title='很抱歉', message='请先选择客户')
            return
        if selected_inventory_id is None:
            showerror(title='很抱歉', message='请先选择要租出的拷贝')
            return

        # 获取 rental_id
        max_id = querySql('SELECT MAX(rental_id) FROM rental')[0][0] or 0
        new_rental_id = max_id + 1

        # 获取影片租金
        rows = querySql(
            f'SELECT f.rental_rate FROM film f '
            f'JOIN inventory i ON f.film_id=i.film_id '
            f'WHERE i.inventory_id={selected_inventory_id}')
        amount = rows[0][0] if rows else 4.99

        staff_id = staff_info.get('id', 1)

        # 创建 rental 记录
        doSql(
            f'INSERT INTO rental(rental_id, rental_date, inventory_id, customer_id, staff_id) '
            f'VALUES({new_rental_id}, NOW(), {selected_inventory_id}, '
            f'{selected_customer_id}, {staff_id})')

        # 获取 payment_id
        max_pay = querySql('SELECT MAX(payment_id) FROM payment')[0][0] or 0
        new_pay_id = max_pay + 1

        # 创建 payment 记录
        doSql(
            f'INSERT INTO payment(payment_id, customer_id, staff_id, rental_id, amount, payment_date) '
            f'VALUES({new_pay_id}, {selected_customer_id}, {staff_id}, '
            f'{new_rental_id}, {amount}, NOW())')

        showinfo('恭喜', f'租赁成功！租赁ID: {new_rental_id}')
        selected_inventory_id = None
        load_available()
        load_rented()

    tkinter.Button(rent_frame, text='确认租出', width=12, height=2,
                   command=rent_out).place(x=350, y=195)

    # ======== 区域3: 当前在借 (归还) ========
    return_frame = tkinter.LabelFrame(frame, text='归还操作 — 当前在借记录')
    return_frame.place(x=10, y=295, width=940, height=370)

    return_tree = Treeview(return_frame,
                           columns=('rid', 'cname', 'ftitle', 'iid', 'rdate', 'days'),
                           show='headings', height=12)
    return_tree.column('rid', width=60, anchor='center')
    return_tree.column('cname', width=150, anchor='center')
    return_tree.column('ftitle', width=300, anchor='center')
    return_tree.column('iid', width=60, anchor='center')
    return_tree.column('rdate', width=150, anchor='center')
    return_tree.column('days', width=70, anchor='center')
    return_tree.heading('rid', text='租赁ID')
    return_tree.heading('cname', text='客户')
    return_tree.heading('ftitle', text='影片')
    return_tree.heading('iid', text='拷贝ID')
    return_tree.heading('rdate', text='租出日期')
    return_tree.heading('days', text='已租天数')
    return_tree.place(x=5, y=5, width=925, height=300)

    def return_click(event):
        global selected_rental_id
        if not return_tree.selection():
            return
        item = return_tree.selection()[0]
        vals = return_tree.item(item, 'values')
        selected_rental_id = int(vals[0])

    return_tree.bind('<ButtonRelease-1>', return_click)

    def load_rented():
        for r in return_tree.get_children():
            return_tree.delete(r)
        store_id = staff_info.get('store_id', 1)
        rows = querySql(
            f'SELECT r.rental_id, '
            f'CONCAT(c.first_name, " ", c.last_name), '
            f'f.title, r.inventory_id, r.rental_date, '
            f'DATEDIFF(NOW(), r.rental_date) '
            f'FROM rental r '
            f'JOIN inventory i ON r.inventory_id=i.inventory_id '
            f'JOIN film f ON i.film_id=f.film_id '
            f'JOIN customer c ON r.customer_id=c.customer_id '
            f'WHERE r.return_date IS NULL AND i.store_id={store_id} '
            f'ORDER BY r.rental_date')
        for item in rows:
            return_tree.insert('', tkinter.END, values=item)

    def return_item():
        global selected_rental_id
        if selected_rental_id is None:
            showerror(title='很抱歉', message='请先选择要归还的租赁记录')
            return
        if askyesno('请确认', f'确定要归还租赁 #{selected_rental_id} 吗？') == tkinter.YES:
            doSql(f'UPDATE rental SET return_date=NOW() WHERE rental_id={selected_rental_id}')
            showinfo('恭喜', '归还成功')
            selected_rental_id = None
            load_rented()
            load_available()

    tkinter.Button(return_frame, text='刷新', command=load_rented).place(x=5, y=315)
    tkinter.Button(return_frame, text='确认归还', width=12, height=2,
                   command=return_item).place(x=800, y=312)

    # 初始化
    search_customers()
    load_available()
    load_rented()

    return frame
