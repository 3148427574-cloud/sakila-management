"""
Sakila DVD 租赁管理系统 — 电影管理模块
"""
import tkinter
import tkinter.ttk


def create_film_frame(parent):
    frame = tkinter.Frame(parent)
    tkinter.Label(frame, text='电影管理模块（开发中）',
                  font=('Arial', 16)).place(x=300, y=200)
    return frame
