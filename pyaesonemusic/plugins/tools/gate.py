# 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 𝐆𝐚𝐭𝐞𝐰𝐚𝐲𝐬 𝐇𝐮𝐧𝐭𝐞𝐫
from pyrogram import Client, filters
import requests
from pyaesonemusic import app

sessi = requests.session()

@app.on_message(filters.command("url", prefixes=[".", "/"]))
async def check_payment_gateways(client, message):
    
    def find_captcha(response_text):
        if 'recaptcha' in response_text.lower():
            return 'Using Google reCAPTCHA ✅'
        elif 'hcaptcha' in response_text.lower():
            return 'Using hCaptcha ✅'
        else:
            return 'Not using Any Captcha 🚫'

    def detect_cloudflare(response):
        cloudflare_headers = ["cf-ray", "cf-cache-status", "server"]
        return any(header in response.headers for header in cloudflare_headers)

    def find_payment_gateways(response_text):
        detected_gateways = []
        lower_text = response_text.lower()
        gateways = {
            "paypal": "PayPal",
            "stripe": "Stripe",   
            "braintree": "Braintree",
            "square": "Square",
            "authorize.net": "Authorize.Net",
            "2checkout": "2Checkout",
            "adyen": "Adyen",
            "worldpay": "Worldpay",
            "sagepay": "SagePay",
            "checkout.com": "Checkout.com",
            "skrill": "Skrill",
            "neteller": "Neteller",
            "payoneer": "Payoneer",
            "klarna": "Klarna",
            "afterpay": "Afterpay",
            "sezzle": "Sezzle",
            "alipay": "Alipay",
            "wechat pay": "WeChat Pay",
            "tenpay": "Tenpay",
            "qpay": "QPay",
            "sofort": "SOFORT Banking",
            "giropay": "Giropay",
            "ideal": "iDEAL",
            "trustly": "Trustly",
            "zelle": "Zelle",
            "venmo": "Venmo",
            "epayments": "ePayments",
            "revolut": "Revolut",
            "wise": "Wise",
            "shopify payments": "Shopify Payments",
            "woocommerce": "WooCommerce",
            "paytm": "Paytm",
            "phonepe": "PhonePe",
            "google pay": "Google Pay",
            "bhim upi": "BHIM UPI",
            "razorpay": "Razorpay",
            "instamojo": "Instamojo",
            "ccavenue": "CCAvenue",
            "payu": "PayU",
            "mobikwik": "MobiKwik",
            "freecharge": "FreeCharge",
            "ebs": "EBS",
            "cashfree": "Cashfree",
            "jio money": "JioMoney",
            "yandex.money": "Yandex.Money",
            "qiwi": "QIWI",
            "webmoney": "WebMoney",
            "paysafe": "Paysafe",
            "bpay": "BPAY",
            "mollie": "Mollie",
            "paysera": "Paysera",
            "multibanco": "Multibanco",
            "pagseguro": "PagSeguro",
            "mercadopago": "MercadoPago",
            "payfast": "PayFast",
            "billdesk": "BillDesk",
            "paystack": "Paystack",
            "interswitch": "Interswitch",
            "voguepay": "VoguePay",
            "flutterwave": "Flutterwave",
        }

        for key, value in gateways.items():
            if key in lower_text:
                detected_gateways.append(value)

        return detected_gateways if detected_gateways else ["Unknown"]

    def detect_graphql(response_text):
        return "True ✅" if "graphql" in response_text.lower() else "False 🔥"

    def detect_platform(response_text):
        platforms = {
            "shopify": "Shopify", "woocommerce": "WooCommerce", "magento": "Magento",
            "bigcommerce": "BigCommerce", "opencart": "OpenCart", "prestashop": "PrestaShop"
        }
        for key, value in platforms.items():
            if key in response_text.lower():
                return value
        return "None"

    def detect_errors(response_text):
        error_keywords = ["error", "exception", "failed", "not found", "unavailable"]
        errors = [word for word in error_keywords if word in response_text.lower()]
        return ", ".join(errors) if errors else "None"

    def detect_payment_type(response_text):
        if "3d secure" in response_text.lower() or "3ds" in response_text.lower():
            return "3D Secure Payment ✅"
        return "2D Payment 🔥"

    async def check_payment_gateways_internal(url):
        try:
            response = sessi.get(url)
            response.raise_for_status()

            detected_gateways = find_payment_gateways(response.text)
            detected_captcha = find_captcha(response.text)
            is_cloudflare_protected = detect_cloudflare(response)
            graphql_status = detect_graphql(response.text)
            platform_type = detect_platform(response.text)
            error_logs = detect_errors(response.text)
            payment_type = detect_payment_type(response.text)

            result_message = (
                f"𝗚𝗔𝗧𝗘𝗪𝗔𝗬 𝗛𝗨𝗡𝗧..🔍\n"
                f"**>>━━━━━━━━━━━━━━<<**\n\n"
                f"☞ 𝙍𝙚𝙨𝙪𝙡𝙩𝙨 𝙛𝙤𝙧 -» {url}  \n"
                f"☞ 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗚𝗮𝘁𝗲𝘄𝗮𝘆𝘀 -» {', '.join(detected_gateways)}\n"
                f"☞ 𝗖𝗮𝗽𝘁𝗰𝗵𝗮 -» {detected_captcha}\n"
                f"☞ 𝘾𝙡𝙤𝙪𝙙𝙛𝙡𝗮𝗿𝗲 𝙋𝙧𝗼𝙩𝙚𝙘𝙩𝗶𝗼𝗻 -» {'Yes ✅' if is_cloudflare_protected else 'No 🔥'}\n"
                f"☞ **𝗚𝗿𝗮𝗽𝗵𝗾𝗹** -» {graphql_status}\n"
                f"☞ **𝗣𝗹𝗮𝘁𝗳𝗼𝗿𝗺** -» {platform_type}\n"
                f"☞ **𝗘𝗿𝗿𝗼𝗿 𝗹𝗼𝗴𝘀** -» {error_logs}\n"
                f"☞ **𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗧𝘆𝗽𝗲** -» {payment_type}\n"
                f"**>>━━━━━━━━━━━━━━<<**\n"
            )
            await message.reply_text(result_message, disable_web_page_preview=True)

        except requests.exceptions.RequestException:
            await message.reply_text("𝐄𝐫𝐫𝐨𝐫: 𝐈𝐧 𝐅𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐃𝐞𝐭𝐚𝐢𝐥𝐬. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐜𝐡𝐞𝐜𝐤 𝐋𝐢𝐧𝐤 𝐢𝐟 𝐭𝐡𝐞 𝐥𝐢𝐧𝐤 𝐢𝐬 𝐫𝐞𝐚𝐜𝐡𝐚𝐛𝐥𝐞 𝐨𝐫 𝐧𝐨𝐭")

    # Process the URL correctly
    try:
        website_url = message.text.split(maxsplit=1)[1].strip()
        if not website_url.startswith(("http://", "https://")):
            website_url = "http://" + website_url

        await check_payment_gateways_internal(website_url)

    except IndexError:
        await message.reply_text("<b>Please provide a valid URL. Usage: `/url <url>`</b>")
    except Exception as e:
        print(f"Unhandled error: {e}")
