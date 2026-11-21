#!/usr/bin/env python3
# lang: Python3, file: toolkit.py, target: Kali/Debian Linux
# menu-driven launcher — subprocess.run per tool, install check built in

import os
import sys
import subprocess
from time import sleep

# ─────────────────────────────────────────────
# TRUE-COLOR RAINBOW ENGINE
# ─────────────────────────────────────────────

def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def bg_rgb(r, g, b):
    return f"\033[48;2;{r};{g};{b}m"

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
ITALIC = "\033[3m"

# Static palette (fallback / accents)
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"

B_RED    = BOLD + RED
B_GREEN  = BOLD + GREEN
B_YELLOW = BOLD + YELLOW
B_CYAN   = BOLD + CYAN
B_WHITE  = BOLD + WHITE
B_MAGENTA= BOLD + MAGENTA

def rainbow_char(ch, pos, offset=0):
    """Return a single character wrapped in a rainbow color based on position."""
    import math
    hue = (pos * 0.08 + offset) % 1.0
    # HSV → RGB, S=1, V=1
    h = hue * 6
    i = int(h)
    f = h - i
    q = int((1 - f) * 255)
    t = int(f * 255)
    v = 255
    palettes = [
        (v, t, 0), (q, v, 0), (0, v, t),
        (0, q, v), (t, 0, v), (v, 0, q),
    ]
    r, g, b = palettes[i % 6]
    return rgb(r, g, b) + ch + RESET

def rainbow_str(text, offset=0):
    """Colorize every character of text in a smooth rainbow."""
    out = ""
    pos = 0
    for ch in text:
        if ch == " ":
            out += ch
        else:
            out += rainbow_char(ch, pos, offset)
            pos += 1
    return out

def gradient_line(text, r1, g1, b1, r2, g2, b2):
    """Left-to-right gradient across text."""
    n = max(len(text) - 1, 1)
    out = ""
    for i, ch in enumerate(text):
        t = i / n
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        out += rgb(r, g, b) + ch
    return out + RESET

# ─────────────────────────────────────────────
# BANNER  (rainbow gradient, line by line)
# ─────────────────────────────────────────────

_LOGO_LINES = [
    r"  ████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗",
    r"  ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝",
    r"     ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║   ",
    r"     ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║   ",
    r"     ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║   ",
    r"     ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝   ",
]

# Rainbow gradient stops per row: (r1,g1,b1) → (r2,g2,b2)
_ROW_GRADIENTS = [
    ((255, 0,  128), (255, 80,  0)),   # hot pink → orange
    ((255, 80,  0),  (220, 220, 0)),   # orange   → yellow
    ((220, 220, 0),  (0,  220, 80)),   # yellow   → lime
    ((0,  220, 80),  (0,  180, 255)),  # lime     → cyan
    ((0,  180, 255), (120, 0,  255)),  # cyan     → violet
    ((120, 0,  255), (255, 0,  128)),  # violet   → pink (wraps)
]

def build_banner():
    w = 62
    border_top    = gradient_line("  ╔" + "═" * w + "╗", 255, 0, 128, 120, 0, 255)
    border_blank  = gradient_line("  ║" + " " * w + "║", 255, 0, 128, 120, 0, 255)
    border_bottom = gradient_line("  ╚" + "═" * w + "╝", 120, 0, 255, 255, 0, 128)

    lines = ["\n", border_top, border_blank]
    for row, line in enumerate(_LOGO_LINES):
        (r1, g1, b1), (r2, g2, b2) = _ROW_GRADIENTS[row]
        # pad line inside box
        inner = line.ljust(w)
        colored = gradient_line("  ║" + inner + "║", r1, g1, b1, r2, g2, b2)
        lines.append(BOLD + colored + RESET)
    lines.append(border_blank)
    lines.append(border_bottom)

    # tagline with cycling rainbow
    tagline   = rainbow_str("  ══[ All-in-One Penetration Testing Framework ]══")
    sysline   = (
        rgb(100,100,100) + "  ◈ Platform: " + RESET + rgb(180,180,180) + "Kali / Debian" + RESET +
        rgb(100,100,100) + "   ◈ Mode: "    + RESET + rgb(180,180,180) + "Interactive"   + RESET +
        rgb(100,100,100) + "   ◈ "          + RESET + rgb(255,80,80)   + "Root Required" + RESET
    )
    lines += [tagline, sysline, ""]
    return "\n".join(lines)

