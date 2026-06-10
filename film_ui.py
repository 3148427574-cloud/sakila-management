"""
Sakila DVD 租赁管理系统 — 电影管理模块
"""
import tkinter
import tkinter.ttk
from tkinter.ttk import Treeview
from tkinter.messagebox import showerror, showinfo, askyesno

from db import doSql, querySql

selected_film_id = None


def create_film_frame(parent):
    global selected_film_id
    frame = tkinter.Frame(parent)

    # --- 表单第1行 ---
    tkinter.Label(frame, text='片名：').place(x=10, y=10, width=40, height=25)
    entry_title = tkinter.Entry(frame)
    entry_title.place(x=50, y=10, width=200, height=25)

    tkinter.Label(frame, text='发行年份：').place(x=260, y=10, width=65, height=25)
    entry_year = tkinter.Entry(frame)
    entry_year.place(x=325, y=10, width=70, height=25)

    tkinter.Label(frame, text='语言：').place(x=405, y=10, width=40, height=25)
    combo_lang = tkinter.ttk.Combobox(frame, state='readonly')
    combo_lang.place(x=445, y=10, width=130, height=25)

    tkinter.Label(frame, text='分级：').place(x=585, y=10, width=40, height=25)
    combo_rating = tkinter.ttk.Combobox(frame, state='readonly',
                                        values=['G', 'PG', 'PG-13', 'R', 'NC-17'])
    combo_rating.place(x=625, y=10, width=80, height=25)

    # --- 表单第2行 ---
    tkinter.Label(frame, text='租期(天)：').place(x=10, y=45, width=65, height=25)
    entry_dur = tkinter.Entry(frame)
    entry_dur.place(x=75, y=45, width=60, height=25)

    tkinter.Label(frame, text='日租金：').place(x=145, y=45, width=55, height=25)
    entry_rate = tkinter.Entry(frame)
    entry_rate.place(x=200, y=45, width=70, height=25)

    tkinter.Label(frame, text='片长(分)：').place(x=280, y=45, width=65, height=25)
    entry_len = tkinter.Entry(frame)
    entry_len.place(x=345, y=45, width=70, height=25)

    tkinter.Label(frame, text='替换成本：').place(x=425, y=45, width=65, height=25)
    entry_cost = tkinter.Entry(frame)
    entry_cost.place(x=490, y=45, width=80, height=25)

    # --- 简介 ---
    tkinter.Label(frame, text='简介：').place(x=10, y=80, width=40, height=25)
    text_desc = tkinter.Text(frame, height=3)
    text_desc.place(x=50, y=80, width=480, height=55)

    # --- 分类选择区 ---
    category_frame = tkinter.LabelFrame(frame, text='影片分类')
    category_frame.place(x=550, y=80, width=200, height=150)

    cat_vars = {}

    # --- 演员关联区 ---
    actor_frame = tkinter.LabelFrame(frame, text='参演演员')
    actor_frame.place(x=760, y=80, width=190, height=150)

    actor_tree = Treeview(actor_frame, columns=('aid', 'aname'), show='headings', height=4)
    actor_tree.column('aid', width=40, anchor='center')
    actor_tree.column('aname', width=130, anchor='center')
    actor_tree.heading('aid', text='ID')
    actor_tree.heading('aname', text='演员')
    actor_tree.place(x=5, y=20, width=180, height=90)

    combo_add_actor = tkinter.ttk.Combobox(actor_frame, state='readonly')
    combo_add_actor.place(x=5, y=115, width=120, height=25)

    def add_actor_link():
        if selected_film_id is None:
            return
        aid = _get_combo_id(combo_add_actor)
        if not aid:
            return
        existing = querySql(
            f'SELECT 1 FROM film_actor WHERE film_id={selected_film_id} AND actor_id={aid}')
        if existing:
            showerror(title='很抱歉', message='该演员已关联到此影片')
            return
        doSql(f'INSERT INTO film_actor(film_id, actor_id) VALUES({selected_film_id}, {aid})')
        load_film_actors(selected_film_id)

    def remove_actor_link():
        if not actor_tree.selection():
            return
        item = actor_tree.selection()[0]
        vals = actor_tree.item(item, 'values')
        aid = int(vals[0])
        aname = vals[1]
        if askyesno('请确认', f'确定要移除演员"{aname}"吗？') == tkinter.YES:
            doSql(f'DELETE FROM film_actor WHERE film_id={selected_film_id} AND actor_id={aid}')
            load_film_actors(selected_film_id)

    tkinter.Button(actor_frame, text='+', width=2,
                   command=add_actor_link).place(x=130, y=114, width=25, height=25)
    tkinter.Button(actor_frame, text='-', width=2,
                   command=remove_actor_link).place(x=160, y=114, width=25, height=25)

    # --- 表格 ---
    table_frame = tkinter.Frame(frame)
    table_frame.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True, padx=5, pady=5)

    scrollbar = tkinter.Scrollbar(table_frame)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    tree = Treeview(table_frame,
                    columns=('id', 'title', 'rating', 'length', 'rate', 'lang'),
                    show='headings', yscrollcommand=scrollbar.set)
    tree.column('id', width=50, anchor='center')
    tree.column('title', width=280, anchor='center')
    tree.column('rating', width=60, anchor='center')
    tree.column('length', width=70, anchor='center')
    tree.column('rate', width=70, anchor='center')
    tree.column('lang', width=100, anchor='center')
    tree.heading('id', text='ID')
    tree.heading('title', text='片名')
    tree.heading('rating', text='分级')
    tree.heading('length', text='片长')
    tree.heading('rate', text='日租金')
    tree.heading('lang', text='语言')
    tree.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
    scrollbar.config(command=tree.yview)

    def bind_data(rows=None):
        for row in tree.get_children():
            tree.delete(row)
        if rows is None:
            rows = querySql(
                'SELECT f.film_id, f.title, f.rating, f.length, f.rental_rate, l.name '
                'FROM film f LEFT JOIN language l ON f.language_id=l.language_id '
                'ORDER BY f.film_id')
        for i, item in enumerate(rows):
            tree.insert('', i, values=item)

    def clear_form():
        global selected_film_id
        selected_film_id = None
        entry_title.delete(0, tkinter.END)
        entry_year.delete(0, tkinter.END)
        combo_lang.set('')
        combo_rating.set('')
        entry_dur.delete(0, tkinter.END)
        entry_rate.delete(0, tkinter.END)
        entry_len.delete(0, tkinter.END)
        entry_cost.delete(0, tkinter.END)
        text_desc.delete('1.0', tkinter.END)
        for var in cat_vars.values():
            var.set(0)
        for row in actor_tree.get_children():
            actor_tree.delete(row)

    def load_film_actors(film_id):
        for row in actor_tree.get_children():
            actor_tree.delete(row)
        rows = querySql(
            f'SELECT a.actor_id, CONCAT(a.first_name, " ", a.last_name) '
            f'FROM actor a JOIN film_actor fa ON a.actor_id=fa.actor_id '
            f'WHERE fa.film_id={film_id} ORDER BY a.first_name')
        for item in rows:
            actor_tree.insert('', tkinter.END, values=item)

    def load_film_categories(film_id):
        rows = querySql(f'SELECT category_id FROM film_category WHERE film_id={film_id}')
        cat_ids = {r[0] for r in rows}
        for cid, var in cat_vars.items():
            var.set(1 if cid in cat_ids else 0)

    def tree_click(event):
        global selected_film_id
        if not tree.selection():
            return
        item = tree.selection()[0]
        vals = tree.item(item, 'values')
        selected_film_id = int(vals[0])

        clear_form()
        row = querySql(f'SELECT * FROM film WHERE film_id={selected_film_id}')
        if not row:
            return
        r = row[0]
        entry_title.insert(0, r[1] if r[1] else '')
        text_desc.insert('1.0', r[2] if r[2] else '')
        entry_year.insert(0, str(r[3]) if r[3] else '')
        entry_dur.insert(0, str(r[5]) if r[5] else '')
        entry_rate.insert(0, str(r[6]) if r[6] else '')
        entry_len.insert(0, str(r[7]) if r[7] else '')
        entry_cost.insert(0, str(r[8]) if r[8] else '')
        if r[9]:
            combo_rating.set(r[9])

        # Language
        lang_rows = querySql(f'SELECT name FROM language WHERE language_id={r[4]}')
        if lang_rows:
            combo_lang.set(lang_rows[0][0])

        load_film_categories(selected_film_id)
        load_film_actors(selected_film_id)

    tree.bind('<ButtonRelease-1>', tree_click)

    def _get_combo_id(combo):
        text = combo.get()
        if not text:
            return None
        m = getattr(combo, '_map', {})
        return m.get(text)

    def query_click():
        conditions = []
        title = entry_title.get().strip()
        if title:
            conditions.append(f'f.title LIKE "%{title}%"')
        rating = combo_rating.get()
        if rating:
            conditions.append(f'f.rating="{rating}"')
        lang = _get_combo_id(combo_lang)
        if lang:
            conditions.append(f'f.language_id={lang}')

        base = ('SELECT f.film_id, f.title, f.rating, f.length, f.rental_rate, l.name '
                'FROM film f LEFT JOIN language l ON f.language_id=l.language_id')
        if conditions:
            sql = base + ' WHERE ' + ' AND '.join(conditions) + ' ORDER BY f.film_id'
        else:
            sql = base + ' ORDER BY f.film_id'
        bind_data(querySql(sql))

    def add_click():
        title = entry_title.get().strip()
        if not title:
            showerror(title='很抱歉', message='必须输入片名')
            return
        lang_id = _get_combo_id(combo_lang) or 1
        year = entry_year.get().strip() or 'NULL'
        if year != 'NULL':
            year = int(year)
        dur = entry_dur.get().strip() or '3'
        rate = entry_rate.get().strip() or '4.99'
        length = entry_len.get().strip() or 'NULL'
        if length != 'NULL':
            length = int(length)
        cost = entry_cost.get().strip() or '19.99'
        rating = combo_rating.get() or 'PG'
        desc = text_desc.get('1.0', tkinter.END).strip().replace("'", "''")
        desc_val = f'"{desc}"' if desc else 'NULL'

        def val(v):
            if v == 'NULL':
                return 'NULL'
            elif isinstance(v, str):
                return f'"{v}"'
            return str(v)

        sql = (f'INSERT INTO film(title, description, release_year, language_id, '
               f'rental_duration, rental_rate, length, replacement_cost, rating) '
               f'VALUES("{title}", {desc_val}, {val(year)}, {lang_id}, '
               f'{val(dur)}, {val(rate)}, {val(length)}, {val(cost)}, {val(rating)})')
        doSql(sql)

        # 获取新增的 film_id
        new_id = querySql('SELECT MAX(film_id) FROM film')[0][0]

        # 同步分类
        for cid, var in cat_vars.items():
            if var.get():
                doSql(f'INSERT INTO film_category(film_id, category_id) VALUES({new_id}, {cid})')

        showinfo('恭喜', '电影添加成功')
        clear_form()
        bind_data()

    def edit_click():
        global selected_film_id
        if selected_film_id is None:
            showerror(title='很抱歉', message='请先在表格中选择一条记录')
            return
        title = entry_title.get().strip()
        if not title:
            showerror(title='很抱歉', message='必须输入片名')
            return
        lang_id = _get_combo_id(combo_lang) or 1
        year = entry_year.get().strip() or 'NULL'
        if year != 'NULL':
            year = int(year)
        dur = entry_dur.get().strip() or '3'
        rate = entry_rate.get().strip() or '4.99'
        length = entry_len.get().strip() or 'NULL'
        if length != 'NULL':
            length = int(length)
        cost = entry_cost.get().strip() or '19.99'
        rating = combo_rating.get() or 'PG'
        desc = text_desc.get('1.0', tkinter.END).strip().replace("'", "''")
        desc_val = f'"{desc}"' if desc else 'NULL'

        def val(v):
            if v == 'NULL':
                return 'NULL'
            elif isinstance(v, str):
                return f'"{v}"'
            return str(v)

        sql = (f'UPDATE film SET title="{title}", description={desc_val}, '
               f'release_year={val(year)}, language_id={lang_id}, '
               f'rental_duration={val(dur)}, rental_rate={val(rate)}, '
               f'length={val(length)}, replacement_cost={val(cost)}, '
               f'rating={val(rating)} WHERE film_id={selected_film_id}')
        doSql(sql)

        # 同步分类
        doSql(f'DELETE FROM film_category WHERE film_id={selected_film_id}')
        for cid, var in cat_vars.items():
            if var.get():
                doSql(f'INSERT INTO film_category(film_id, category_id) '
                      f'VALUES({selected_film_id}, {cid})')

        showinfo('恭喜', '电影修改成功')
        clear_form()
        bind_data()

    def delete_click():
        global selected_film_id
        if selected_film_id is None:
            showerror(title='很抱歉', message='请先在表格中选择一条记录')
            return
        # 检查是否有在借拷贝
        rented = querySql(
            f'SELECT COUNT(*) FROM inventory i '
            f'JOIN rental r ON i.inventory_id=r.inventory_id AND r.return_date IS NULL '
            f'WHERE i.film_id={selected_film_id}')
        if rented and rented[0][0] > 0:
            showerror(title='很抱歉', message='该影片有拷贝正在租出中，无法删除')
            return
        title = entry_title.get()
        if askyesno('请确认', f'确定要删除电影"{title}"吗？') == tkinter.YES:
            doSql(f'DELETE FROM film_actor WHERE film_id={selected_film_id}')
            doSql(f'DELETE FROM film_category WHERE film_id={selected_film_id}')
            doSql(f'DELETE FROM inventory WHERE film_id={selected_film_id}')
            doSql(f'DELETE FROM film WHERE film_id={selected_film_id}')
            showinfo('恭喜', '电影及关联数据删除成功')
            clear_form()
            bind_data()

    button_query = tkinter.Button(frame, text='查询', command=query_click)
    button_query.place(x=70, y=195, width=80, height=28)
    button_add = tkinter.Button(frame, text='添加', command=add_click)
    button_add.place(x=180, y=195, width=80, height=28)
    button_edit = tkinter.Button(frame, text='修改', command=edit_click)
    button_edit.place(x=290, y=195, width=80, height=28)
    button_delete = tkinter.Button(frame, text='删除', command=delete_click)
    button_delete.place(x=400, y=195, width=80, height=28)

    # 初始化
    lang_rows = querySql('SELECT language_id, name FROM language ORDER BY name')
    combo_lang['values'] = [f'{r[0]}|{r[1]}' for r in lang_rows]
    combo_lang._map = {f'{r[0]}|{r[1]}': r[0] for r in lang_rows}
    combo_lang.set(f'{lang_rows[0][0]}|{lang_rows[0][1]}')

    # Load categories as checkboxes
    cat_rows = querySql('SELECT category_id, name FROM category ORDER BY name')
    for i, (cid, cname) in enumerate(cat_rows):
        var = tkinter.IntVar()
        cat_vars[cid] = var
        row = i % 8
        col = i // 8
        cb = tkinter.Checkbutton(category_frame, text=cname, variable=var)
        cb.place(x=5 + col * 100, y=5 + row * 20)

    # Load actors for the add-actor combobox
    actor_rows = querySql('SELECT actor_id, CONCAT(first_name, " ", last_name) FROM actor ORDER BY first_name')
    combo_add_actor['values'] = [f'{r[0]}|{r[1]}' for r in actor_rows]
    combo_add_actor._map = {f'{r[0]}|{r[1]}': r[0] for r in actor_rows}

    bind_data()
    return frame
