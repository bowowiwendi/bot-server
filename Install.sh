#!/bin/bash

# Script untuk menginstal bot Telegram dan mengatur service systemd

# Meminta input dari pengguna
read -p "Masukkan Username : " USER
read -p "Masukkan Token Bot Telegram: " BOT_TOKEN
read -p "Masukkan User ID Admin (pisahkan dengan spasi jika lebih dari satu): " ADMIN_IDS

#!/bin/bash

# Script untuk menginstal bot Telegram dan mengatur service systemd

# Direktori instalasi
INSTALL_DIR="/opt/telegram_bot"
SERVICE_NAME="telegram_bot.service"

# Update dan install dependensi
echo -e "Mengupdate sistem dan menginstal dependensi..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# Buat direktori instalasi
echo -e "Membuat direktori instalasi di $INSTALL_DIR..."
sudo mkdir -p $INSTALL_DIR
sudo chown $USER:$USER $INSTALL_DIR
cd $INSTALL_DIR

# Buat virtual environment
echo -e "Membuat virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install library yang diperlukan
echo -e "Menginstal library Python..."
pip install python-telegram-bot paramiko

# Download script bot
echo -e "Mengunduh script bot..."
wget -O bot-server.py https://raw.githubusercontent.com/bowowiwendi/bot-server/refs/heads/main/bot-server.py

# Ganti token dan admin ID di script bot
echo -e "Mengatur token dan admin ID..."
sed -i "s/YOUR_TOKEN/$BOT_TOKEN/g" bot-server.py
sed -i "s/ADMIN_IDS = \[.*\]/ADMIN_IDS = \[$(echo $ADMIN_IDS | sed 's/ /, /g')\]/g" bot-server.py

# Buat service systemd
echo -e "Membuat service systemd..."
cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME > /dev/null
[Unit]
Description=Telegram Bot Manager
After=network.target

[Service]
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/bot-server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd dan start service
echo -e "Mengaktifkan dan menjalankan service..."
systemctl daemon-reload
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# Tampilkan status service
echo -e "Memeriksa status service..."
#systemctl status $SERVICE_NAME

echo -e "Instalasi selesai! Bot Telegram berhasil diinstal dan dijalankan sebagai service."
