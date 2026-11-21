# OMEGA-7 / VirtualBox Kali launcher

This repository contains a **safe, limited diagnostic edition** and a Windows `.bat` launcher for a Kali Linux guest running in Oracle VirtualBox. All ten requested categories are shown; higher-risk items are **catalog entries only**, not bundled exploits. It is not a GUI application. No automatic tool installations, credential attacks, phishing, or exploitation are performed.

## Requirements
- Windows 10/11, Oracle VirtualBox, Windows OpenSSH Client (`ssh.exe`)
- A Kali Linux VM with NAT on **Adapter 1**, and SSH server installed inside Kali
- Python 3 in Kali; optional `nmap` for limited authorized scans

## First-time setup
1. Find the exact VM name: `"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list vms`. Edit `VM_NAME=Kali Linux` in **both** BAT files to match.
2. Power off the VM completely. Run `SETUP_NAT_FORWARDING.bat` on Windows **once**. It creates a host-only SSH forwarding rule `127.0.0.1:2222 -> guest:22` for NAT Adapter 1. If the rule already exists, do not add it twice. If your VM uses bridged networking, this NAT setup does not apply.
3. Start Kali from VirtualBox normally, open a terminal in Kali, and run:
   ```bash
   sudo apt update
   sudo apt install -y openssh-server python3
   sudo systemctl enable --now ssh
   mkdir -p ~/omega7
   ```
4. Copy `toolkit.py` into `~/omega7/toolkit.py` **inside Kali**. You can use a shared folder, Git clone after pushing the files, or a secure copy command from Windows once SSH is available:
   ```powershell
   scp -P 2222 .\toolkit.py kali@127.0.0.1:~/omega7/toolkit.py
   ```
   Replace `kali` with your actual Kali username in this command and in `START_TOOLKIT.bat`.
5. Optional: in Kali run `sudo apt install -y nmap`.
6. Double-click `START_TOOLKIT.bat` on Windows. The BAT starts the VM headlessly if needed, then opens the toolkit through SSH. The first SSH connection may ask you to confirm the host key. Verify its fingerprint before accepting. Use SSH keys for regular use.

## Troubleshooting
- **VM not found**: update `VM_NAME` in both BAT files.
- **Connection refused**: check Kali `sudo systemctl status ssh`, NAT adapter, port forwarding, and VM boot status.
- **Authentication failed**: change `SSH_USER` to the actual Kali login, or configure SSH keys.
- **No `ssh.exe`**: install Windows Optional Feature **OpenSSH Client**.
- **Rule already exists**: skip the setup BAT; check existing rules with `VBoxManage showvminfo "VM name"`.
- **VM appears running but no SSH**: allow Kali time to boot and retry.
- **GitHub publication**: do not commit passwords, private SSH keys, scan results, or personal data.

## Safety
Only run scans against hosts you own or have explicit permission to test. TCP port scans are limited to 100 ports at a time. Nmap runs with fixed arguments (`-sT -Pn -p 22,80,443`). No shell interpolation is used for target input. HTTPS header checks do not follow redirects. The `toolkit.py` program does not require root.

## Licensing
The supplied original toolkit code is **not** redistributed here because this is a separately authored limited edition. Before publishing a repository based on third-party projects, review each project's license and attribution requirements.
