
from attached_assets.baii import bot, OWNER_ID, AUTHORIZED_USERS
import asyncio

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║         Stripe Auth Checker Bot        ║
║            Started Successfully        ║
╚════════════════════════════════════════╝
""")
    
    try:
        print("✅ Bot is running...")
        print("👉 Press Ctrl+C to stop the bot")
        asyncio.run(bot.polling(non_stop=True, timeout=60))
    except KeyboardInterrupt:
        print("\n⚠️ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
    finally:
        print("\n🔄 Bot session ended")