BANNER = build_banner()

# ─────────────────────────────────────────────
# SECTION ICONS  (each gets its own gradient)
# ─────────────────────────────────────────────

ICONS = {
    "Information Gathering": ("◉", (0,  200, 255), (0,   80, 255)),
    "Password Attacks":      ("⚿", (255, 60,  60), (255,160,  0)),
    "Wireless Testing":      ("◈", (0,  255, 160), (0,  200, 255)),
    "Exploitation Tools":    ("⚠", (255, 60,   0), (255,  0, 100)),
    "Sniffing & Spoofing":   ("⊛", (180,  0, 255), (255, 60, 200)),
    "Web Hacking":           ("⊗", (255,200,  0),  (200,255,  0)),
    "Private Web Hacking":   ("⊕", (0,  255,  80), (0,  200,  0)),
    "Post Exploitation":     ("◆", (255,  0, 100), (120,  0, 255)),
    "Contributors":          ("♥", (255,100, 180), (255,  0,  80)),
    "Install & Update":      ("⚙", (100,200, 255), (0,  150, 255)),
}

def icon_color(label):
    entry = ICONS.get(label, ("·", (200,200,200), (120,120,120)))
    sym, (r1,g1,b1), _ = entry
    return rgb(r1,g1,b1) + BOLD + sym + RESET

def label_gradient(label):
    entry = ICONS.get(label, ("·", (200,200,200), (120,120,120)))
    _, (r1,g1,b1), (r2,g2,b2) = entry
    return gradient_line(label, r1, g1, b1, r2, g2, b2)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def clear():
    os.system("clear")

def banner():
    clear()
    print(BANNER)

def divider(r1=80, g1=0, b1=200, r2=0, g2=180, b2=255):
    line = "  " + "─" * 68
    print(BOLD + gradient_line(line, r1, g1, b1, r2, g2, b2) + RESET)

def status(msg, kind="info"):
    tags = {
        "info":  (rgb(0,  180, 255), "●"),
        "ok":    (rgb(0,  255, 100), "✔"),
        "warn":  (rgb(255,200,   0), "⚠"),
        "error": (rgb(255,  60,  60),"✖"),
        "prompt":(rgb(200,  60, 255),"?"),
    }
    color, sym = tags.get(kind, (WHITE, "·"))
    print(f"  {color}{BOLD}{sym}{RESET}  {msg}")

def pause():
    print()
    divider(255, 0, 128, 120, 0, 255)
    input(f"  {DIM}{rgb(180,180,180)}[ Press Enter to return to menu... ]{RESET}  ")

def run(cmd):
    try:
        prefix = gradient_line("  ┌── ", 255, 0, 128, 0, 180, 255)
        suffix = gradient_line("  └── done", 0, 180, 255, 255, 0, 128)
        short  = cmd[:55] + ("…" if len(cmd) > 55 else "")
        print(f"\n{prefix}{DIM}{short}{RESET}")
        subprocess.run(cmd, shell=True)
        print(suffix + RESET)
    except KeyboardInterrupt:
        print(f"\n  {B_RED}[ ✖ Interrupted ]{RESET}")

def check_install(pkg, install_cmd=None):
    result = subprocess.run(f"which {pkg}", shell=True, capture_output=True)
    if result.returncode != 0:
        status(f"{rgb(255,200,0)}{pkg}{RESET} not found on this system.", "warn")
        if install_cmd:
            g = gradient_line(f"  Install {pkg}?", 255, 60, 0, 255, 0, 150)
            choice = input(f"{g} {DIM}[{RESET}{rgb(0,255,80)}y{RESET}{DIM}/{RESET}{rgb(255,60,60)}n{RESET}{DIM}]{RESET}: ").lower()
            if choice == 'y':
                status(f"Installing {pkg}…", "info")
                run(install_cmd)
        return False
    status(f"{pkg} is available.", "ok")
    return True

def prompt(label):
    arrow = gradient_line("  ▶ ", 255, 0, 200, 0, 200, 255)
    return input(f"{arrow}{BOLD}{WHITE}{label}{RESET}: {WHITE}")

