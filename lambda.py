#!/usr/bin/env python3

import time
import sys
import math
import platform
import socket
import shutil
import datetime
import getpass

try:
    import msvcrt
except ImportError:
    msvcrt = None

try:
    import psutil
except ImportError:
    print("psutil puuttuu.")
    print("Asenna se komennolla: py -m pip install psutil")
    sys.exit(1)


# ─────────────────────────────────────────────
# ANSI / TERMINAL
# ─────────────────────────────────────────────

ORANGE = "\033[38;5;208m"
RESET = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
ALT_ON = "\033[?1049h"
ALT_OFF = "\033[?1049l"
CLEAR = "\033[2J"
HOME = "\033[H"


# ─────────────────────────────────────────────
# LOGO
# ─────────────────────────────────────────────

raw_logo = r"""
                 .:::::.
             -+###*****##*=:
          .+##+:..      .-*%#-
         -%#-   -##%*      .+%*.
        =%*      ..#%+       :%#.
       .%#         +%%-       -*%.
       =%-        +%#%%.       #%.
       +%-      .*@+ +%#       *%.
       -@+     :#%=   *%+     .%#
        *%-   =%%-    .#%+++  *%-
         *%= .++.      :#+=::#%-
          -##=.           :*%*.
            -*##+=----=+*##+:
               :-=+++++=-.
"""

logo = [line for line in raw_logo.splitlines() if line.strip()]
h = len(logo)
w = max(len(line) for line in logo)
logo = [line.ljust(w) for line in logo]


def mv(row, col):
    return f"\033[{row};{col}H"


# ─────────────────────────────────────────────
# SYSTEM INFO
# ─────────────────────────────────────────────

def get_os():
    return platform.platform()


def get_cpu():
    try:
        name = platform.processor()

        if not name:
            name = platform.uname().processor

        if not name:
            return "unknown"

        return name.strip()

    except Exception:
        return "unknown"


def temp():
    """
    Windows ei yleensä tarjoa CPU-lämpötilaa
    helposti ilman valmistajakohtaista rajapintaa.
    psutil voi joillain koneilla tarjota lämpötila-antureita.
    """

    try:
        sensors = psutil.sensors_temperatures()

        if sensors:
            for entries in sensors.values():
                for entry in entries:
                    if entry.current:
                        return f"{entry.current:.1f}°C"

    except Exception:
        pass

    return "N/A"


def load():
    """
    Windowsissa ei ole Linuxin load averagea.
    Näytetään sen sijaan CPU-käyttö.
    """

    try:
        cpu = psutil.cpu_percent(interval=None)
        return f"CPU {cpu:.1f}%"
    except Exception:
        return "unknown"


def get_iface():
    """
    Etsii aktiivisimman verkkoliitännän.
    """

    try:
        counters = psutil.net_io_counters(pernic=True)

        best = None
        best_total = 0

        for name, stats in counters.items():
            total = stats.bytes_sent + stats.bytes_recv

            if total > best_total:
                best_total = total
                best = name

        return best

    except Exception:
        return None


def read_net(iface):
    if not iface:
        return 0, 0

    try:
        counters = psutil.net_io_counters(pernic=True)

        if iface in counters:
            stats = counters[iface]
            return stats.bytes_recv, stats.bytes_sent

    except Exception:
        pass

    return 0, 0


def uptime():
    try:
        seconds = time.time() - psutil.boot_time()

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)

        days = hours // 24
        hours %= 24

        if days > 0:
            return f"{days}d {hours}h {minutes}m"

        return f"{hours}h {minutes}m"

    except Exception:
        return "unknown"


def ram():
    try:
        mem = psutil.virtual_memory()

        used = mem.used // (1024 ** 2)
        total = mem.total // (1024 ** 2)

        return f"{used}MiB / {total}MiB"

    except Exception:
        return "unknown"


def disk():
    try:
        d = shutil.disk_usage("C:\\")

        used = (d.total - d.free) // (1024 ** 3)
        total = d.total // (1024 ** 3)

        return f"{used}GiB / {total}GiB"

    except Exception:
        return "unknown"


# ─────────────────────────────────────────────
# ANIMATION
# ─────────────────────────────────────────────

def frame(scale, flip):
    out = []

    tw = max(2, int(w * scale))
    cx = w / 2

    for row in logo:

        line = ""

        for j in range(tw):

            x = cx + (j - tw / 2) / scale
            xi = int(x + 0.5)

            if 0 <= xi < w:
                line += row[xi]
            else:
                line += " "

        if flip:
            line = line[::-1]

        out.append(line)

    return out


# ─────────────────────────────────────────────
# INFO PANEL
# ─────────────────────────────────────────────

