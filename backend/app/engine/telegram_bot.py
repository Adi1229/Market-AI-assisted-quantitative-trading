import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import httpx

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, bot_token: str, backend_url: str = "http://localhost:8000"):
        self.bot_token = bot_token
        self.backend_url = backend_url
        self.application = Application.builder().token(bot_token).build()
        self._setup_handlers()
        self.is_running = False

    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("positions", self.positions_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Market 2.0 Trading Bot Started.\nUse /help to see commands.")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
Commands:
/status - System health and mode
/positions - Current open positions
/portfolio - Full portfolio overview
/help - Available commands
        """
        await update.message.reply_text(help_text)

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/api/v1/health")
                if response.status_code == 200:
                    data = response.json()
                    msg = f"System Status: {data.get('status', 'Unknown')}\nProvider: {data.get('provider', 'Unknown')}\nTime: {data.get('time', '')}"
                else:
                    msg = "System Status: DOWN (Backend Error)"
        except Exception as e:
            msg = f"System Status: DOWN ({str(e)})"
        await update.message.reply_text(msg)

    async def positions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/api/v1/portfolio/positions")
                if response.status_code == 200:
                    positions = response.json()
                    if not positions:
                        msg = "No open positions."
                    else:
                        msg = "Open Positions:\n"
                        for p in positions:
                            msg += f"- {p['instrument_id']} ({p['direction']}): {p['quantity']} @ {p['entry_price']}\n"
                else:
                    msg = "Failed to fetch positions."
        except Exception as e:
            msg = f"Error fetching positions: {e}"
        await update.message.reply_text(msg)

    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/api/v1/portfolio/summary")
                if response.status_code == 200:
                    summary = response.json()
                    msg = "Portfolio Summary:\n"
                    msg += f"Total Value: {summary.get('total_value', 0)}\n"
                    msg += f"Cash: {summary.get('cash', 0)}\n"
                    msg += f"Unrealized P&L: {summary.get('unrealized_pnl', 0)}\n"
                    msg += f"Realized P&L: {summary.get('realized_pnl', 0)}"
                else:
                    msg = "Failed to fetch portfolio."
        except Exception as e:
            msg = f"Error fetching portfolio: {e}"
        await update.message.reply_text(msg)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        data = query.data
        if not data or ":" not in data:
            await query.edit_message_text(text="Invalid callback format.")
            return

        action, opp_id = data.split(":", 1)
        
        url = ""
        if action == "TAKE_TRADE":
            url = f"{self.backend_url}/api/v1/opportunities/{opp_id}/approve"
        elif action == "IGNORE":
            url = f"{self.backend_url}/api/v1/opportunities/{opp_id}/ignore"
        else:
            await query.edit_message_text(text=f"Unknown action: {action}")
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url)
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status", "Unknown")
                    await query.edit_message_text(text=f"{query.message.text}\n\n[ Action Recorded: {status} ]")
                else:
                    error_msg = response.json().get("detail", "Error processing action")
                    await query.edit_message_text(text=f"{query.message.text}\n\n[ Action Failed: {error_msg} ]")
        except Exception as e:
            await query.edit_message_text(text=f"{query.message.text}\n\n[ Action Failed: Backend Unreachable ]")

    async def start(self):
        if not self.is_running:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            self.is_running = True
            logger.info("Telegram Bot started.")

    async def stop(self):
        if self.is_running:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            self.is_running = False
            logger.info("Telegram Bot stopped.")
