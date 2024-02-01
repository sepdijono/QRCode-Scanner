# QRCode-Scanner

**This project consists two repositories** 

* QRCode-Scanner, contains "scanner-side" (this repo)
* QRCode-Server, contains "server-side"

Notes: I use same environment for these two repos

scan.py : single camera processing & simple output without implement PyQt5 & threading

This output come from scan.py
![Selection_613](https://github.com/sepdijono/QRCode-Scanner/assets/54463742/4cde3201-41e6-4929-945f-453154904f86)


scan_multiple_cam.py : this version implements multiple camera image processing with PyQt5 threading

This output come from scan_multiple_cam.py
![Workspace 1_007](https://github.com/sepdijono/QRCode-Scanner/assets/54463742/a13f751c-28bd-4809-80a3-f58e61081878)

This output come from scan_user_attendance.py
![Selection_886](https://github.com/sepdijono/QRCode-Scanner/assets/54463742/856bf0f5-2c2d-4aaf-889d-8a8620c1267c)




QRCode-scanner use OpenCV2 with GPU support, all scanned qr-codes will be shown in a box with respective data on it. There is only two qr-code types: 
1. Registered qr-code will shown the data (username, full name, address, scanned location)
2. Unregistered qr-code will be appeared as "Tidak terdaftar"
   
However, unfortunately this is just prototype so it comes without admin dashboard whatsoever. 

Oke thats all hope you find something useful

Regards: pyy

