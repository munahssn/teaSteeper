from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageTk


APP_TITLE = "Tea Steeper"
WINDOW_SIZE = 640
SPRITE_SIZE = 2560
SPRITE_DIR = Path(__file__).resolve().parent / "sprites"
BUTTON_HEIGHT = 230
SCENE_SIZE = 560
SCENE_TOP = 20
FONT_FAMILY = "Space Mono"


@dataclass(frozen=True)
class Tea:
    name: str
    seconds: int
    button_file: str
    liquid_prefix: str


TEAS = (
    Tea("Black Tea", 3 * 60, "btn_black.png", "liquid_black"),
    Tea("Green Tea", 2 * 60, "btn_green.png", "liquid_green"),
    Tea("Herbal Tea", 4 * 60, "btn_herbal.png", "liquid_herbal"),
)


class TeaSteeperApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.resizable(False, False)

        self.images: dict[str, ImageTk.PhotoImage] = {}
        self.after_id: str | None = None
        self.active_tea: Tea | None = None
        self.remaining_seconds = 0

        self.canvas = tk.Canvas(
            self,
            width=WINDOW_SIZE,
            height=WINDOW_SIZE,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()

        self.load_images()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.show_menu()

    def load_images(self) -> None:
        filenames = [
            "background.png",
            "mug_empty.png",
            "done.png",
            "steam_1.png",
            "steam_2.png",
        ]

        for tea in TEAS:
            filenames.append(tea.button_file)
            filenames.extend(f"{tea.liquid_prefix}{stage}.png" for stage in range(1, 4))

        for filename in filenames:
            path = SPRITE_DIR / filename
            if not path.exists():
                raise FileNotFoundError(f"Missing sprite: {path}")

            image = Image.open(path).convert("RGBA")
            if filename.startswith("btn_"):
                image = self.prepare_button_image(image)
            elif filename == "background.png":
                image = image.resize((WINDOW_SIZE, WINDOW_SIZE), Image.Resampling.NEAREST)
            else:
                image = self.prepare_scene_image(image)

            self.images[filename] = ImageTk.PhotoImage(image)

    @staticmethod
    def prepare_button_image(image: Image.Image) -> Image.Image:
        bounds = image.getbbox()
        if bounds is not None:
            image = image.crop(bounds)

        width = round(image.width * (BUTTON_HEIGHT / image.height))
        return image.resize((width, BUTTON_HEIGHT), Image.Resampling.NEAREST)

    @staticmethod
    def prepare_scene_image(image: Image.Image) -> Image.Image:
        scaled = image.resize((SCENE_SIZE, SCENE_SIZE), Image.Resampling.NEAREST)
        canvas = Image.new("RGBA", (WINDOW_SIZE, WINDOW_SIZE), (0, 0, 0, 0))
        left = (WINDOW_SIZE - SCENE_SIZE) // 2
        canvas.alpha_composite(scaled, (left, SCENE_TOP))
        return canvas

    def clear_timer(self) -> None:
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

    def reset_canvas(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.images["background.png"], anchor="nw")

    def show_menu(self) -> None:
        self.clear_timer()
        self.active_tea = None
        self.reset_canvas()

        self.canvas.create_text(
            WINDOW_SIZE // 2,
            84,
            text="What tea would you like to brew today?",
            fill="#382313",
            font=self.font(24, "bold"),
        )

        button_positions = (130, 320, 510)
        for tea, x in zip(TEAS, button_positions):
            tag = self.tea_tag(tea)
            self.canvas.create_image(
                x,
                330,
                image=self.images[tea.button_file],
                anchor="center",
                tags=(tag,),
            )
            self.bind_clickable(tag, lambda _event, tea=tea: self.start_tea(tea))

    @staticmethod
    def tea_tag(tea: Tea) -> str:
        return tea.name.lower().replace(" ", "_")

    def bind_clickable(self, tag: str | int, command) -> None:
        self.canvas.tag_bind(tag, "<Button-1>", command)
        self.canvas.tag_bind(tag, "<Enter>", lambda _event: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(tag, "<Leave>", lambda _event: self.canvas.config(cursor=""))

    def start_tea(self, tea: Tea) -> None:
        self.clear_timer()
        self.active_tea = tea
        self.remaining_seconds = tea.seconds
        self.draw_brewing()
        self.after_id = self.after(1000, self.tick)

    def tick(self) -> None:
        self.after_id = None

        if self.active_tea is None:
            return

        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self.draw_done()
            return

        self.draw_brewing()
        self.after_id = self.after(1000, self.tick)

    def liquid_stage(self) -> int:
        if self.active_tea is None:
            return 1

        elapsed = self.active_tea.seconds - self.remaining_seconds
        third = self.active_tea.seconds / 3
        return min(3, int(elapsed // third) + 1)

    def draw_brewing(self) -> None:
        if self.active_tea is None:
            return

        self.reset_canvas()
        stage = self.liquid_stage()
        liquid_file = f"{self.active_tea.liquid_prefix}{stage}.png"
        steam_file = "steam_1.png" if self.remaining_seconds % 2 == 0 else "steam_2.png"

        self.draw_full_sprite(liquid_file)
        self.draw_full_sprite("mug_empty.png")
        self.draw_full_sprite(steam_file)
        self.draw_timer_text()
        self.draw_back_button()

    def draw_done(self) -> None:
        if self.active_tea is None:
            return

        self.clear_timer()
        liquid_file = f"{self.active_tea.liquid_prefix}3.png"
        self.reset_canvas()
        self.draw_full_sprite(liquid_file)
        self.draw_full_sprite("done.png")
        self.draw_timer_text("Time to drink!")
        self.draw_back_button("Brew another?")

    def draw_full_sprite(self, filename: str) -> None:
        self.canvas.create_image(0, 0, image=self.images[filename], anchor="nw")

    def draw_timer_text(self, text: str | None = None) -> None:
        label = text or self.format_time(self.remaining_seconds)
        self.canvas.create_text(
            WINDOW_SIZE // 2,
            WINDOW_SIZE - 56,
            text=label,
            fill="#382313",
            font=self.font(34, "bold"),
        )

    def draw_back_button(self, text: str = "Menu") -> None:
        button_bg = self.canvas.create_rectangle(
            20,
            20,
            180 if text == "Menu" else 260,
            68,
            fill= None,
            outline="",
            width=0,
            tags=("menu_button",),
        )
        button_text = self.canvas.create_text(
            42,
            44,
            text=text,
            fill="#382313",
            font=self.font(16, "bold"),
            anchor="w",
            tags=("menu_button",),
        )
        self.bind_clickable(button_bg, lambda _event: self.show_menu())
        self.bind_clickable(button_text, lambda _event: self.show_menu())

    @staticmethod
    def font(size: int, weight: str = "normal") -> tuple[str, int, str]:
        return (FONT_FAMILY, size, weight)

    @staticmethod
    def format_time(seconds: int) -> str:
        minutes, remaining = divmod(max(0, seconds), 60)
        return f"{minutes}:{remaining:02d}"

    def close(self) -> None:
        self.clear_timer()
        self.destroy()


if __name__ == "__main__":
    app = TeaSteeperApp()
    app.mainloop()
