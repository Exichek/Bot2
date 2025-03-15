import os
import qrcode
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

# Токен вашего бота (замените на свой)
BOT_TOKEN = "7320074229:AAG19mqnGv2wgIx1kn5x_dXAhl6ZQOThk-A"


# Функция для генерации QR-кода
def generate_wifi_qr(ssid: str, password: str, encryption: str = "WPA") -> str:
    # Формируем данные для QR-кода
    if encryption.upper() == "WEP":
        wifi_data = f"WIFI:T:WEP;S:{ssid};P:{password};;"
    elif encryption.upper() == "NOPASS":
        wifi_data = f"WIFI:T:nopass;S:{ssid};;"
    else:
        wifi_data = f"WIFI:T:WPA;S:{ssid};P:{password};;"

    # Генерируем QR-код
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(wifi_data)
    qr.make(fit=True)

    # Создаем изображение
    img = qr.make_image(fill_color="black", back_color="white")
    file_path = f"{ssid}_wifi_qr.png"
    img.save(file_path)

    return file_path


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот для генерации QR-кодов Wi-Fi.\n"
        "Чтобы узнать, как мной пользоваться, отправь команду /help."
    )


# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 **Как пользоваться ботом:**\n\n"
        "1. Отправь мне данные Wi-Fi в формате:\n"
        "`<SSID> <пароль> <тип шифрования>`\n\n"
        "🔹 **SSID** — имя вашей Wi-Fi сети.\n"
        "🔹 **Пароль** — пароль от сети. Если пароль содержит пробелы, заключи его в кавычки.\n"
        "🔹 **Тип шифрования** — WPA, WEP или NOPASS (для открытых сетей).\n\n"
        "📝 **Примеры использования:**\n"
        "- `MyWiFi MyPassword123 WPA`\n"
        "- `OpenNetwork NOPASS`\n"
        "- `OldWiFi 12345 WEP`\n"
        "- `MyWiFi \"My Password With Spaces\" WPA`\n\n"
        "2. Я отправлю тебе QR-код, который можно отсканировать для подключения к Wi-Fi.\n\n"
        "🔐 **Поддерживаемые типы шифрования:**\n"
        "- **WPA** (по умолчанию)\n"
        "- **WEP**\n"
        "- **NOPASS** (открытая сеть без пароля)"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Получаем текст сообщения
        text = update.message.text.strip()

        # Разделяем текст на части
        parts = text.split(maxsplit=2)

        # Проверяем количество аргументов
        if len(parts) < 2:
            await update.message.reply_text(
                "❌ **Ошибка:** Недостаточно данных.\n\n"
                "📝 Используй формат:\n"
                "`<SSID> <пароль> <тип шифрования>`\n\n"
                "Пример: `MyWiFi MyPassword123 WPA`"
            )
            return

        # Извлекаем SSID, пароль и тип шифрования
        ssid = parts[0]
        password = parts[1].strip('"')  # Убираем кавычки, если они есть
        encryption = parts[2] if len(parts) > 2 else "WPA"

        # Проверяем тип шифрования
        if encryption.upper() not in ["WPA", "WEP", "NOPASS"]:
            await update.message.reply_text(
                "❌ **Ошибка:** Неверный тип шифрования.\n\n"
                "🔐 Поддерживаемые типы:\n"
                "- WPA\n"
                "- WEP\n"
                "- NOPASS"
            )
            return

        # Генерируем QR-код
        qr_file = generate_wifi_qr(ssid, password, encryption)

        # Отправляем QR-код пользователю
        with open(qr_file, "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption=f"🔑 **QR-код для сети:** {ssid}\n"
                        f"🔒 **Тип шифрования:** {encryption.upper()}"
            )

        # Удаляем временный файл
        os.remove(qr_file)

    except Exception as e:
        await update.message.reply_text(
            f"❌ **Ошибка:** Произошла непредвиденная ошибка. Попробуй еще раз.\n\nОшибка: {e}")


# Основная функция
def main():
    # Создаем приложение бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()