def info(down, up):

    now = datetime.datetime.now().strftime("%H:%M:%S")

    return [
        f"OS:       {get_os()}",
        f"Kernel:   {platform.release()}",
        f"Arch:     {platform.machine()}",
        f"Uptime:   {uptime()}",
        f"RAM:      {ram()}",
        f"Disk:     {disk()}",
        f"CPU:      {get_cpu()}",
        f"Temp:     {temp()}",
        f"Load:     {load()}",
        f"Net:      ↓ {down:.0f} KB/s ↑ {up:.0f} KB/s",
        f"Time:     {now}",
        f"Host:     {socket.gethostname()}",
        f"User:     {getpass.getuser()}",
        f"Platform: {platform.system()}",
    ]


def footer():

    return [
        "Sector:   C - Lambda Complex",
        "Clearance:Level 3",
        "Device:   Black Mesa Field Notebook",
        "System Status: stable",
    ]


# ─────────────────────────────────────────────
# WINDOWS KEY INPUT
# ─────────────────────────────────────────────

def key_pressed():

    if msvcrt is None:
        return False

    return msvcrt.kbhit()


def read_key():

    if msvcrt is None:
        return

    try:
        msvcrt.getch()
    except Exception:
        pass


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():

    cols, rows = shutil.get_terminal_size()

    # Estetään liian pieni terminaali
    if cols < 70:
        cols = 70

    top = 5
    left = 4

    right = int(cols * 0.55) - 1

    max_w = right - left - 2
    max_info = cols - right - 3

    iface = get_iface()

    prx, ptx = read_net(iface)

    last_measure = time.time()

    down = 0
    up = 0

    # Luodaan animaatiokehykset
    frames = []

    for k in range(120):

        angle = 2 * math.pi * k / 120

        scale = 0.2 + 0.8 * abs(math.cos(angle))
        flip = math.cos(angle) < 0

        frames.append(frame(scale, flip))

    draw_w = min(
        max(len(line) for f in frames for line in f),
        max_w
    )

    # Alternate screen + kursori piiloon
    sys.stdout.write(
        ALT_ON +
        HIDE_CURSOR +
        CLEAR +
        HOME
    )

    title = "BLACK MESA RESEARCH FACILITY"
    sub = "Lambda Complex - Field Operations Terminal"

    sys.stdout.write(
        mv(1, max(1, (cols - len(title)) // 2)) +
        ORANGE +
        title +
        RESET
    )

    sys.stdout.write(
        mv(2, max(1, (cols - len(sub)) // 2)) +
        ORANGE +
        sub +
        RESET
    )

    sys.stdout.write(
        mv(3, 1) +
        ORANGE +
        "─" * cols +
        RESET
    )

    lower = top + h + 1

    sys.stdout.write(
        mv(lower, 1) +
        ORANGE +
        "─" * cols +
        RESET
    )

    ft = lower + 1

    for i, line in enumerate(footer()):

        sys.stdout.write(
            mv(ft + i, max(1, (cols - len(line)) // 2)) +
            ORANGE +
            line +
            RESET
        )

    hint = "[ Press any key to exit ]"

    sys.stdout.write(
        mv(
            ft + len(footer()) + 1,
            max(1, (cols - len(hint)) // 2)
        ) +
        ORANGE +
        hint +
        RESET
    )

    sys.stdout.flush()

    try:

        frame_index = 0

        while True:

            # Windowsissa msvcrt hoitaa näppäimistön
            if key_pressed():
                read_key()
                break

            now = time.time()

            # Verkkonopeuden päivitys
            if now - last_measure >= 0.1:

                rx, tx = read_net(iface)

                dt = now - last_measure

                if dt > 0:

                    down = (rx - prx) / 1024 / dt
                    up = (tx - ptx) / 1024 / dt

                    # Suojaus mahdollisia laskuvirheitä vastaan
                    down = max(0, down)
                    up = max(0, up)

                prx = rx
                ptx = tx

                last_measure = now

            f = frames[frame_index]

            data = info(down, up)

            # Tyhjennä logoalue
            for i in range(h):

                sys.stdout.write(
                    mv(top + i, left) +
                    " " * draw_w
                )

            # Oikean puolen tiedot
            for i, line in enumerate(data):

                sys.stdout.write(
                    mv(top + i, right) +
                    ORANGE +
                    line.ljust(max_info) +
                    RESET
                )

            # Logo
            for i in range(h):

                line = f[i]

                if len(line) > draw_w:

                    cut = (len(line) - draw_w) // 2

                    line = line[
                        cut:
                        cut + draw_w
                    ]

                sys.stdout.write(
                    mv(top + i, left) +
                    ORANGE +
                    line.center(draw_w) +
                    RESET
                )

            sys.stdout.flush()

            frame_index = (frame_index + 1) % len(frames)

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    finally:

        # Palautetaan normaali terminaali
        sys.stdout.write(
            RESET +
            SHOW_CURSOR +
            ALT_OFF
        )

        sys.stdout.flush()


if __name__ == "__main__":
    main()