def _box_header(title, w=64):
    """Draw a gradient double-line box around a title."""
    entry = ICONS.get(title, ("·", (0,180,255), (120,0,255)))
    sym, (r1,g1,b1), (r2,g2,b2) = entry
    inner = f"  {sym}  {title}  {sym}  "
    pad   = max(0, w - len(inner))
    top    = gradient_line("  ╔" + "═" * w + "╗", r1,g1,b1, r2,g2,b2)
    mid    = gradient_line("  ║", r1,g1,b1, r2,g2,b2) + BOLD + WHITE + inner + " " * pad + RESET + gradient_line("║", r2,g2,b2, r1,g1,b1)
    bot    = gradient_line("  ╚" + "═" * w + "╝", r2,g2,b2, r1,g1,b1)
    print(f"\n{top}\n{mid}\n{bot}\n")

def menu(title, options):
    while True:
        banner()
        _box_header(title)

        for i, (label, _) in enumerate(options, 1):
            num   = gradient_line(f"[{i:02d}]", 0, 255, 100, 0, 180, 255)
            arrow = rgb(80, 80, 120) + "›" + RESET
            lbl   = label_gradient(label)
            print(f"  {BOLD}{num}{RESET} {arrow} {lbl}")

        back = gradient_line("[00]", 255, 60, 60, 255, 0, 100)
        print(f"\n  {BOLD}{back}{RESET} {DIM}↩  Back{RESET}\n")
        divider()

        ps = (gradient_line("root", 255,80,80, 255,0,100) + rgb(80,80,120) + "@" + RESET +
              gradient_line("toolkit", 0,180,255, 120,0,255) + rgb(80,80,120) + ":~# " + RESET + WHITE)
        choice = input(f"\n  {ps}").strip()
        print(RESET, end="")

        if choice == "00" or choice.lower() == "back":
            return
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                banner()
                lbl = options[idx][0]
                bar = gradient_line("  ┌──[ " + lbl + " ]" + "─" * max(0, 50-len(lbl)) + "┐",
                                    255, 0, 128, 0, 180, 255)
                print(f"\n{BOLD}{bar}{RESET}\n")
                options[idx][1]()
                print(f"\n{BOLD}{gradient_line('  └' + '─'*54 + '┘', 0,180,255, 255,0,128)}{RESET}")
                pause()
            else:
                status("Invalid option.", "warn"); sleep(0.6)
        else:
            status("Enter a number.", "warn"); sleep(0.6)

# ─────────────────────────────────────────────
# INFORMATION GATHERING
# ─────────────────────────────────────────────

def run_nmap():
    target = prompt("Target (IP/domain)")
    flags  = prompt("Flags (Enter → -sV -sC)") or "-sV -sC"
    run(f"nmap {flags} {target}")

def run_setoolkit_info():
    check_install("setoolkit", "apt install set -y")
    run("setoolkit")

def host_to_ip():
    host = prompt("Hostname")
    run(f"python3 -c \"import socket; print(socket.gethostbyname('{host}'))\"")

def run_wpscan():
    check_install("wpscan", "gem install wpscan")
    url = prompt("WordPress URL")
    run(f"wpscan --url {url} --enumerate u,p,t")

def run_cms_scanner():
    check_install("cmseek", "git clone https://github.com/Tuhinshubhra/CMSeeK && cd CMSeeK && pip3 install -r requirements.txt")
    target = prompt("Target URL")
    run(f"python3 CMSeeK/cmseek.py -u {target}")

def run_xsstrike():
    check_install("python3")
    url = prompt("Target URL")
    run(f"python3 XSStrike/xsstrike.py -u {url}")

def run_dork():
    dork = prompt("Google Dork query")
    run(f"python3 Dork-Scan/dork_scanner.py --dork \"{dork}\"")

def scan_server_users():
    target = prompt("Target URL")
    run(f"curl -s {target}/~admin/ -o /dev/null -w '%{{http_code}}'")
    run(f"python3 UserScan/scan.py -u {target}")

def run_crips():
    check_install("crips")
    run("crips")

INFO_GATHERING = [
    ("Nmap",                              run_nmap),
    ("Setoolkit",                         run_setoolkit_info),
    ("Host To IP",                        host_to_ip),
    ("WPScan",                            run_wpscan),
    ("CMS Scanner",                       run_cms_scanner),
    ("XSStrike",                          run_xsstrike),
    ("Dork - Google Dorks Passive Audit", run_dork),
    ("Scan A Server's Users",             scan_server_users),
    ("Crips",                             run_crips),
]

