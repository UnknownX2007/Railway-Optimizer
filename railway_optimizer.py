import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import math
import json

from algorithms import kruskal, dijkstra


# ============================================================
# 1. CÁC LỚP DỮ LIỆU ĐỒ THỊ
# ============================================================

class Station:
    """Đại diện cho một nhà ga (đỉnh của đồ thị)."""

    def __init__(self, station_id, name, x, y, broken=False):
        self.id = station_id
        self.name = name
        self.x = x
        self.y = y
        self.broken = broken


class RailwayEdge:
    """Đại diện cho một tuyến đường sắt (cạnh của đồ thị)."""

    def __init__(self, u, v, weight, broken=False):
        self.u = u
        self.v = v
        self.weight = weight
        self.broken = broken


# ============================================================
# 2. ỨNG DỤNG TKINTER
# ============================================================

class RailwayApp:
    BG = "#F3F6FA"
    PANEL = "#FFFFFF"
    NAVY = "#17324D"
    BLUE = "#2878B5"
    GREEN = "#219653"
    RED = "#D64545"
    ORANGE = "#E59A27"
    PURPLE = "#7C3AED"
    BROKEN = "#B91C1C"
    TEXT = "#243447"
    MUTED = "#68788A"
    EDGE = "#AAB7C4"
    CITY_NAMES = (
        "Cần Thơ",
        "TP. Hồ Chí Minh",
        "Đà Lạt",
        "Nha Trang",
        "Đà Nẵng",
        "Huế",
        "Hà Nội",
        "Phú Thọ",
    )

    def __init__(self, root):
        self.root = root
        self.root.title("BLING CANDY | RAILWAY NETWORK OPTIMIZER")
        self.root.geometry("1180x760")
        self.root.minsize(980, 650)
        self.root.configure(bg=self.BG)

        self.stations = []
        self.edges = []
        self.mst_edges = []
        self.path_edges = []

        self.next_station_id = 0
        self.mode = "VIEW"
        self.selected_station = None
        self.selected_edge = None
        self._canvas_scale = 1.0
        self._canvas_offset_x = 0
        self._canvas_offset_y = 0

        self._setup_style()
        self._setup_ui()
        self._draw_graph()

    # --------------------------------------------------------
    # GIAO DIỆN
    # --------------------------------------------------------

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground=self.TEXT,
            rowheight=27,
            font=("Arial", 9)
        )
        style.configure(
            "Treeview.Heading",
            background="#E8EEF5",
            foreground=self.NAVY,
            font=("Arial", 9, "bold")
        )
        style.map("Treeview", background=[("selected", "#D8EAF8")])

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.NAVY, height=76)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="RAILWAY NETWORK OPTIMIZER",
            font=("Arial", 20, "bold"),
            fg="white",
            bg=self.NAVY
        ).pack(anchor="w", padx=22, pady=(13, 0))

        tk.Label(
            header,
            text="BLING CANDY | MÔ PHỎNG MẠNG LƯỚI ĐƯỜNG SẮT BẰNG THUẬT TOÁN ĐỒ THỊ",
            font=("Arial", 9),
            fg="#D5E3EF",
            bg=self.NAVY
        ).pack(anchor="w", padx=24, pady=(2, 0))

        footer = tk.Label(
            self.root,
            text="Project | Developed by BLING CANDY | Graph Theory",
            bg="#DDE7F0",
            fg=self.NAVY,
            font=("Arial", 8, "bold"),
            pady=5
        )
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Sidebar
        sidebar = tk.Frame(body, bg=self.PANEL, width=245, bd=1, relief=tk.SOLID)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="BẢNG ĐIỀU KHIỂN",
            bg=self.PANEL, fg=self.NAVY,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=15, pady=(17, 12))

        self._section_label(sidebar, "QUẢN LÝ MẠNG ĐƯỜNG SẮT")
        self._make_button(sidebar, "＋  Thêm nhà ga", self.enable_add_station, self.BLUE)
        self._make_button(sidebar, "⚑  Đánh dấu hỏng / Khôi phục", self.enable_toggle_flag, self.BROKEN)

        self._section_label(sidebar, "THUẬT TOÁN ĐỒ THỊ")
        self._make_button(sidebar, "🌲  Chạy Kruskal (MST)", self.run_kruskal, self.GREEN)
        self._make_button(sidebar, "⌖  Chạy Dijkstra", self.run_dijkstra_dialog, self.ORANGE)

        self._section_label(sidebar, "QUẢN LÝ DỮ LIỆU")
        self._make_button(sidebar, "Tạo dữ liệu mẫu", self.load_sample_data, "#64748B")
        self._make_button(sidebar, "Lưu dữ liệu JSON", self.save_data, "#64748B")
        self._make_button(sidebar, "Mở dữ liệu JSON", self.load_data, "#64748B")
        self._make_button(sidebar, "Xóa kết quả", self.clear_results, "#64748B")
        self._make_button(sidebar, "Xóa toàn bộ", self.clear_all, self.RED)

        self.status_label = tk.Label(
            sidebar,
            text="Trạng thái: Sẵn sàng.\nChọn nhà ga hoặc tuyến đường trên sơ đồ để thao tác.",
            bg="#EDF4FA",
            fg=self.NAVY,
            font=("Arial", 9),
            justify=tk.LEFT,
            wraplength=205,
            padx=10,
            pady=10
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=12)

        # Main workspace
        workspace = tk.Frame(body, bg=self.BG)
        workspace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(workspace, bg=self.PANEL, bd=1, relief=tk.SOLID)
        toolbar.pack(fill=tk.X, pady=(0, 9))

        tk.Label(
            toolbar, text="SƠ ĐỒ MẠNG LƯỚI",
            bg=self.PANEL, fg=self.NAVY,
            font=("Arial", 11, "bold")
        ).pack(side=tk.LEFT, padx=14, pady=11)

        tk.Label(
            toolbar,
            text="• Đỏ đứt nét: Bị hỏng    • Xanh lá: MST    • Cam: Đường đi Dijkstra",
            bg=self.PANEL, fg=self.MUTED,
            font=("Arial", 8)
        ).pack(side=tk.RIGHT, padx=12)

        canvas_frame = tk.Frame(workspace, bg=self.PANEL, bd=1, relief=tk.SOLID)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#FBFCFE",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", lambda event: self._draw_graph())

        bottom = tk.Frame(workspace, bg=self.PANEL, bd=1, relief=tk.SOLID)
        bottom.pack(fill=tk.X, pady=(9, 0))

        tk.Label(
            bottom, text="KẾT QUẢ / THÔNG TIN",
            bg=self.PANEL, fg=self.NAVY,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=12, pady=(9, 4))

        self.result_text = tk.Text(
            bottom,
            height=6,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#F8FAFC",
            fg=self.TEXT,
            relief=tk.FLAT,
            padx=10,
            pady=7
        )
        self.result_text.pack(fill=tk.X, padx=10, pady=(0, 10))
        self._set_result(
            "Chào mừng đến với Railway Optimizer!\n"
            "• Thêm nhà ga: bấm nút “Thêm nhà ga” bên trái, sau đó nhấp lên vị trí muốn đặt trên sơ đồ.\n"
            "• Nhấp vào 1 nhà ga: hiện nút Đổi tên / Xóa ngay trên sơ đồ, hoặc nhấp thêm 1 ga nữa để tạo tuyến đường.\n"
            "• Nhấp vào 1 tuyến đường: hiện nút Đổi trọng số / Xóa tuyến ngay trên sơ đồ."
        )

    def _section_label(self, parent, text):
        tk.Label(
            parent, text=text, bg=self.PANEL, fg=self.MUTED,
            font=("Arial", 8, "bold")
        ).pack(anchor="w", padx=15, pady=(13, 5))

    def _make_button(self, parent, text, command, color):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            font=("Arial", 9, "bold"),
            anchor="w",
            padx=12,
            pady=8,
            cursor="hand2"
        )
        button.pack(fill=tk.X, padx=11, pady=3)

    def _set_status(self, text):
        self.status_label.config(text="Trạng thái: " + text)

    def _set_result(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)

    def _update_canvas_transform(self):
        width = max(self.canvas.winfo_width(), 500)
        height = max(self.canvas.winfo_height(), 350)
        self._canvas_scale = min(width / 900.0, height / 500.0)
        self._canvas_offset_x = (width - 900 * self._canvas_scale) / 2
        self._canvas_offset_y = (height - 500 * self._canvas_scale) / 2

    def _graph_to_canvas(self, x, y):
        return (
            self._canvas_offset_x + x * self._canvas_scale,
            self._canvas_offset_y + y * self._canvas_scale
        )

    def _canvas_to_graph(self, x, y):
        return (
            (x - self._canvas_offset_x) / self._canvas_scale,
            (y - self._canvas_offset_y) / self._canvas_scale
        )

    # --------------------------------------------------------
    # TÌM KIẾM DỮ LIỆU
    # --------------------------------------------------------

    def get_station(self, station_id):
        for station in self.stations:
            if station.id == station_id:
                return station
        return None

    def get_station_at(self, x, y):
        gx, gy = self._canvas_to_graph(x, y)
        for station in reversed(self.stations):
            sx, sy = self._graph_to_canvas(station.x, station.y)
            if math.hypot(sx - x, sy - y) <= 23:
                return station
        return None

    @staticmethod
    def _point_to_segment_dist(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        len_sq = dx * dx + dy * dy
        if len_sq == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / len_sq))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(px - proj_x, py - proj_y)

    def get_edge_at(self, x, y, threshold=9):
        for edge in reversed(self.edges):
            a = self.get_station(edge.u)
            b = self.get_station(edge.v)
            if not a or not b:
                continue
            ax, ay = self._graph_to_canvas(a.x, a.y)
            bx, by = self._graph_to_canvas(b.x, b.y)
            if self._point_to_segment_dist(x, y, ax, ay, bx, by) <= threshold:
                return edge
        return None

    def station_name(self, station_id):
        station = self.get_station(station_id)
        return station.name if station else f"Ga {station_id}"

    def edge_exists(self, u, v):
        return any(
            (edge.u == u and edge.v == v) or
            (edge.u == v and edge.v == u)
            for edge in self.edges
        )

    def ask_positive_weight(self, title, prompt, initialvalue=None):
        """Request a finite edge weight greater than zero."""
        while True:
            weight = simpledialog.askfloat(
                title,
                prompt,
                initialvalue=initialvalue,
                parent=self.root
            )
            if weight is None:
                return None
            if math.isfinite(weight) and weight > 0:
                return weight
            messagebox.showwarning(
                "Giá trị không hợp lệ",
                "Độ dài tuyến đường phải là số lớn hơn 0.",
                parent=self.root
            )

    # --------------------------------------------------------
    # TƯƠNG TÁC CANVAS
    # --------------------------------------------------------

    def enable_add_station(self):
        self.mode = "ADD_STATION"
        self.selected_station = None
        self.selected_edge = None
        self._draw_graph()
        self._set_status("Thêm nhà ga: nhấp vào vị trí muốn đặt trên sơ đồ.")

    def enable_toggle_flag(self):
        if not self.stations and not self.edges:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa có nhà ga hoặc tuyến đường nào.")
            return

        if self.mode == "TOGGLE_FLAG":
            self.mode = "VIEW"
            self._draw_graph()
            self._set_status("Đã thoát chế độ đánh dấu hỏng.")
            return

        self.mode = "TOGGLE_FLAG"
        self.selected_station = None
        self.selected_edge = None
        self._draw_graph()
        self._set_status("Gắn/gỡ cờ hỏng: nhấp vào nhà ga hoặc tuyến đường (nhấp vùng trống để thoát).")

    def on_canvas_click(self, event):
        # Nếu bấm vào các nút thao tác nổi trên canvas thì để tag_bind xử lý
        if self.canvas.gettags("current"):
            tags = self.canvas.gettags("current")
            if any(t.startswith("hud_") for t in tags):
                return

        if self.mode == "ADD_STATION":
            self.add_station_at(event.x, event.y)
            return

        if self.mode == "TOGGLE_FLAG":
            self.toggle_flag_at(event.x, event.y)
            return

        # 1. Kiểm tra nhấp vào nhà ga
        station = self.get_station_at(event.x, event.y)
        if station:
            # Nếu đang chọn 1 nhà ga khác trước đó -> tạo tuyến đường giữa 2 ga
            if self.selected_station is not None and self.selected_station != station.id:
                u, v = self.selected_station, station.id
                self.selected_station = None
                self.selected_edge = None
                self._draw_graph()
                self._create_edge_between(u, v)
                return

            # Nhấp lại chính nhà ga đang chọn -> bỏ chọn
            if self.selected_station == station.id:
                self.selected_station = None
                self._draw_graph()
                self._set_status(f"Đã bỏ chọn {station.name}.")
                return

            # Chọn nhà ga này
            self.selected_station = station.id
            self.selected_edge = None
            self._draw_graph()
            state_txt = " [HỎNG]" if station.broken else ""
            self._set_status(
                f"Đã chọn {station.name}{state_txt}. Nhấp thêm 1 ga nữa để tạo tuyến, "
                "hoặc chọn Đổi tên / Xóa trên sơ đồ."
            )
            return

        # 2. Kiểm tra nhấp vào tuyến đường (cạnh)
        edge = self.get_edge_at(event.x, event.y)
        if edge:
            self.selected_station = None
            if self.selected_edge is edge:
                self.selected_edge = None
                self._draw_graph()
                self._set_status("Đã bỏ chọn tuyến đường.")
                return

            self.selected_edge = edge
            self._draw_graph()
            pair = f"{self.station_name(edge.u)} - {self.station_name(edge.v)}"
            self._set_status(
                f"Đã chọn tuyến {pair} ({edge.weight:g}). "
                "Chọn Đổi độ dài hoặc Xóa tuyến trên sơ đồ."
            )
            return

        # 3. Nhấp ra vùng trống -> bỏ chọn tất cả
        if self.selected_station is not None or self.selected_edge is not None:
            self.selected_station = None
            self.selected_edge = None
            self._draw_graph()
            self._set_status("Đã bỏ chọn.")
        else:
            self._set_status("Chế độ xem sơ đồ.")

    def toggle_flag_at(self, x, y):
        station = self.get_station_at(x, y)
        if station:
            station.broken = not station.broken
            self._invalidate_results()
            self._draw_graph()
            if station.broken:
                self._set_status(f"Đã đánh dấu HỎNG nhà ga {station.name}.")
            else:
                self._set_status(f"Đã khôi phục hoạt động nhà ga {station.name}.")
            return

        edge = self.get_edge_at(x, y)
        if edge:
            edge.broken = not edge.broken
            self._invalidate_results()
            self._draw_graph()
            pair = f"{self.station_name(edge.u)} - {self.station_name(edge.v)}"
            if edge.broken:
                self._set_status(f"Đã đánh dấu HỎNG tuyến {pair}.")
            else:
                self._set_status(f"Đã khôi phục hoạt động tuyến {pair}.")
            return

        self.mode = "VIEW"
        self._draw_graph()
        self._set_status("Đã thoát chế độ gắn cờ hỏng.")

    def add_station_at(self, x, y):
        if x < 30 or y < 52 or x > self.canvas.winfo_width() - 30 or y > self.canvas.winfo_height() - 30:
            self._set_status("Vị trí quá sát mép sơ đồ, hãy chọn điểm khác.")
            return

        gx, gy = self._canvas_to_graph(x, y)
        for station in self.stations:
            distance = math.hypot(station.x - gx, station.y - gy)
            if distance < 55:
                messagebox.showwarning(
                    "Quá gần nhà ga",
                    f"Vị trí này quá gần nhà ga {station.name}. "
                    "Hãy đặt cách ít nhất 55 đơn vị."
                )
                self._set_status("Không thể thêm ga: khoảng cách với ga khác quá gần.")
                return

        default_name = (
            self.CITY_NAMES[self.next_station_id]
            if self.next_station_id < len(self.CITY_NAMES)
            else f"Thành phố {self.next_station_id + 1}"
        )
        name = simpledialog.askstring(
            "Thêm nhà ga",
            "Nhập tên nhà ga:",
            initialvalue=default_name,
            parent=self.root
        )
        if not name or not name.strip():
            self.mode = "VIEW"
            self._draw_graph()
            self._set_status("Đã hủy thêm nhà ga.")
            return

        name = name.strip()
        if any(s.name.lower() == name.lower() for s in self.stations):
            messagebox.showwarning("Tên bị trùng", "Tên nhà ga đã tồn tại.")
            return

        station = Station(self.next_station_id, name, gx, gy)
        self.next_station_id += 1
        self.stations.append(station)

        self._invalidate_results()
        self.mode = "VIEW"
        self._draw_graph()
        self._set_status(f"Đã thêm nhà ga {name}.")

    def _create_edge_between(self, u, v):
        if self.edge_exists(u, v):
            messagebox.showwarning("Tuyến đường đã tồn tại", "Hai nhà ga này đã được nối.")
            self._set_status("Tuyến đường đã tồn tại.")
            return

        weight = self.ask_positive_weight(
            "Độ dài tuyến đường",
            f"Nhập độ dài xây dựng tuyến {self.station_name(u)} - {self.station_name(v)}:"
            " (Nhập số dương)"
        )

        if weight is None:
            self._set_status("Đã hủy thêm tuyến đường.")
            return

        self.edges.append(RailwayEdge(u, v, weight))
        self._invalidate_results()
        self._draw_graph()
        self._set_status(f"Đã thêm tuyến {self.station_name(u)} - {self.station_name(v)}.")

    # --------------------------------------------------------
    # THAO TÁC TRÊN NHÀ GA / CẠNH ĐANG CHỌN TRÊN CANVAS
    # --------------------------------------------------------

    def rename_selected_station(self):
        station = self.get_station(self.selected_station)
        if not station:
            return

        new_name = simpledialog.askstring(
            "Đổi tên nhà ga",
            f"Nhập tên mới cho {station.name}:",
            initialvalue=station.name,
            parent=self.root
        )
        if not new_name or not new_name.strip():
            return

        new_name = new_name.strip()
        if any(
            s.id != station.id and s.name.lower() == new_name.lower()
            for s in self.stations
        ):
            messagebox.showwarning("Tên bị trùng", "Tên nhà ga đã tồn tại.")
            return

        old_name = station.name
        station.name = new_name
        self._invalidate_results()
        self._draw_graph()
        self._set_status(f"Đã đổi tên {old_name} thành {new_name}.")

    def delete_selected_station(self):
        station = self.get_station(self.selected_station)
        if not station:
            return

        if not messagebox.askyesno(
            "Xác nhận",
            f"Bạn có chắc muốn xóa {station.name}?\n"
            "Các tuyến đường liên quan cũng sẽ bị xóa."
        ):
            return

        self.stations = [s for s in self.stations if s.id != station.id]
        self.edges = [
            e for e in self.edges
            if e.u != station.id and e.v != station.id
        ]
        self.selected_station = None
        self._invalidate_results()
        self._draw_graph()
        self._set_status(f"Đã xóa nhà ga {station.name}.")

    def edit_selected_edge_weight(self):
        edge = self.selected_edge
        if edge is None or edge not in self.edges:
            return

        pair = f"{self.station_name(edge.u)} - {self.station_name(edge.v)}"
        new_weight = self.ask_positive_weight(
            "Đổi độ dài tuyến đường",
            f"Nhập độ dài mới cho tuyến {pair}:",
            initialvalue=edge.weight
        )
        if new_weight is None:
            return

        edge.weight = new_weight
        self._invalidate_results()
        self._draw_graph()
        self._set_status(f"Đã đổi độ dài tuyến {pair} thành {new_weight:g}.")

    def delete_selected_edge(self):
        edge = self.selected_edge
        if edge is None or edge not in self.edges:
            return

        pair = f"{self.station_name(edge.u)} - {self.station_name(edge.v)}"
        if not messagebox.askyesno(
            "Xác nhận",
            f"Bạn có chắc muốn xóa tuyến {pair} ({edge.weight:g})?"
        ):
            return

        self.edges.remove(edge)
        self.selected_edge = None
        self._invalidate_results()
        self._draw_graph()
        self._set_status(f"Đã xóa tuyến {pair}.")

    # --------------------------------------------------------
    # VẼ ĐỒ THỊ & THANH THAO TÁC TRÊN CANVAS
    # --------------------------------------------------------

    def _draw_hud_button(self, x, y, text, bg, border, fg, tag, callback):
        w = max(92, len(text) * 7 + 22)
        self.canvas.create_rectangle(
            x, y, x + w, y + 28,
            fill=bg, outline=border, width=1,
            tags=(tag,)
        )
        self.canvas.create_text(
            x + w / 2, y + 14,
            text=text,
            fill=fg,
            font=("Arial", 8, "bold"),
            tags=(tag,)
        )
        self.canvas.tag_bind(
            tag,
            "<Button-1>",
            lambda event: (callback(), "break")[1]
        )
        return x + w + 8

    def _draw_canvas_hud(self):
        x = 12
        y = 10

        # Nhãn trạng thái chế độ hiện tại trên canvas
        if self.mode == "ADD_STATION":
            info_text = "＋ Nhấp vào vị trí trống trên sơ đồ để đặt nhà ga"
            bg, border, fg = "#EFF6FF", "#BFDBFE", self.BLUE
        elif self.mode == "TOGGLE_FLAG":
            info_text = "⚑ Nhấp vào nhà ga hoặc tuyến đường để gắn/gỡ cờ hỏng"
            bg, border, fg = "#FEF2F2", "#FECACA", self.BROKEN
        elif self.selected_station is not None:
            st = self.get_station(self.selected_station)
            name = st.name if st else ""
            info_text = f"● Đang chọn {name} (nhấp thêm 1 ga nữa để tạo tuyến)"
            bg, border, fg = "#FFFBEB", "#FDE68A", "#B45309"
        elif self.selected_edge is not None:
            pair = f"{self.station_name(self.selected_edge.u)} - {self.station_name(self.selected_edge.v)}"
            info_text = f"━ Đang chọn tuyến {pair} ({self.selected_edge.weight:g})"
            bg, border, fg = "#F5F3FF", "#DDD6FE", self.PURPLE
        else:
            info_text = "Nhấp vào 1 nhà ga hoặc 1 tuyến đường trên sơ đồ để thao tác"
            bg, border, fg = "#EEF4FA", "#D5E2EE", self.NAVY

        pill_w = max(260, len(info_text) * 6 + 22)
        self.canvas.create_rectangle(
            x, y, x + pill_w, y + 28,
            fill=bg, outline=border, width=1,
            tags=("hud_info",)
        )
        self.canvas.create_text(
            x + 11, y + 14,
            text=info_text,
            anchor="w",
            fill=fg,
            font=("Arial", 8, "bold"),
            tags=("hud_info",)
        )
        x += pill_w + 10

        # Nếu đang chọn 1 nhà ga -> hiện nút Đổi tên & Xóa nhà ga ngay trên canvas
        if self.selected_station is not None and self.get_station(self.selected_station) is not None:
            x = self._draw_hud_button(
                x, y, "✎ Đổi tên ga",
                "#475569", "#334155", "white",
                "hud_rename_station", self.rename_selected_station
            )
            self._draw_hud_button(
                x, y, "⌫ Xóa nhà ga",
                self.RED, "#B91C1C", "white",
                "hud_delete_station", self.delete_selected_station
            )

        # Nếu đang chọn 1 tuyến đường -> hiện nút Đổi trọng số & Xóa tuyến ngay trên canvas
        elif self.selected_edge is not None and self.selected_edge in self.edges:
            x = self._draw_hud_button(
                x, y, "✎ Đổi trọng số",
                self.PURPLE, "#6D28D9", "white",
                "hud_edit_weight", self.edit_selected_edge_weight
            )
            self._draw_hud_button(
                x, y, "✂ Xóa tuyến",
                self.RED, "#B91C1C", "white",
                "hud_delete_edge", self.delete_selected_edge
            )

    def _draw_graph(self):
        if not hasattr(self, "canvas"):
            return

        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 500)
        height = max(self.canvas.winfo_height(), 350)
        self._update_canvas_transform()

        # Lưới nền nhẹ
        for x in range(0, width, 30):
            self.canvas.create_line(x, 0, x, height, fill="#F0F3F7")
        for y in range(0, height, 30):
            self.canvas.create_line(0, y, width, y, fill="#F0F3F7")

        mst_keys = {
            frozenset((edge.u, edge.v)) for edge in self.mst_edges
        }
        path_keys = {
            frozenset((edge.u, edge.v)) for edge in self.path_edges
        }

        # Vẽ các tuyến đường
        for edge in self.edges:
            a = self.get_station(edge.u)
            b = self.get_station(edge.v)
            if not a or not b:
                continue
            ax, ay = self._graph_to_canvas(a.x, a.y)
            bx, by = self._graph_to_canvas(b.x, b.y)

            is_broken_edge = edge.broken or a.broken or b.broken
            is_selected_edge = self.selected_edge is edge
            key = frozenset((edge.u, edge.v))
            color = self.EDGE
            line_width = 2
            dash = None

            if is_broken_edge:
                color = self.BROKEN if edge.broken else "#E5A5A5"
                line_width = 3 if edge.broken else 2
                dash = (6, 4)
            else:
                if key in mst_keys:
                    color = self.GREEN
                    line_width = 4
                if key in path_keys:
                    color = self.ORANGE
                    line_width = 5

            if is_selected_edge:
                color = self.PURPLE
                line_width = 5

            self.canvas.create_line(
                ax, ay, bx, by,
                fill=color,
                width=line_width,
                dash=dash
            )

            mid_x = (ax + bx) / 2
            mid_y = (ay + by) / 2
            label = f"{edge.weight:g} ⚑" if edge.broken else f"{edge.weight:g}"
            box_half_w = 24 if edge.broken else 19

            if is_selected_edge:
                box_fill, box_outline, txt_fill, box_w = "#F5F3FF", self.PURPLE, self.PURPLE, 2
            elif edge.broken:
                box_fill, box_outline, txt_fill, box_w = "#FEF2F2", self.BROKEN, self.BROKEN, 1
            else:
                box_fill, box_outline, txt_fill, box_w = "white", "#DCE3EA", self.TEXT, 1

            self.canvas.create_rectangle(
                mid_x - box_half_w, mid_y - 11,
                mid_x + box_half_w, mid_y + 11,
                fill=box_fill,
                outline=box_outline,
                width=box_w
            )
            self.canvas.create_text(
                mid_x, mid_y,
                text=label,
                fill=txt_fill,
                font=("Arial", 8, "bold")
            )

        # Vẽ nhà ga
        for station in self.stations:
            sx, sy = self._graph_to_canvas(station.x, station.y)
            fill = self.BROKEN if station.broken else self.BLUE
            outline = "#FECACA" if station.broken else "white"
            radius = 17

            if station.id == self.selected_station:
                outline = self.ORANGE
                radius = 20
                self.canvas.create_oval(
                    sx - 23, sy - 23,
                    sx + 23, sy + 23,
                    outline="#FDE68A",
                    width=2
                )

            self.canvas.create_oval(
                sx - radius, sy - radius,
                sx + radius, sy + radius,
                fill=fill,
                outline=outline,
                width=3
            )

            if station.broken:
                self.canvas.create_text(
                    sx, sy,
                    text="✕",
                    fill="white",
                    font=("Arial", 11, "bold")
                )

            label_text = f"{station.name} [HỎNG]" if station.broken else station.name
            self.canvas.create_text(
                sx,
                sy + 29,
                text=label_text,
                fill=self.BROKEN if station.broken else self.NAVY,
                font=("Arial", 9, "bold")
            )

        if not self.stations:
            self.canvas.create_text(
                width / 2, height / 2,
                text="Chưa có dữ liệu nhà ga. Bấm “Thêm nhà ga” bên trái rồi nhấp lên sơ đồ để bắt đầu",
                fill="#91A0AF",
                font=("Arial", 13),
                justify=tk.CENTER
            )

        self._draw_canvas_hud()

    # --------------------------------------------------------
    # KRUSKAL - CÂY KHUNG NHỎ NHẤT
    # --------------------------------------------------------

    def run_kruskal(self):
        if not self.stations:
            messagebox.showwarning("Thiếu dữ liệu", "Hãy thêm nhà ga trước.")
            return

        result = kruskal(self.stations, self.edges)
        active_stations = result["active_stations"]
        broken_stations = result["broken_stations"]
        usable_edges = result["usable_edges"]
        selected = result["selected_edges"]
        total_weight = result["total_weight"]

        self.mst_edges = selected
        self.path_edges = []
        self._draw_graph()

        if not active_stations:
            self._set_result(
                "KẾT QUẢ KRUSKAL: Tất cả nhà ga đều đang bị gắn cờ hỏng, "
                "không thể xây dựng mạng lưới."
            )
            self._set_status("Tất cả nhà ga đều đang bị hỏng.")
            return

        if len(active_stations) == 1:
            self._set_result(
                "KẾT QUẢ KRUSKAL: "
                f"Chỉ còn 1 nhà ga hoạt động ({active_stations[0].name}).\n"
                "Cây khung nhỏ nhất không cần cạnh, tổng trọng số = 0."
            )
            self._set_status("Chỉ có một nhà ga đang hoạt động.")
            return

        broken_note = ""
        if broken_stations:
            broken_note = "Nhà ga bị bỏ qua (đang hỏng): " + ", ".join(
                station.name for station in broken_stations
            )

        if not result["connected"]:
            report = (
                "KẾT QUẢ KRUSKAL: "
                "Không thể tạo cây khung bao phủ toàn bộ nhà ga đang hoạt động.\n"
                "Nguyên nhân: Hệ thống nhà ga có nhiều tuyến chưa được xây dựng hoặc đang bị hỏng.\n"
                f"Số thành phố đang hoạt động: {len(active_stations)} / {len(self.stations)}\n"
                f"Số tuyến trong đồ thị: {len(usable_edges)}\n"
                f"Số tuyến thuộc MST đã chọn: {len(selected)} / {len(active_stations) - 1}\n"
                f"Tổng độ dài các tuyến đã chọn: {total_weight:g}\n"
                f"{broken_note}"
            )
            self._set_result(report)
            self._set_status(
                "Đồ thị không liên thông, không tồn tại tuyến đường bao phủ các ga hoạt động."
            )
            return

        lines = ["KẾT QUẢ CÂY KHUNG NHỎ NHẤT (KRUSKAL): \n"]
        for i, edge in enumerate(selected, 1):
            lines.append(
                f"{i}. {self.station_name(edge.u)} -> "
                f"{self.station_name(edge.v)}: {edge.weight:g}\n"
            )
        lines += [
            f"Tổng độ dài cây khung nhỏ nhất (MST): {total_weight:g}\n",
            f"Số thành phố đang hoạt động: {len(active_stations)} / {len(self.stations)}\n",
            f"Số tuyến trong đồ thị: {len(usable_edges)}\n",
            f"Số tuyến thuộc MST: {len(selected)}\n",
        ]
        if broken_stations:
            lines.append(
                "Nhà ga đang hỏng (bỏ qua): "
                + ", ".join(station.name for station in broken_stations)
            )
        lines.append("")
        lines.append("Các tuyến màu xanh lá là những tuyến thuộc cây khung nhỏ nhất")
        self._set_result("".join(lines))
        self._set_status(
            f"Đã tìm được cây khung nhỏ nhất (MST) với tổng độ dài {total_weight:g}."
        )

    # --------------------------------------------------------
    # DIJKSTRA - ĐƯỜNG ĐI NGẮN NHẤT
    # --------------------------------------------------------

    def ask_station_combobox(self, title, prompt, names):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=self.PANEL)

        result = {"value": None}
        tk.Label(
            dialog,
            text=prompt,
            bg=self.PANEL,
            fg=self.NAVY,
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, padx=18, pady=(16, 8), sticky="w")

        combo = ttk.Combobox(
            dialog,
            values=names,
            state="readonly",
            width=34,
            font=("Arial", 9)
        )
        combo.grid(row=1, column=0, padx=18, pady=(0, 12))
        if names:
            combo.current(0)

        def accept():
            result["value"] = combo.get()
            dialog.destroy()

        def cancel():
            dialog.destroy()

        buttons = tk.Frame(dialog, bg=self.PANEL)
        buttons.grid(row=2, column=0, padx=18, pady=(0, 16), sticky="e")
        tk.Button(
            buttons, text="Hủy", command=cancel,
            bg="#E8EEF5", fg=self.NAVY, relief=tk.FLAT, padx=12, pady=5
        ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(
            buttons, text="Chọn", command=accept,
            bg=self.BLUE, fg="white", relief=tk.FLAT, padx=12, pady=5
        ).pack(side=tk.LEFT)

        dialog.bind("<Return>", lambda event: accept())
        dialog.bind("<Escape>", lambda event: cancel())
        dialog.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        dialog.wait_window()
        return result["value"]

    def run_dijkstra_dialog(self):
        if len(self.stations) < 2:
            messagebox.showwarning("Thiếu dữ liệu", "Cần ít nhất hai nhà ga.")
            return

        names = [
            f"{s.name} [HỎNG]" if s.broken else s.name
            for s in self.stations
        ]

        start_name = self.ask_station_combobox("Ga xuất phát", "Chọn nhà ga xuất phát:", names)
        if not start_name:
            return

        start = self._find_station_by_name(start_name.strip())
        if not start:
            messagebox.showerror("Không tìm thấy", "Nhà ga xuất phát không tồn tại.")
            return
        if start.broken:
            messagebox.showwarning("Nhà ga bị hỏng", f"Nhà ga {start.name} đang bị gắn cờ hỏng, không thể xuất phát.")
            return

        end_name = self.ask_station_combobox("Ga đích đến", "Chọn nhà ga đích đến:", names)
        if not end_name:
            return

        end = self._find_station_by_name(end_name.strip())
        if not end:
            messagebox.showerror("Không tìm thấy", "Nhà ga đích không tồn tại.")
            return
        if end.broken:
            messagebox.showwarning("Nhà ga bị hỏng", f"Nhà ga {end.name} đang bị gắn cờ hỏng, không thể đi tới.")
            return

        if start.id == end.id:
            self.path_edges = []
            self._draw_graph()
            self._set_result(
                "KẾT QUẢ DIJKSTRA:\n"
                f"Lộ trình ngắn nhất từ {start.name} đến {end.name}: 0\n"
                f"Ga xuất phát và ga đích đều là {start.name}."
            )
            self._set_status(f"Ga xuất phát và ga đích đều là {start.name}; khoảng cách: 0.")
            return

        self.run_dijkstra(start.id, end.id)

    def _find_station_by_name(self, name):
        clean_name = name.replace("[HỎNG]", "").strip().lower()
        for station in self.stations:
            if station.name.lower() == clean_name:
                return station
        return None

    def run_dijkstra(self, start_id, end_id):
        result = dijkstra(self.stations, self.edges, start_id, end_id)

        if result["status"] == "negative_weight":
            messagebox.showerror(
                "Độ dài không hợp lệ",
                "Trọng số tuyến đường không thể là số âm."
            )
            return

        if result["status"] == "invalid_station":
            messagebox.showerror(
                "Nhà ga không hợp lệ",
                "Nhà ga xuất phát hoặc đích đến không tồn tại hay đang bị hỏng."
            )
            return

        if result["status"] == "unreachable":
            self.path_edges = []
            self.mst_edges = []
            self._draw_graph()
            self._set_result(
                "KẾT QUẢ DIJKSTRA: "
                f"Không tìm thấy đường đi khả dụng từ {self.station_name(start_id)} "
                f"đến {self.station_name(end_id)}.\n"
                "Có thể chưa có tuyến đường hoặc tuyến đường và nhà ga trung gian đang bị hỏng."
            )
            self._set_status("Không tồn tại đường đi khả dụng giữa hai nhà ga đã chọn.")
            return

        path = result["path"]
        path_edges = result["path_edges"]
        distance = result["distance"]
        self.path_edges = path_edges
        self.mst_edges = []
        self._draw_graph()

        path_names = [self.station_name(station_id) for station_id in path]
        lines = [
            "KẾT QUẢ ĐƯỜNG ĐI NGẮN NHẤT (DIJKSTRA)\n",
            f"Lộ trình ngắn nhất từ {self.station_name(path[0])} đến "
            f"{self.station_name(path[-1])}: ",
            "  " + "  →  ".join(path_names),
            "\n",
            "Các tuyến trên lộ trình:\n"
        ]
        for i, edge in enumerate(path_edges, 1):
            lines.append(
                f"{i}. {self.station_name(path[i - 1])} - "
                f"{self.station_name(path[i])}: {edge.weight:g}\n"
            )
        lines += [
            f"Tổng độ dài tuyến đường ngắn nhất: {distance:g}\n",
            "Các tuyến màu cam là tuyến thuộc đường đi ngắn nhất (đã tránh các điểm hỏng)."
        ]
        self._set_result("".join(lines))
        self._set_status(
            f"Đã tìm thấy đường đi ngắn nhất, tổng độ dài {distance:g}."
        )

    # --------------------------------------------------------
    # DỮ LIỆU MẪU
    # --------------------------------------------------------

    def load_sample_data(self):
        if self.stations or self.edges:
            if not messagebox.askyesno(
                "Tạo dữ liệu mẫu\n",
                "Dữ liệu hiện tại sẽ được thay thế. Bạn có muốn tiếp tục?"
            ):
                return

        self.stations = []
        self.edges = []
        self.mst_edges = []
        self.path_edges = []
        self.selected_station = None
        self.selected_edge = None
        self.mode = "VIEW"
        self.next_station_id = 0

        sample_stations = [
            ("Cần Thơ", 100, 260),
            ("TP. Hồ Chí Minh", 190, 80),
            ("Đà Lạt", 280, 310),
            ("Nha Trang", 370, 130),
            ("Đà Nẵng", 460, 340),
            ("Huế", 550, 190),
            ("Hà Nội", 640, 270),
            ("Phú Thọ", 730, 190),
        ]

        for name, x, y in sample_stations:
            self.stations.append(
                Station(self.next_station_id, name, x, y)
            )
            self.next_station_id += 1

        sample_edges = [
            (0, 1, 174),
            (1, 2, 310),
            (1, 3, 442),
            (2, 3, 285),
            (2, 4, 620),
            (3, 4, 516),
            (3, 5, 621),
            (4, 5, 105),
            (5, 6, 658),
            (6, 7, 90),
            (4, 6, 763),
        ]

        for u, v, weight in sample_edges:
            self.edges.append(RailwayEdge(u, v, weight))

        self._draw_graph()
        self._set_status("Đã tải dữ liệu mẫu gồm 8 thành phố và 11 tuyến đường.")
        self._set_result(
            "ĐÃ TẠO DỮ LIỆU MẪU\n"
            "Đồ thị gồm 8 thành phố, bố trí nằm ngang từ Nam sang Bắc: Cần Thơ, TP. Hồ Chí Minh, Đà Lạt, Nha Trang, Đà Nẵng, Huế, Hà Nội, Phú Thọ.\n"
            "• Nhấp 1 nhà ga để Đổi tên / Xóa, hoặc nhấp thêm 1 ga nữa để nối tuyến.\n"
            "• Nhấp 1 tuyến đường để Đổi độ dài / Xóa tuyến."
        )

    # --------------------------------------------------------
    # LÀM MỚI / XÓA DỮ LIỆU
    # --------------------------------------------------------

    def _invalidate_results(self):
        self.mst_edges = []
        self.path_edges = []
        self._set_result(
            "Dữ liệu đồ thị đã thay đổi.\n"
            "Hãy chạy lại Kruskal hoặc Dijkstra để cập nhật kết quả."
        )

    def save_data(self):
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Lưu dữ liệu mạng lưới",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Tất cả tệp", "*.*")]
        )
        if not path:
            return

        data = {
            "stations": [
                {
                    "id": station.id,
                    "name": station.name,
                    "x": station.x,
                    "y": station.y,
                    "broken": station.broken
                }
                for station in self.stations
            ],
            "edges": [
                {
                    "u": edge.u,
                    "v": edge.v,
                    "weight": edge.weight,
                    "broken": edge.broken
                }
                for edge in self.edges
            ]
        }
        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except OSError as error:
            messagebox.showerror("Không thể lưu", f"Không thể ghi tệp JSON:\n{error}")
            return

        self._set_status(f"Đã lưu dữ liệu JSON tại {path}.")
        self._set_result(f"ĐÃ LƯU DỮ LIỆU\nTệp: {path}\n")

    def load_data(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Mở dữ liệu mạng lưới",
            filetypes=[("JSON", "*.json"), ("Tất cả tệp", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Tệp JSON không đúng cấu trúc.")

            stations = []
            for item in data.get("stations", []):
                if not isinstance(item, dict):
                    raise ValueError("Danh sách nhà ga không hợp lệ.")
                stations.append(
                    Station(
                        int(item["id"]),
                        str(item["name"]),
                        float(item["x"]),
                        float(item["y"]),
                        bool(item.get("broken", False))
                    )
                )

            station_ids = {station.id for station in stations}
            edges = []
            for item in data.get("edges", []):
                if not isinstance(item, dict):
                    raise ValueError("Danh sách tuyến đường không hợp lệ.")
                u, v, weight = int(item["u"]), int(item["v"]), float(item["weight"])
                if u not in station_ids or v not in station_ids:
                    raise ValueError("Tuyến đường tham chiếu tới nhà ga không tồn tại.")
                if not math.isfinite(weight) or weight <= 0:
                    raise ValueError("Trọng số tuyến đường phải là số dương.")
                edges.append(RailwayEdge(u, v, weight, bool(item.get("broken", False))))
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            messagebox.showerror("Không thể mở", f"Dữ liệu JSON không hợp lệ:\n{error}")
            return

        self.stations = stations
        self.edges = edges
        self.mst_edges = []
        self.path_edges = []
        self.next_station_id = max(station_ids, default=-1) + 1
        self.selected_station = None
        self.selected_edge = None
        self.mode = "VIEW"
        self._draw_graph()
        self._set_status(f"Đã mở dữ liệu JSON gồm {len(stations)} ga và {len(edges)} tuyến.")
        self._set_result(f"ĐÃ MỞ DỮ LIỆU\nTệp: {path}\n")

    def clear_results(self):
        self.mst_edges = []
        self.path_edges = []
        self.selected_station = None
        self.selected_edge = None
        self._draw_graph()
        self._set_result("Đã xóa phần kết quả thuật toán. Dữ liệu đồ thị vẫn được giữ nguyên.")
        self._set_status("Đã xóa kết quả.")

    def clear_all(self):
        if not self.stations and not self.edges:
            return

        if not messagebox.askyesno(
            "Xóa toàn bộ",
            "Bạn có chắc muốn xóa tất cả nhà ga và tuyến đường?"
        ):
            return

        self.stations.clear()
        self.edges.clear()
        self.mst_edges.clear()
        self.path_edges.clear()
        self.next_station_id = 0
        self.selected_station = None
        self.selected_edge = None
        self.mode = "VIEW"

        self._draw_graph()
        self._set_result("Đồ thị đã được xóa hoàn toàn.")
        self._set_status("Đã xóa toàn bộ dữ liệu.")
