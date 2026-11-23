"""Điểm khởi chạy chương trình Bling Candy Railway Optimizer."""
import tkinter as tk
from railway_optimizer import RailwayApp


def main():
    root = tk.Tk()
    RailwayApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