# ─────────────────────────────────────────────
# PASSWORD ATTACKS
# ─────────────────────────────────────────────

def run_cupp():
    check_install("cupp", "apt install cupp -y")
    run("cupp -i")

def run_ncrack():
    check_install("ncrack", "apt install ncrack -y")
    target   = prompt("Target (IP:port)")
    service  = prompt("Service (ssh/ftp/rdp)")
    wordlist = prompt("Wordlist path")
    run(f"ncrack -U {wordlist} -P {wordlist} {service}://{target}")

PASSWORD_ATTACKS = [
    ("Cupp  - Custom Wordlist Generator", run_cupp),
    ("Ncrack - Network Auth Cracker",     run_ncrack),
]

# ─────────────────────────────────────────────
# WIRELESS TESTING
# ─────────────────────────────────────────────

def run_reaver():
    check_install("reaver", "apt install reaver -y")
    iface = prompt("Interface (e.g. wlan0mon)")
    bssid = prompt("BSSID")
    run(f"reaver -i {iface} -b {bssid} -vv")

def run_pixiewps():
    check_install("pixiewps", "apt install pixiewps -y")
    run("pixiewps --help")
    pke     = prompt("PKE")
    pkr     = prompt("PKR")
    e_hash1 = prompt("E-Hash1")
    e_hash2 = prompt("E-Hash2")
    authkey = prompt("AuthKey")
    run(f"pixiewps -e {pke} -r {pkr} -s {e_hash1} -z {e_hash2} -a {authkey} -n 0")

def run_bt_honeypot():
    check_install("bluez", "apt install bluez -y")
    run("hciconfig hci0 up")
    name = prompt("Honeypot name (Enter → iPhone13Pro)") or "iPhone13Pro"
    run(f"hciconfig hci0 name '{name}' && hciconfig hci0 piscan")
    status(f"Bluetooth honeypot active as: {BOLD}{WHITE}{name}{RESET}", "ok")
    run("hcidump -i hci0")

WIRELESS_TESTING = [
    ("Reaver - WPS Brute Force",    run_reaver),
    ("Pixiewps - WPS Offline Atk",  run_pixiewps),
    ("Bluetooth Honeypot",          run_bt_honeypot),
]

# ─────────────────────────────────────────────
# EXPLOITATION TOOLS
# ─────────────────────────────────────────────

def run_atscan():
    target = prompt("Target")
    run(f"perl atscan.pl --target {target} --dork '' --level 3")

def run_sqlmap():
    check_install("sqlmap", "apt install sqlmap -y")
    url = prompt("Target URL")
    run(f"sqlmap -u \"{url}\" --dbs --batch --random-agent")

def run_shellnoob():
    check_install("shellnoob")
    run("shellnoob --get-sh --intel")

def run_commix():
    check_install("commix", "apt install commix -y")
    url = prompt("Target URL")
    run(f"commix --url=\"{url}\"")

def run_ftp_bypass():
    target = prompt("FTP host")
    run(f"hydra -l anonymous -p anonymous ftp://{target}")
    run(f"ftp {target}")

def run_jboss_autopwn():
    target = prompt("JBoss target URL")
    run(f"python3 jboss-autopwn.py {target}")

EXPLOITATION = [
    ("ATSCAN",          run_atscan),
    ("SQLMap",          run_sqlmap),
    ("ShellNoob",       run_shellnoob),
    ("Commix",          run_commix),
    ("FTP Auto Bypass", run_ftp_bypass),
    ("JBoss Autopwn",   run_jboss_autopwn),
]

# ─────────────────────────────────────────────
# SNIFFING & SPOOFING
# ─────────────────────────────────────────────

def run_setoolkit_sniff():
    check_install("setoolkit", "apt install set -y")
    run("setoolkit")

def run_sslstrip():
    check_install("sslstrip", "apt install sslstrip -y")
    iface = prompt("Interface")
    run(f"arpspoof -i {iface} -t $(ip route | grep default | awk '{{print $3}}') &")
    run(f"sslstrip -l 8080")

def run_pypisher():
    target = prompt("Target email/host")
    run(f"python3 pyPISHER/pyPISHER.py -t {target}")

