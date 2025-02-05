import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import sqlite3
import paramiko

# Konfigurasi logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Daftar User ID admin yang diizinkan
ADMIN_IDS = [123456789, 987654321]  # Ganti dengan User ID admin Anda

# Nama file database
DB_FILE = 'servers.db'

# Fungsi untuk memeriksa apakah pengguna adalah admin
def is_admin(user_id):
    return user_id in ADMIN_IDS

# Fungsi untuk membuat tabel server
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            name TEXT PRIMARY KEY,
            hostname TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Fungsi untuk menambahkan server ke database
def add_server_db(name, hostname, username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO servers (name, hostname, username, password)
        VALUES (?, ?, ?, ?)
    ''', (name, hostname, username, password))
    conn.commit()
    conn.close()

# Fungsi untuk menghapus server dari database
def delete_server_db(name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM servers WHERE name = ?', (name,))
    conn.commit()
    conn.close()

# Fungsi untuk mengambil semua server dari database
def get_all_servers():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT name, hostname, username, password FROM servers')
    servers = cursor.fetchall()
    conn.close()
    return servers

# Fungsi untuk menjalankan perintah di server via SSH
def run_ssh_command(server, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server['hostname'], username=server['username'], password=server['password'])
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        ssh.close()
        return output
    except Exception as e:
        return str(e)

# Command handler untuk /start
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text('Maaf, Anda tidak memiliki akses ke bot ini.')
        return
    update.message.reply_text('Bot manajemen server siap! Gunakan /help untuk melihat perintah yang tersedia.')

# Command handler untuk /help
def help_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text('Maaf, Anda tidak memiliki akses ke bot ini.')
        return
    commands = [
        '/start - Mulai bot',
        '/help - Tampilkan bantuan',
        '/list_servers - Daftar server yang tersedia',
        '/add_server <server_name> <hostname> <username> <password> - Tambahkan server baru',
        '/delete_server <server_name> - Hapus server',
        '/run <server_name> <command> - Jalankan perintah di server tertentu'
    ]
    update.message.reply_text('\n'.join(commands))

# Command handler untuk /list_servers
def list_servers(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text('Maaf, Anda tidak memiliki akses ke bot ini.')
        return
    servers = get_all_servers()
    if not servers:
        update.message.reply_text('Tidak ada server yang terdaftar.')
    else:
        server_list = '\n'.join([f"{name}: {hostname}" for name, hostname, _, _ in servers])
        update.message.reply_text(f'Server yang tersedia:\n{server_list}')

# Command handler untuk /add_server
def add_server(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text('Maaf, Anda tidak memiliki akses ke bot ini.')
        return
    try:
        args = context.args
        if len(args) != 4:
            update.message.reply_text('Usage: /add_server <server_name> <hostname> <username> <password>')
            return

        server_name, hostname, username, password = args
        add_server_db(server_name, hostname, username, password)
        update.message.reply_text(f'Server {server_name} berhasil ditambahkan.')
    except Exception as e:
        update.message.reply_text(f'Error: {str(e)}')

# Command handler untuk /delete_server
def delete_server(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text('Maaf, Anda tidak memiliki akses ke bot ini.')
        return
    try:
        args = context.args
        if len(args) != 1:
            update.message.reply_text('Usage: /delete_server <server_name>')
            return

        server_name = args[0]
        delete_server_db(server_name)
        update.message.reply_text(f'Server {server_name} berhasil dihapus.')
    except Exception as e:
        update.message.reply_text(f'Error: {str(e)}')

# Command handler untuk /run
def run_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        update.message.reply_text('Maaf, Anda tidak memiliki akses ke bot ini.')
        return
    try:
        args = context.args
        if len(args) < 2:
            update.message.reply_text('Usage: /run <server_name> <command>')
            return

        server_name = args[0]
        command = ' '.join(args[1:])

        servers = get_all_servers()
        server = next((s for s in servers if s[0] == server_name), None)

        if not server:
            update.message.reply_text(f'Server {server_name} tidak ditemukan.')
            return

        server_data = {
            'hostname': server[1],
            'username': server[2],
            'password': server[3]
        }
        output = run_ssh_command(server_data, command)
        update.message.reply_text(f'Output dari {server_name}:\n{output}')
    except Exception as e:
        update.message.reply_text(f'Error: {str(e)}')

# Fungsi utama
def main() -> None:
    # Ganti 'YOUR_TOKEN' dengan token bot Anda
    updater = Updater("YOUR_TOKEN")

    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("list_servers", list_servers))
    dispatcher.add_handler(CommandHandler("add_server", add_server))
    dispatcher.add_handler(CommandHandler("delete_server", delete_server))
    dispatcher.add_handler(CommandHandler("run", run_command))

    # Mulai bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    init_db()
    main()