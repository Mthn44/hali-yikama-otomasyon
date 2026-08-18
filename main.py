import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.metrics import dp


DB = "hali_yikama.db"
M2_FIYAT = 50


def database():
    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            phone TEXT,
            carpet TEXT,
            m2 REAL,
            price REAL,
            status TEXT,
            date TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            unit TEXT,
            stock REAL,
            buy_price REAL,
            sell_price REAL,
            min_stock REAL
        )
    """)

    conn.commit()
    return conn


class MenuScreen(Screen):

    def on_enter(self):

        self.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12)
        )

        title = Label(
            text="HALI YIKAMA\nOTOMASYONU",
            font_size=dp(26),
            size_hint_y=None,
            height=dp(90)
        )

        layout.add_widget(title)

        buttons = [
            ("➕ YENİ SİPARİŞ", "order"),
            ("📋 SİPARİŞLER", "orders"),
            ("🧴 DETERJAN / ÜRÜNLER", "products"),
            ("📊 RAPORLAR", "reports")
        ]

        for text, screen in buttons:

            button = Button(
                text=text,
                font_size=dp(18)
            )

            button.bind(
                on_press=lambda x, s=screen:
                setattr(self.manager, "current", s)
            )

            layout.add_widget(button)

        self.add_widget(layout)


class OrderScreen(Screen):

    def on_enter(self):

        self.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(8)
        )

        title = Label(
            text="YENİ SİPARİŞ",
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50)
        )

        layout.add_widget(title)

        self.customer = TextInput(
            hint_text="Müşteri adı",
            multiline=False
        )

        self.phone = TextInput(
            hint_text="Telefon",
            multiline=False
        )

        self.carpet = TextInput(
            hint_text="Halı türü",
            multiline=False
        )

        self.m2 = TextInput(
            hint_text="Metrekare",
            multiline=False,
            input_filter="float"
        )

        for field in [
            self.customer,
            self.phone,
            self.carpet,
            self.m2
        ]:
            layout.add_widget(field)

        save = Button(
            text="SİPARİŞİ KAYDET",
            size_hint_y=None,
            height=dp(55)
        )

        save.bind(on_press=self.save_order)

        layout.add_widget(save)

        back = Button(
            text="← ANA MENÜ",
            size_hint_y=None,
            height=dp(45)
        )

        back.bind(
            on_press=lambda x:
            setattr(self.manager, "current", "menu")
        )

        layout.add_widget(back)

        self.add_widget(layout)

    def save_order(self, instance):

        try:

            customer = self.customer.text.strip()
            phone = self.phone.text.strip()
            carpet = self.carpet.text.strip()
            m2 = float(self.m2.text)

            if not customer or m2 <= 0:
                raise ValueError

            total = m2 * M2_FIYAT

            conn = database()

            conn.execute("""
                INSERT INTO orders
                (customer, phone, carpet, m2, price, status, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                customer,
                phone,
                carpet,
                m2,
                total,
                "Alındı",
                datetime.now().strftime("%d.%m.%Y %H:%M")
            ))

            conn.commit()
            conn.close()

            message = (
                f"Sipariş kaydedildi!\n\n"
                f"Müşteri: {customer}\n"
                f"Halı: {carpet}\n"
                f"Miktar: {m2} m²\n"
                f"Ücret: {total:.2f} TL\n"
                f"Durum: Alındı"
            )

            Popup(
                title="BAŞARILI",
                content=Label(text=message),
                size_hint=(0.85, 0.45)
            ).open()

            self.customer.text = ""
            self.phone.text = ""
            self.carpet.text = ""
            self.m2.text = ""

        except:

            Popup(
                title="HATA",
                content=Label(
                    text="Bilgileri doğru şekilde doldur."
                ),
                size_hint=(0.85, 0.3)
            ).open()


class OrdersScreen(Screen):

    def on_enter(self):

        self.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(5)
        )

        title = Label(
            text="SİPARİŞLER",
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50)
        )

        layout.add_widget(title)

        conn = database()

        orders = conn.execute("""
            SELECT id, customer, carpet, m2, price, status, date
            FROM orders
            ORDER BY id DESC
        """).fetchall()

        conn.close()

        if not orders:

            layout.add_widget(
                Label(text="Henüz sipariş bulunmuyor.")
            )

        else:

            for order in orders:

                text = (
                    f"#{order[0]} - {order[1]}\n"
                    f"{order[2]} | {order[3]} m² | "
                    f"{order[4]:.2f} TL\n"
                    f"Durum: {order[5]} | {order[6]}"
                )

                layout.add_widget(
                    Label(
                        text=text,
                        size_hint_y=None,
                        height=dp(70)
                    )
                )

        back = Button(
            text="← ANA MENÜ",
            size_hint_y=None,
            height=dp(45)
        )

        back.bind(
            on_press=lambda x:
            setattr(self.manager, "current", "menu")
        )

        layout.add_widget(back)

        self.add_widget(layout)


