#!/bin/bash

# Script untuk menginstal bot Telegram dan mengatur service systemd

# Fungsi untuk menampilkan pesan
function log_message {
    echo -e "\n[INFO] $1"
}

# Meminta input dari pengguna
read -p "Masukkan Token Bot Telegram: " BOT_TOKEN
read -p "Masukkan User ID Admin (pisahkan dengan spasi jika lebih dari satu): " ADMIN_IDS

# Direktori instalasi
INSTALL_DIR="/opt/telegram_bot"
SERVICE_NAME="telegram_bot.service"

# Update dan install dependensi
log_message "Mengupdate sistem dan menginstal dependensi..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# Buat direktori instalasi
log_message "Membuat direktori instalasi di $INSTALL_DIR..."
sudo mkdir -p $INSTALL_DIR
sudo chown $USER:$USER $INSTALL_DIR
cd $INSTALL_DIR

# Buat virtual environment
log_message "Membuat virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install library yang diperlukan
log_message "Menginstal library Python..."
pip install python-telegram-bot paramiko

# Download script bot
log_message "Mengunduh script bot..."
wget -O bot_manager.py https://raw.githubusercontent.com/username/repository/main/bot_manager.py

# Ganti token dan admin ID di script bot
log_message "Mengatur token dan admin ID..."
sed -i "s/YOUR_TOKEN/$BOT_TOKEN/g" bot_manager.py
sed -i "s/ADMIN_IDS = \[.*\]/ADMIN_IDS = \[$(echo $ADMIN_IDS | sed 's/ /, /g')\]/g" bot_manager.py

# Buat service systemd
log_message "Membuat service systemd..."
cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME > /dev/null
[Unit]
Description=Telegram Bot Manager
After=network.target

[Service]
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/bot_manager.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd dan start service
log_message "Mengaktifkan dan menjalankan service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Tampilkan status service
log_message "Memeriksa status service..."
sudo systemctl status $SERVICE_NAME

log_message "Instalasi selesai! Bot Telegram berhasil diinstal dan dijalankan sebagai service."