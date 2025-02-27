from telegram import Message, Update


class ProcessingMessagePlaceHolder:
    def __init__(self, update: Update, placeholder_text: str = "⌛ обрабатываем ⌛"):
        self.update = update
        self.placeholder_text = placeholder_text
        self._placeholder_message: Message | None = None

    async def __aenter__(self):
        self._placeholder_message = await self.update.message.reply_text(self.placeholder_text)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.update.get_bot().delete_message(
            chat_id=self.update.message.chat_id,
            message_id=self._placeholder_message.message_id,
        )