class ProductsScreen(Screen):

    def on_enter(self):

        self.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        title = Label(
            text="🧴 DETERJAN / ÜRÜNLER",
            font_size=dp(22),
            size_hint_y=None,
            height=dp(50)
        )

        layout.add_widget(title)

        add = Button(
            text="➕ YENİ ÜRÜN",
            size_hint_y=None,
            height=dp(50)
        )

        add.bind(on_press=self.add_product)

        layout.add_widget(add)

        conn = database()

        products = conn.execute("""
            SELECT name, unit, stock,
                   buy_price, sell_price, min_stock
            FROM products
            ORDER BY name
        """).fetchall()

        conn.close()

        if not products:

            layout.add_widget(
                Label(text="Henüz ürün eklenmedi.")
            )

        else:

            for product in products:

                warning = ""

                if product[2] <= product[5]:
                    warning = " ⚠️ AZ STOK"

                text = (
                    f"{product[0]}{warning}\n"
                    f"Stok: {product[2]} {product[1]}\n"
                    f"Alış: {product[3]:.2f} TL | "
                    f"Satış: {product[4]:.2f} TL"
                )

                layout.add_widget(
                    Label(
                        text=text,
                        size_hint_y=None,
                        height=dp(75)
                    )
                )

        back = Button(
            text="← ANA MENÜ",
            size_hint_y=None,
            height=dp(45)
        )

        back.bind(
            on_press=lambda x:
            setattr(self.manager, "current", "menu")
        )

        layout.add_widget(back)

        self.add_widget(layout)

    def add_product(self, instance):

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(6)
        )

        name = TextInput(
            hint_text="Ürün adı",
            multiline=False
        )

        unit = TextInput(
            hint_text="Birim: litre / kg / adet",
            multiline=False
        )

        stock = TextInput(
            hint_text="Stok miktarı",
            multiline=False,
            input_filter="float"
        )

        buy = TextInput(
            hint_text="Alış fiyatı",
            multiline=False,
            input_filter="float"
        )

        sell = TextInput(
            hint_text="Satış fiyatı",
            multiline=False,
            input_filter="float"
        )

        minimum = TextInput(
            hint_text="Minimum stok",
            multiline=False,
            input_filter="float"
        )

        for field in [
            name,
            unit,
            stock,
            buy,
            sell,
            minimum
        ]:
            layout.add_widget(field)

        save = Button(
            text="KAYDET",
            size_hint_y=None,
            height=dp(50)
        )

        layout.add_widget(save)

        popup = Popup(
            title="YENİ ÜRÜN",
            content=layout,
            size_hint=(0.9, 0.85)
        )

        def save_product(instance):

            try:

                conn = database()

                conn.execute("""
                    INSERT INTO products
                    (name, unit, stock, buy_price,
                     sell_price, min_stock)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    name.text,
                    unit.text,
                    float(stock.text),
                    float(buy.text),
                    float(sell.text),
                    float(minimum.text)
                ))

                conn.commit()
                conn.close()

                popup.dismiss()
                self.on_enter()

            except:

                pass

        save.bind(on_press=save_product)

        popup.open()


class ReportsScreen(Screen):

    def on_enter(self):

        self.clear_widgets()

        conn = database()

        count = conn.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]

        revenue = conn.execute(
            "SELECT COALESCE(SUM(price),0) FROM orders"
        ).fetchone()[0]

        products = conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        low_stock = conn.execute(
            "SELECT COUNT(*) FROM products WHERE stock <= min_stock"
        ).fetchone()[0]

        conn.close()

        text = (
            "📊 RAPORLAR\n\n"
            f"Toplam sipariş: {count}\n\n"
            f"Toplam ciro: {revenue:.2f} TL\n\n"
            f"Toplam ürün: {products}\n\n"
            f"Az stoklu ürün: {low_stock}"
        )

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        layout.add_widget(
            Label(
                text=text,
                font_size=dp(22)
            )
        )

        back = Button(
            text="← ANA MENÜ",
            size_hint_y=None,
            height=dp(50)
        )

        back.bind(
            on_press=lambda x:
            setattr(self.manager, "current", "menu")
        )

        layout.add_widget(back)

        self.add_widget(layout)


class HaliYikamaApp(App):

    def build(self):

        database().close()

        manager = ScreenManager()

        manager.add_widget(
            MenuScreen(name="menu")
        )

        manager.add_widget(
            OrderScreen(name="order")
        )

        manager.add_widget(
            OrdersScreen(name="orders")
        )

        manager.add_widget(
            ProductsScreen(name="products")
        )

        manager.add_widget(
            ReportsScreen(name="reports")
        )

        return manager


if __name__ == "__main__":
    HaliYikamaApp().run()
