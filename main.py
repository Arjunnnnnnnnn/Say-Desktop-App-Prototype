
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

import authentication as auth
import database
import email_verification
from themes import THEMES


# ================================================
# APP CONFIGURATION
# ================================================

YELLOW = "#FFD900"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class SayApp:

    def __init__(self, root):
        self.root = root
        self.root.title("say.")
        self.root.geometry("1280x820")
        self.root.minsize(950, 650)

        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass

        self.user = None
        self.pending_registration = None
        self.theme_name = "light"
        self.colors = THEMES["light"]
        self.current_page = "home"

        database.initialize_database()
        self.show_welcome()

    # ================================================
    # GENERAL HELPERS
    # ================================================

    def apply_theme(self):
        self.colors = THEMES[self.theme_name]
        ctk.set_appearance_mode(self.theme_name)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(
            fg_color=self.colors["background"]
        )

    def label(
        self,
        parent,
        text,
        size=12,
        color="text",
        bold=False,
        **kwargs
    ):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=(
                "Segoe UI",
                size,
                "bold" if bold else "normal"
            ),
            text_color=self.colors[color],
            **kwargs
        )

    def logo(self, parent, size=34):
        """Creates the yellow Say logo."""
        return ctk.CTkLabel(
            parent,
            text="say.",
            font=("Segoe UI", size, "bold"),
            text_color=YELLOW
        )

    def button(
        self,
        parent,
        text,
        command,
        primary=True,
        width=None
    ):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width or 180,
            height=44,
            corner_radius=12,
            font=("Segoe UI", 12, "bold"),
            fg_color=(
                self.colors["accent"]
                if primary
                else self.colors["surface_alt"]
            ),
            hover_color=(
                self.colors["accent_hover"]
                if primary
                else self.colors["border"]
            ),
            text_color=(
                self.colors["accent_text"]
                if primary
                else self.colors["text"]
            )
        )

    def entry(self, parent, placeholder="", show=None):
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=46,
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"],
            fg_color=self.colors["entry"],
            text_color=self.colors["text"],
            placeholder_text_color=self.colors["muted"],
            font=("Segoe UI", 12),
            show=show
        )

    def card(self, parent):
        return ctk.CTkFrame(
            parent,
            fg_color=self.colors["surface"],
            corner_radius=18,
            border_width=1,
            border_color=self.colors["border"]
        )

    def text_link(self, parent, text, command):
        link = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=34,
            corner_radius=9,
            fg_color="transparent",
            hover_color=self.colors["surface_alt"],
            text_color=self.colors["text"],
            font=("Segoe UI", 11),
            anchor="w"
        )
        link.pack(anchor="w", pady=3)
        return link

    def change_theme(self, theme):
        self.theme_name = theme
        self.apply_theme()

        if self.user:
            database.save_theme(self.user["id"], theme)
            self.show_dashboard(self.current_page)
        else:
            self.show_welcome()

    # ================================================
    # AUTHENTICATION LAYOUT
    # ================================================

    def auth_shell(self, title, subtitle):
        self.clear_screen()

        outer = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["background"],
            corner_radius=0
        )
        outer.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=24
        )

        panel = self.card(outer)
        panel.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        panel.grid_columnconfigure(
            0,
            weight=4,
            uniform="auth"
        )
        panel.grid_columnconfigure(
            1,
            weight=6,
            uniform="auth"
        )
        panel.grid_rowconfigure(0, weight=1)

        # Branding panel
        brand = ctk.CTkFrame(
            panel,
            fg_color=self.colors["surface_alt"],
            corner_radius=18
        )
        brand.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(12, 5),
            pady=12
        )

        brand_content = ctk.CTkFrame(
            brand,
            fg_color="transparent"
        )
        brand_content.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=32
        )

        # Yellow logo
        self.logo(
            brand_content,
            48
        ).pack(anchor="w")

        self.label(
            brand_content,
            "SIMPLE. PRIVATE. CONNECTED.",
            9,
            "muted",
            True
        ).pack(
            anchor="w",
            pady=(2, 0)
        )

        ctk.CTkFrame(
            brand_content,
            fg_color="transparent"
        ).pack(fill="both", expand=True)

        self.label(
            brand_content,
            "Conversations\nthat matter.",
            30,
            "text",
            True,
            justify="left"
        ).pack(anchor="w")

        self.label(
            brand_content,
            "Private messaging for the\npeople in your life.",
            13,
            "muted",
            justify="left"
        ).pack(
            anchor="w",
            pady=(12, 0)
        )

        ctk.CTkFrame(
            brand_content,
            fg_color="transparent"
        ).pack(fill="both", expand=True)

        # Yellow branding text
        ctk.CTkLabel(
            brand_content,
            text="WELCOME TO SAY",
            font=("Segoe UI", 10, "bold"),
            text_color=YELLOW
        ).pack(anchor="w")

        # Scrollable form panel
        right = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            corner_radius=18,
            scrollbar_button_color=self.colors["border"],
            scrollbar_button_hover_color=self.colors["muted"]
        )
        right.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(5, 12),
            pady=12
        )

        right.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )
        form.pack(
            fill="x",
            padx=40,
            pady=35
        )

        self.label(
            form,
            title,
            28,
            "text",
            True
        ).pack(anchor="w")

        self.label(
            form,
            subtitle,
            12,
            "muted"
        ).pack(
            anchor="w",
            pady=(8, 22)
        )

        return form

    def add_field(
        self,
        parent,
        caption,
        placeholder,
        show=None
    ):
        self.label(
            parent,
            caption.upper(),
            10,
            "muted",
            True
        ).pack(
            anchor="w",
            pady=(12, 7)
        )

        field = self.entry(
            parent,
            placeholder,
            show
        )
        field.pack(fill="x")

        return field

    # ================================================
    # WELCOME PAGE
    # ================================================

    def show_welcome(self):
        form = self.auth_shell(
            "Welcome to Say",
            "Simple, private messaging with the people you care about."
        )

        ctk.CTkFrame(
            form,
            fg_color="transparent",
            height=20
        ).pack()

        self.button(
            form,
            "Log in",
            self.show_login
        ).pack(
            fill="x",
            pady=7
        )

        self.button(
            form,
            "Create an account",
            self.show_register,
            False
        ).pack(
            fill="x",
            pady=7
        )

        self.label(
            form,
            "APPEARANCE",
            10,
            "muted",
            True
        ).pack(
            anchor="w",
            pady=(35, 10)
        )

        theme_row = ctk.CTkFrame(
            form,
            fg_color="transparent"
        )
        theme_row.pack(anchor="w")

        self.button(
            theme_row,
            "Light",
            lambda: self.change_theme("light"),
            False,
            110
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.button(
            theme_row,
            "Dark",
            lambda: self.change_theme("dark"),
            False,
            110
        ).pack(side="left")

    # ================================================
    # REGISTER
    # ================================================

    def show_register(self):
        form = self.auth_shell(
            "Create your account",
            "Choose a Say ID to get started."
        )

        email = self.add_field(
            form,
            "Gmail address",
            "you@gmail.com"
        )

        say_id = self.add_field(
            form,
            "Say ID",
            "Choose a unique username"
        )

        password = self.add_field(
            form,
            "Password",
            "At least 10 characters",
            "•"
        )

        confirm = self.add_field(
            form,
            "Confirm password",
            "Enter your password again",
            "•"
        )

        def submit():
            problem = auth.validate_registration(
                email.get(),
                say_id.get(),
                password.get()
            )

            if problem:
                messagebox.showerror(
                    "Registration",
                    problem
                )
                return

            if password.get() != confirm.get():
                messagebox.showerror(
                    "Registration",
                    "The passwords you entered do not match."
                )
                return

            if database.get_user_by_email(email.get()):
                messagebox.showerror(
                    "Registration",
                    "An account with this email already exists."
                )
                return

            if database.get_user_by_say_id(say_id.get()):
                messagebox.showerror(
                    "Registration",
                    "This Say ID is already taken. Please choose another."
                )
                return

            self.pending_registration = {
                "email": email.get().strip().lower(),
                "say_id": say_id.get().strip().lstrip("@").lower(),
                "password": password.get()
            }

            try:
                email_verification.send_verification_code(
                    self.pending_registration["email"]
                )
            except Exception as exc:
                messagebox.showerror(
                    "Unable to send code",
                    str(exc)
                )
                return

            self.show_verification()

        self.button(
            form,
            "Send verification code",
            submit
        ).pack(
            fill="x",
            pady=(25, 10)
        )

        self.text_link(
            form,
            "Already have an account? Log in",
            self.show_login
        )

        self.text_link(
            form,
            "Back",
            self.show_welcome
        )

    # ================================================
    # VERIFICATION
    # ================================================

    def show_verification(self):
        if not self.pending_registration:
            self.show_register()
            return

        form = self.auth_shell(
            "Verify your email",
            "Enter the 6-digit code we sent to your inbox."
        )

        self.label(
            form,
            self.pending_registration["email"],
            12,
            "text",
            True
        ).pack(
            anchor="w",
            pady=(0, 15)
        )

        code = self.add_field(
            form,
            "Verification code",
            "000000"
        )

        def verify():
            valid = email_verification.verify_verification_code(
                self.pending_registration["email"],
                code.get()
            )

            if not valid:
                messagebox.showerror(
                    "Verification",
                    "The code is incorrect or has expired."
                )
                return

            details = self.pending_registration

            password_hash, password_salt = auth.hash_password(
                details["password"]
            )

            try:
                user_id = database.create_user(
                    details["email"],
                    details["say_id"],
                    password_hash,
                    password_salt
                )
            except Exception as exc:
                messagebox.showerror(
                    "Account creation",
                    str(exc)
                )
                return

            self.user = {
                "id": user_id,
                "email": details["email"],
                "say_id": details["say_id"]
            }

            self.pending_registration = None
            self.theme_name = "light"
            self.apply_theme()

            messagebox.showinfo(
                "Welcome to Say",
                "Your email has been verified and your account is ready."
            )

            self.show_dashboard("home")

        self.button(
            form,
            "Verify and create account",
            verify
        ).pack(
            fill="x",
            pady=(25, 10)
        )

        self.text_link(
            form,
            "Resend code",
            self.resend_code
        )

        self.text_link(
            form,
            "Back to sign up",
            self.show_register
        )

    def resend_code(self):
        if not self.pending_registration:
            return

        try:
            email_verification.send_verification_code(
                self.pending_registration["email"]
            )
            messagebox.showinfo(
                "Say",
                "A new verification code has been sent to your email."
            )
        except Exception as exc:
            messagebox.showerror(
                "Email",
                str(exc)
            )

    # ================================================
    # LOGIN
    # ================================================

    def show_login(self):
        form = self.auth_shell(
            "Welcome back",
            "Log in to continue to Say."
        )

        email = self.add_field(
            form,
            "Gmail address",
            "you@gmail.com"
        )

        password = self.add_field(
            form,
            "Password",
            "Enter your password",
            "•"
        )

        def login():
            user = database.get_user_by_email(email.get())

            if not user or not auth.verify_password(
                password.get(),
                user["password_hash"],
                user["password_salt"]
            ):
                messagebox.showerror(
                    "Login",
                    "Incorrect email or password. Please try again."
                )
                return

            self.user = user
            self.theme_name = database.get_theme(user["id"])
            self.apply_theme()
            self.show_dashboard("home")

        self.button(
            form,
            "Log in",
            login
        ).pack(
            fill="x",
            pady=(25, 10)
        )

        self.text_link(
            form,
            "Create an account",
            self.show_register
        )

        self.text_link(
            form,
            "Back",
            self.show_welcome
        )

    # ================================================
    # DASHBOARD LAYOUT
    # ================================================

    def show_dashboard(self, page="home"):
        self.current_page = page
        self.clear_screen()

        main = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["background"],
            corner_radius=0
        )
        main.pack(fill="both", expand=True)

        # Top navigation bar
        top = ctk.CTkFrame(
            main,
            height=76,
            corner_radius=0,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        top.pack(fill="x")
        top.pack_propagate(False)

        # Yellow dashboard logo
        self.logo(
            top,
            34
        ).pack(
            side="left",
            padx=28,
            pady=10
        )

        self.label(
            top,
            "@" + self.user["say_id"],
            12,
            "muted"
        ).pack(
            side="right",
            padx=30
        )

        # Main area
        body = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )
        body.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=20
        )

        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(
            body,
            width=225,
            corner_radius=18,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )

        sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 18)
        )

        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)

        self.label(
            sidebar,
            "WORKSPACE",
            10,
            "muted",
            True
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(24, 14)
        )

        navigation = [
            ("Home", "home"),
            ("Messages", "messages"),
            ("Find people", "find"),
            ("Chat requests", "requests"),
            ("Profile", "profile"),
            ("Settings", "settings")
        ]

        for index, (text, target) in enumerate(
            navigation,
            start=1
        ):
            active = target == page

            nav = ctk.CTkButton(
                sidebar,
                text=text,
                command=lambda p=target: self.show_dashboard(p),
                height=46,
                corner_radius=11,
                anchor="w",
                font=(
                    "Segoe UI",
                    12,
                    "bold" if active else "normal"
                ),
                fg_color=(
                    self.colors["accent"]
                    if active
                    else "transparent"
                ),
                hover_color=(
                    self.colors["accent_hover"]
                    if active
                    else self.colors["surface_alt"]
                ),
                text_color=(
                    self.colors["accent_text"]
                    if active
                    else self.colors["text"]
                )
            )

            nav.grid(
                row=index,
                column=0,
                sticky="ew",
                padx=10,
                pady=4
            )

        # Flexible row keeps logout at the bottom
        sidebar.grid_rowconfigure(99, weight=1)

        self.button(
            sidebar,
            "Log out",
            self.logout,
            False
        ).grid(
            row=100,
            column=0,
            sticky="ew",
            padx=12,
            pady=16
        )

        # Scrollable content area
        self.content = ctk.CTkScrollableFrame(
            body,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.colors["border"],
            scrollbar_button_hover_color=self.colors["muted"]
        )

        self.content.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.content.grid_columnconfigure(0, weight=1)

        self.render_page(page)

    # ================================================
    # PAGE HELPERS
    # ================================================

    def page_heading(self, title, subtitle):
        self.label(
            self.content,
            title,
            29,
            "text",
            True
        ).pack(
            anchor="w",
            pady=(12, 5)
        )

        self.label(
            self.content,
            subtitle,
            13,
            "muted"
        ).pack(
            anchor="w",
            pady=(0, 22)
        )

    # ================================================
    # HOME
    # ================================================

    def render_home(self):
        self.page_heading(
            f"Welcome, @{self.user['say_id']}",
            "Message the people who matter to you."
        )

        card = self.card(self.content)
        card.pack(fill="x", pady=5)

        self.label(
            card,
            "Start a conversation.",
            22,
            "text",
            True
        ).pack(
            anchor="w",
            padx=25,
            pady=(24, 8)
        )

        self.label(
            card,
            "Search for someone by their Say ID and send them a chat request.",
            13,
            "muted",
            wraplength=750,
            justify="left"
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

        self.button(
            card,
            "Find people",
            lambda: self.show_dashboard("find"),
            width=155
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 24)
        )

    # ================================================
    # FIND PEOPLE
    # ================================================

    def render_find_people(self):
        self.page_heading(
            "Find people",
            "Search for people by their Say ID."
        )

        card = self.card(self.content)
        card.pack(fill="x", pady=5)

        self.label(
            card,
            "Search by Say ID",
            17,
            "text",
            True
        ).pack(
            anchor="w",
            padx=24,
            pady=(24, 12)
        )

        search_row = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        search_row.pack(
            fill="x",
            padx=24
        )

        search_row.grid_columnconfigure(0, weight=1)

        query = self.entry(
            search_row,
            "Enter a Say ID"
        )

        query.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 12)
        )

        results = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        results.pack(
            fill="x",
            padx=24,
            pady=(18, 24)
        )

        def search():
            for widget in results.winfo_children():
                widget.destroy()

            matches = database.search_users(
                query.get(),
                self.user["id"]
            )

            if not matches:
                self.label(
                    results,
                    "No users found.",
                    13,
                    "muted"
                ).pack(
                    anchor="w",
                    pady=12
                )
                return

            for match in matches:
                row = ctk.CTkFrame(
                    results,
                    fg_color=self.colors["surface_alt"],
                    corner_radius=12
                )
                row.pack(
                    fill="x",
                    pady=5
                )

                self.label(
                    row,
                    "@" + match["say_id"],
                    14,
                    "text",
                    True
                ).pack(
                    side="left",
                    padx=16,
                    pady=14
                )

                self.button(
                    row,
                    "Send request",
                    lambda receiver=match["id"]: self.send_request(receiver),
                    width=145
                ).pack(
                    side="right",
                    padx=12,
                    pady=8
                )

        self.button(
            search_row,
            "Search",
            search,
            width=125
        ).grid(
            row=0,
            column=1
        )

        query.bind(
            "<Return>",
            lambda event: search()
        )

    # ================================================
    # MESSAGES
    # ================================================

    def render_messages(self):
        self.page_heading(
            "Messages",
            "Your conversations."
        )

        conversations = database.get_conversations(
            self.user["id"]
        )

        if not conversations:
            card = self.card(self.content)
            card.pack(fill="x", pady=5)

            self.label(
                card,
                "No conversations yet",
                20,
                "text",
                True
            ).pack(
                anchor="w",
                padx=24,
                pady=(24, 8)
            )

            self.label(
                card,
                "Send a chat request to start messaging.",
                13,
                "muted"
            ).pack(
                anchor="w",
                padx=24,
                pady=(0, 18)
            )

            self.button(
                card,
                "Find people",
                lambda: self.show_dashboard("find")
            ).pack(
                anchor="w",
                padx=24,
                pady=(0, 24)
            )

            return

        for conversation in conversations:
            row = self.card(self.content)
            row.pack(fill="x", pady=6)

            self.label(
                row,
                "@" + conversation["other_say_id"],
                15,
                "text",
                True
            ).pack(
                anchor="w",
                padx=20,
                pady=18
            )

    # ================================================
    # CHAT REQUESTS
    # ================================================

    def render_requests(self):
        self.page_heading(
            "Chat requests",
            "Review and respond to people who want to connect."
        )

        self.label(
            self.content,
            "INCOMING REQUESTS",
            10,
            "muted",
            True
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        incoming = database.get_incoming_requests(
            self.user["id"]
        )

        if not incoming:
            self.label(
                self.content,
                "No incoming requests.",
                13,
                "muted"
            ).pack(
                anchor="w",
                pady=(0, 18)
            )

        for request in incoming:
            row = self.card(self.content)
            row.pack(fill="x", pady=5)

            self.label(
                row,
                "@" + request["say_id"],
                14,
                "text",
                True
            ).pack(
                side="left",
                padx=16,
                pady=15
            )

            actions = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )
            actions.pack(
                side="right",
                padx=10,
                pady=8
            )

            self.button(
                actions,
                "Accept",
                lambda rid=request["id"]: self.respond_request(rid, True),
                width=100
            ).pack(
                side="left",
                padx=4
            )

            self.button(
                actions,
                "Decline",
                lambda rid=request["id"]: self.respond_request(rid, False),
                False,
                100
            ).pack(
                side="left",
                padx=4
            )

        self.label(
            self.content,
            "SENT REQUESTS",
            10,
            "muted",
            True
        ).pack(
            anchor="w",
            pady=(22, 10)
        )

        outgoing = database.get_outgoing_requests(
            self.user["id"]
        )

        if not outgoing:
            self.label(
                self.content,
                "No pending sent requests.",
                13,
                "muted"
            ).pack(anchor="w")

        for request in outgoing:
            row = self.card(self.content)
            row.pack(fill="x", pady=5)

            self.label(
                row,
                "@" + request["say_id"] + "  ·  Pending",
                13,
                "text"
            ).pack(
                anchor="w",
                padx=16,
                pady=15
            )

    # ================================================
    # PROFILE
    # ================================================

    def render_profile(self):
        self.page_heading(
            "Your profile",
            "Your account details."
        )

        card = self.card(self.content)
        card.pack(fill="x", pady=5)

        self.label(
            card,
            "SAY ID",
            10,
            "muted",
            True
        ).pack(
            anchor="w",
            padx=24,
            pady=(24, 6)
        )

        self.label(
            card,
            "@" + self.user["say_id"],
            22,
            "text",
            True
        ).pack(
            anchor="w",
            padx=24,
            pady=(0, 20)
        )

        self.label(
            card,
            "EMAIL",
            10,
            "muted",
            True
        ).pack(
            anchor="w",
            padx=24,
            pady=(0, 6)
        )

        self.label(
            card,
            self.user["email"],
            13,
            "text"
        ).pack(
            anchor="w",
            padx=24,
            pady=(0, 24)
        )

    # ================================================
    # SETTINGS
    # ================================================

    def render_settings(self):
        self.page_heading(
            "Settings",
            "Manage your preferences."
        )

        card = self.card(self.content)
        card.pack(fill="x", pady=5)

        self.label(
            card,
            "Appearance",
            19,
            "text",
            True
        ).pack(
            anchor="w",
            padx=24,
            pady=(24, 8)
        )

        self.label(
            card,
            "Choose a light or dark theme for Say.",
            13,
            "muted"
        ).pack(
            anchor="w",
            padx=24,
            pady=(0, 20)
        )

        theme_row = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        theme_row.pack(
            anchor="w",
            padx=24,
            pady=(0, 24)
        )

        self.button(
            theme_row,
            "Light mode",
            lambda: self.change_theme("light"),
            False,
            140
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.button(
            theme_row,
            "Dark mode",
            lambda: self.change_theme("dark"),
            False,
            140
        ).pack(side="left")

        self.label(
            card,
            "SAY",
            10,
            "muted",
            True
        ).pack(
            anchor="w",
            padx=24,
            pady=(5, 5)
        )

        self.label(
            card,
            "Desktop app",
            12,
            "text"
        ).pack(
            anchor="w",
            padx=24,
            pady=(0, 24)
        )

    # ================================================
    # PAGE ROUTER
    # ================================================

    def render_page(self, page):
        if page == "home":
            self.render_home()

        elif page == "messages":
            self.render_messages()

        elif page == "find":
            self.render_find_people()

        elif page == "requests":
            self.render_requests()

        elif page == "profile":
            self.render_profile()

        elif page == "settings":
            self.render_settings()

    # ================================================
    # REQUEST ACTIONS
    # ================================================

    def send_request(self, receiver_id):
        try:
            database.send_chat_request(
                self.user["id"],
                receiver_id
            )

            messagebox.showinfo(
                "Say",
                "Chat request sent."
            )

            self.show_dashboard("find")

        except Exception as exc:
            messagebox.showerror(
                "Chat request",
                str(exc)
            )

    def respond_request(self, request_id, accept):
        try:
            database.respond_to_chat_request(
                request_id,
                self.user["id"],
                accept
            )

            messagebox.showinfo(
                "Say",
                "Request accepted."
                if accept
                else "Request declined."
            )

            self.show_dashboard("requests")

        except Exception as exc:
            messagebox.showerror(
                "Chat request",
                str(exc)
            )

    # ================================================
    # LOGOUT
    # ================================================

    def logout(self):
        self.user = None
        self.pending_registration = None
        self.theme_name = "light"
        self.apply_theme()
        self.show_welcome()


# ================================================
# START APP
# ================================================

if __name__ == "__main__":
    root = ctk.CTk()
    app = SayApp(root)
    root.mainloop()