def run_smtp_mailer():
    run("python3 smtp-mailer/mailer.py")

SNIFFING_SPOOFING = [
    ("Setoolkit",   run_setoolkit_sniff),
    ("SSLstrip",    run_sslstrip),
    ("pyPISHER",    run_pypisher),
    ("SMTP Mailer", run_smtp_mailer),
]

# ─────────────────────────────────────────────
# WEB HACKING
# ─────────────────────────────────────────────

def run_drupal_hack():
    target = prompt("Drupal URL")
    run(f"python3 drupal-hack/exploit.py -u {target}")

def run_inurlbr():
    dork = prompt("Dork")
    run(f"php inurlbr.php --dork \"{dork}\" -s results.txt")

def run_wp_joomla_scanner():
    target = prompt("Target URL")
    run(f"wpscan --url {target} --enumerate")

def run_gravity_form():
    target = prompt("Target URL")
    run(f"python3 gravity-scan/scan.py -u {target}")

def run_file_upload_checker():
    target = prompt("Upload endpoint URL")
    run(f"python3 file-upload-checker/check.py -u {target}")

def run_wp_exploit_scanner():
    target = prompt("WordPress URL")
    run(f"wpscan --url {target} --plugins-detection aggressive")

def run_wp_plugins_scanner():
    target = prompt("WordPress URL")
    run(f"wpscan --url {target} --enumerate p --plugins-detection mixed")

def run_shell_finder():
    target = prompt("Target URL")
    run(f"python3 shell-finder/finder.py -u {target}")

def run_joomla_rce():
    target = prompt("Joomla URL (1.5-3.4.5)")
    run(f"python3 joomla-rce/exploit.py -u {target}")

def run_vbulletin_rce():
    target = prompt("vBulletin URL (5.x)")
    run(f"python3 vbulletin-rce/exploit.py -u {target}")

def run_brutex():
    check_install("brutex")
    target = prompt("Target IP")
    run(f"bash brutex {target}")

def run_arachni():
    check_install("arachni")
    target = prompt("Target URL")
    run(f"arachni {target} --report-save-path=report.afr")

WEB_HACKING = [
    ("Drupal Hacking",                           run_drupal_hack),
    ("Inurlbr",                                  run_inurlbr),
    ("WordPress & Joomla Scanner",               run_wp_joomla_scanner),
    ("Gravity Form Scanner",                     run_gravity_form),
    ("File Upload Checker",                      run_file_upload_checker),
    ("WordPress Exploit Scanner",                run_wp_exploit_scanner),
    ("WordPress Plugins Scanner",                run_wp_plugins_scanner),
    ("Shell and Directory Finder",               run_shell_finder),
    ("Joomla 1.5-3.4.5 RCE",                    run_joomla_rce),
    ("vBulletin 5.x RCE",                        run_vbulletin_rce),
    ("BruteX - Brute Force All Services",        run_brutex),
    ("Arachni - Web App Security Scanner",       run_arachni),
]

# ─────────────────────────────────────────────
# PRIVATE WEB HACKING
# ─────────────────────────────────────────────

def get_all_websites():
    ip = prompt("Server IP")
    run(f"python3 -c \"import requests; r=requests.get('https://api.hackertarget.com/reverseiplookup/?q={ip}'); print(r.text)\"")

def get_joomla_sites():
    ip = prompt("Server IP")
    run(f"python3 cms-finder/find.py --ip {ip} --cms joomla")

def get_wp_sites():
    ip = prompt("Server IP")
    run(f"python3 cms-finder/find.py --ip {ip} --cms wordpress")

def find_control_panel():
    target = prompt("Target domain")
    panels = ["cpanel", "admin", "administrator", "plesk", "whm", "webmin",
              "directadmin", "panel", "cp", "controlpanel"]
    status("Probing panel paths…", "info")
    for p in panels:
        url = f"http://{target}/{p}"
        run(f"curl -s -o /dev/null -w '{url} -> %{{http_code}}\n' {url}")

def find_zip_files():
    target = prompt("Target URL")
    zips = ["backup.zip", "www.zip", "site.zip", "files.zip", "backup.tar.gz",
            "public_html.zip", "db.sql", "dump.sql"]
    status("Checking for exposed archives…", "info")
    for z in zips:
        run(f"curl -s -o /dev/null -w '{z} -> %{{http_code}}\n' {target}/{z}")

def find_upload_file():
    target = prompt("Target URL")
    uploads = ["upload.php", "filemanager.php", "upload/", "uploads/", "file_upload.php"]
    status("Scanning upload endpoints…", "info")
    for u in uploads:
        run(f"curl -s -o /dev/null -w '{u} -> %{{http_code}}\n' {target}/{u}")

def get_server_users():
    target = prompt("Target URL")
    run(f"python3 user-enum/enum.py -u {target}")

def sqli_scanner():
    target = prompt("Target URL")
    run(f"sqlmap -u \"{target}\" --dbs --batch --level=3 --risk=2")

def ports_scan_range():
    target = prompt("Target IP")
    start  = prompt("Start port")
    end    = prompt("End port")
    run(f"nmap -p {start}-{end} {target}")

def ports_scan_common():
    target = prompt("Target IP")
    run(f"nmap -F {target}")

def get_server_info():
    target = prompt("Target domain/IP")
    run(f"curl -sI {target}")
    run(f"nmap -sV -O {target}")

def bypass_cloudflare():
    target = prompt("Domain")
    run(f"python3 -c \"import requests; r=requests.get('https://api.hackertarget.com/dnslookup/?q={target}'); print(r.text)\"")
    run(f"python3 cloudflare-bypass/bypass.py -d {target}")

PRIVATE_WEB = [
    ("Get All Websites on Server",    get_all_websites),
    ("Get Joomla Websites",           get_joomla_sites),
    ("Get WordPress Websites",        get_wp_sites),
    ("Control Panel Finder",          find_control_panel),
    ("Zip Files Finder",              find_zip_files),
    ("Upload File Finder",            find_upload_file),
    ("Get Server Users",              get_server_users),
    ("SQLi Scanner",                  sqli_scanner),
    ("Ports Scan (range)",            ports_scan_range),
    ("Ports Scan (common)",           ports_scan_common),
    ("Get Server Info",               get_server_info),
    ("Bypass Cloudflare",             bypass_cloudflare),
]

# ─────────────────────────────────────────────
# POST EXPLOITATION
# ─────────────────────────────────────────────

def run_shell_checker():
    shell_url = prompt("Shell URL")
    run(f"curl -s {shell_url} | head -50")
    cmd = prompt("Test command (Enter → id)") or "id"
    run(f"curl -s '{shell_url}?cmd={cmd}'")

def run_poet():
    check_install("poet")
    host = prompt("C2 host (your IP)")
    port = prompt("Port (Enter → 443)") or "443"
    run(f"python3 poet/poet.py -s {host}:{port}")

def run_weeman():
    run("python3 Weeman/weeman.py")

POST_EXPLOITATION = [
    ("Shell Checker", run_shell_checker),
    ("POET",          run_poet),
    ("Weeman",        run_weeman),
]

# ─────────────────────────────────────────────
# INSTALL & UPDATE
# ─────────────────────────────────────────────

def install_all():
    pkgs = ["nmap","sqlmap","wpscan","commix","reaver","pixiewps",
            "ncrack","cupp","sslstrip","arachni","set"]
    status("Updating apt package lists…", "info")
    run(f"apt update && apt install -y {' '.join(pkgs)}")
    py_pkgs = ["requests", "colorama", "bs4", "mechanize"]
    status("Installing Python dependencies…", "info")
    run(f"pip3 install {' '.join(py_pkgs)}")
    status("Core packages installed.", "ok")

def update_toolkit():
    if os.path.exists(".git"):
        status("Pulling latest changes…", "info")
        run("git pull")
        status("Toolkit updated.", "ok")
    else:
        status("Not a git repo — pull manually.", "warn")

INSTALL_UPDATE = [
    ("Install All Core Tools", install_all),
    ("Update Toolkit",         update_toolkit),
]

# ─────────────────────────────────────────────
# CONTRIBUTORS
# ─────────────────────────────────────────────

def show_contributors():
    top  = gradient_line("  ╔" + "═"*42 + "╗", 255, 100, 180, 255, 0, 80)
    mid  = gradient_line("  ║" + "       ♥  Contributors  ♥       " + "          ║", 255,0,80, 255,100,180)
    bot  = gradient_line("  ╚" + "═"*42 + "╝", 255, 0, 80, 255, 100, 180)
    print(f"\n{BOLD}{top}\n{mid}\n{bot}{RESET}\n")
    print(f"  {gradient_line('AIwolfie', 0,200,255, 120,0,255)}      {DIM}—{RESET} framework design, feature requests")
    print(f"  {gradient_line('Noob',     255,80,0, 255,200,0)}          {DIM}—{RESET} build, wiring, the whole file\n")
    print(f"  {DIM}{rgb(150,150,150)}Tool credits go to their respective original authors.")
    print(f"  This framework is a launcher — all tools are third-party.{RESET}\n")

# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

MAIN_MENU = [
    ("Information Gathering",   lambda: menu("Information Gathering",   INFO_GATHERING)),
    ("Password Attacks",        lambda: menu("Password Attacks",        PASSWORD_ATTACKS)),
    ("Wireless Testing",        lambda: menu("Wireless Testing",        WIRELESS_TESTING)),
    ("Exploitation Tools",      lambda: menu("Exploitation Tools",      EXPLOITATION)),
    ("Sniffing & Spoofing",     lambda: menu("Sniffing & Spoofing",     SNIFFING_SPOOFING)),
    ("Web Hacking",             lambda: menu("Web Hacking",             WEB_HACKING)),
    ("Private Web Hacking",     lambda: menu("Private Web Hacking",     PRIVATE_WEB)),
    ("Post Exploitation",       lambda: menu("Post Exploitation",       POST_EXPLOITATION)),
    ("Contributors",            lambda: (banner(), show_contributors(), pause())),
    ("Install & Update",        lambda: menu("Install & Update",        INSTALL_UPDATE)),
]

def main():
    while True:
        banner()

        # ── Main menu box ──────────────────────────
        w     = 64
        title = "  ⚡  Main Menu  ⚡  "
        pad   = max(0, w - len(title))
        top   = gradient_line("  ╔" + "═"*w + "╗", 255,0,128, 120,0,255)
        mid   = (gradient_line("  ║", 255,0,128, 120,0,255) + BOLD + WHITE +
                 title + " "*pad + RESET + gradient_line("║", 120,0,255, 255,0,128))
        sep   = gradient_line("  ╠" + "═"*w + "╣", 120,0,255, 255,0,128)
        print(f"{BOLD}{top}\n{mid}\n{sep}{RESET}\n")

        for i, (label, _) in enumerate(MAIN_MENU, 1):
            num  = gradient_line(f"[{i:02d}]", 0, 255, 100, 0, 180, 255)
            ic   = icon_color(label)
            lbl  = label_gradient(label)
            print(f"  {BOLD}{num}{RESET}  {ic}  {lbl}")

        exit_num = gradient_line("[00]", 255, 60, 60, 255, 0, 80)
        print(f"\n  {BOLD}{exit_num}{RESET}  {rgb(80,80,100)}⏻  Exit{RESET}\n")
        divider(255, 0, 128, 120, 0, 255)

        ps = (gradient_line("root", 255,60,60, 255,0,100) +
              rgb(60,60,100) + "@" + RESET +
              gradient_line("toolkit", 0,180,255, 120,0,255) +
              rgb(60,60,100) + ":~# " + RESET + WHITE)
        choice = input(f"\n  {ps}").strip()
        print(RESET, end="")

        if choice == "00" or choice.lower() in ("exit", "q"):
            banner()
            msg = gradient_line("  [ ⏻  Shutting down... goodbye. ]", 255,0,128, 120,0,255)
            print(f"\n{BOLD}{msg}{RESET}\n")
            sleep(0.3)
            sys.exit(0)

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(MAIN_MENU):
                MAIN_MENU[idx][1]()
            else:
                status("Invalid selection.", "warn"); sleep(0.6)
        else:
            status("Enter a valid number.", "warn"); sleep(0.6)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"\n  {BOLD}{gradient_line('[ ✖ Permission Denied ]', 255,0,80, 255,60,0)}{RESET}")
        print(f"  {rgb(200,200,0)}Root privileges required.{RESET}")
        print(f"  {DIM}Run:{RESET}  {BOLD}{WHITE}sudo python3 toolkit.py{RESET}\n")
        sys.exit(1)
    main()