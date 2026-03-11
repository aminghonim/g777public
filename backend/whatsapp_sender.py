"""
WhatsApp Sender Engine - Antigravity Suite (Hybrid Mode)
Uses Cloud API for reliable sending instead of fragile browser automation.
"""

import time
import random
from datetime import datetime
from backend.core.i18n import t
from backend.database_manager import db_manager
from .cloud_service import AzureCloudService


class WhatsAppSender:
    """محرك إرسال رسائل WhatsApp (يعتمد على السحابة)"""

    def __init__(
        self, _config_path=None, instance_name: str = None, user_id: str = None  # pylint: disable=unused-argument
    ):
        self.cloud = AzureCloudService()
        self.db_manager = db_manager  # Use module level as default for SaaS consistency
        self.instance_name = instance_name  # SaaS Instance
        self.user_id = (
            user_id or "00000000-0000-0000-0000-000000000000"
        )  # SaaS Identity / Guest Fallback
        self.is_running = False
        self.callback = None
        # Default config needed for delays
        self.config = {"delays": {"min_seconds": 3, "max_seconds": 8}}

    def log(self, message, level="INFO"):
        """إرسال رسالة للـ Console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        print(formatted, flush=True)
        # إرسال للواجهة إذا متصلة
        if self.callback:
            try:
                self.callback(formatted)
            except Exception:  # pylint: disable=broad-exception-caught
                pass

    def set_callback(self, callback_func):
        """Set a callback function for logging."""
        self.callback = callback_func

    # _shorten_url تمت إزالته واستبداله بـ smart_shorten من utils

    async def _process_message(self, message: str, member_data: dict) -> str:
        if isinstance(member_data, dict):
            name = member_data.get("name", t("sender.default_name", "العميل"))
        else:
            name = t("sender.default_name", "العميل")

        message = message.replace("{name}", name)
        message = message.replace("{Name}", name)
        message = message.replace("{NAME}", name)

        # البحث عن روابط وتقصيرها باستخدام Utils
        import re  # pylint: disable=import-outside-toplevel
        from backend.core.utils.api_helpers import smart_shorten  # pylint: disable=import-outside-toplevel
        urls = re.findall(r'(https?://[^\s]+)', message)
        for url in urls:
            # نتجاهل الروابط القصيرة أصلاً أو روابط الواتساب
            if "wa.me" not in url and len(url) > 30:
                short_url = await smart_shorten(url, logger=self.log)
                message = message.replace(url, short_url)

        return message

    def run_campaign(
        self, excel_path, sheet_name, message_templates, _media_folder=None  # pylint: disable=unused-argument
    ):
        """تشغيل حملة إرسال (API Mode)"""
        self.is_running = True
        self.log(t("sender.logs.separator", "=" * 50))
        self.log(
            t("sender.logs.campaign_start", "بدء حملة الإرسال (وضع الـ API السريع)"),
            "START",
        )
        self.log(t("sender.logs.separator", "=" * 50))

        try:
            # قراءة البيانات
            from .excel_processor import ExcelProcessor  # pylint: disable=import-outside-toplevel

            processor = ExcelProcessor()
            members = processor.read_contacts(excel_path, sheet_name)

            if not members:
                self.log(t("sender.logs.no_contacts", "لا توجد جهات اتصال!"), "ERROR")
                return

            self.log(
                t("sender.logs.loaded_contacts", "تم تحميل {count} جهة اتصال").format(
                    count=len(members)
                ),
                "INFO",
            )

            success_count = 0
            fail_count = 0

            # --- Auto-Warmup Step ---
            self.log(
                t(
                    "sender.logs.warmup_start",
                    " جاري إيقاظ السيرفر السحابي (Warm-up)...",
                ),
                "WAIT",
            )
            is_awake, status_msg = self.cloud.warmup()

            if is_awake:
                self.log(
                    t("sender.logs.server_ready", " السيرفر جاهز: {status}").format(
                        status=status_msg
                    ),
                    "OK",
                )
                # لو السيرفر صاحي بس الواتساب مفصول، ندي تحذير بس نكمل
                if "Disconnected" in status_msg:
                    self.log(
                        t(
                            "sender.logs.warn_whatsapp_disconnected",
                            " تنبيه: الواتساب قد يكون غير متصل! تأكد من صفحة الربط.",
                        ),
                        "WARN",
                    )
            else:
                self.log(
                    t(
                        "sender.logs.warmup_failed",
                        " فشل إيقاظ السيرفر. قد تفشل الرسائل الأولى.",
                    ),
                    "WARN",
                )
            # ------------------------

            # --- Anti-Ban: Batch AI Rephrasing (Spintax Alternative) ---
            # لتوفير التوكنز والوقت، نقوم بتوليد المصفوفة مرة واحدة في البداية بدلاً من كل رسالة
            if len(members) > 10:
                self.log(
                    t(
                        "sender.logs.ai_spintax_start",
                        "جاري توليد صيغ تسويقية متعددة باستخدام الذكاء الاصطناعي (Batch Spintax)..."
                    ),
                    "INFO"
                )
                try:
                    from backend.ai_client import AzureAIClient  # pylint: disable=import-outside-toplevel
                    ai = AzureAIClient()

                    base_msgs = "\n---\n".join(message_templates)
                    prompt = (
                        "قم بإعادة صياغة الرسائل التسويقية التالية لتوليد 5 نسخ مختلفة لكل رسالة "
                        "لتجنب حظر واتساب سبام.\n"
                        f"يجب الحفاظ على نفس المعنى والنبرة والمتغيرات مثل {{name}} والروابط.\n"
                        "قم بإرجاع النتائج فقط كرسائل مفصولة بـ '|||'. لا تضف أي نصوص تقديمية.\n\n"
                        f"الرسائل الأصلية:\n{base_msgs}"
                    )

                    import asyncio  # pylint: disable=import-outside-toplevel
                    start_time = time.time()
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            rewritten_batch = asyncio.run_coroutine_threadsafe(
                                ai.generate_response(
                                    prompt, "أنت خبير تسويق إلكتروني وصناعة محتوى عربي."
                                ),
                                loop
                            ).result()
                        else:
                            rewritten_batch = loop.run_until_complete(
                                ai.generate_response(
                                    prompt, "أنت خبير تسويق إلكتروني وصناعة محتوى عربي."
                                )
                            )
                    except RuntimeError:
                        rewritten_batch = asyncio.run(
                            ai.generate_response(
                                prompt, "أنت خبير تسويق إلكتروني وصناعة محتوى عربي."
                            )
                        )

                    latency = time.time() - start_time
                    if rewritten_batch:
                        est_tokens = (len(prompt) + len(rewritten_batch)) // 4
                        self.log(
                            f"Spintax Generation - Latency: {latency:.2f}s | "
                            f"Est. Tokens: ~{est_tokens}",
                            "INFO"
                        )

                        # LLMOps Observability: Persistent Metrics Logging
                        import os  # pylint: disable=import-outside-toplevel
                        os.makedirs("logs", exist_ok=True)
                        with open("logs/llm_performance.log", "a", encoding="utf-8") as f:
                            log_msg = (
                                f"[{datetime.now().isoformat()}] ACTION: Batch Spintax | "
                                f"Latency: {latency:.2f}s | Est. Tokens: ~{est_tokens} "
                                "(Input/Output)\n"
                            )
                            f.write(log_msg)

                        from backend.core.utils.api_helpers import load_api_config  # pylint: disable=import-outside-toplevel

                        config = load_api_config()
                        enforce_vars = config.get("app_logic", {}).get("spintax", {}).get(
                            "enforce_variables", ["{name}", "{company}"]
                        )

                        # Find which required variables exist in the original templates
                        required_vars_in_base = [
                            v for v in enforce_vars if any(v in m for m in message_templates)
                        ]

                        new_templates = []
                        for msg in rewritten_batch.split("|||"):
                            msg = msg.strip()
                            if len(msg) > 10:
                                # RAGAS Check: Ensure all required variables from base are
                                # preserved in the variation
                                is_valid = True
                                for req_var in required_vars_in_base:
                                    if req_var not in msg:
                                        self.log(
                                            f"Spintax Validation Failed: Missing {req_var} "
                                            "in variation. Discarding.",
                                            "WARN"
                                        )
                                        is_valid = False
                                        break

                                # Extra regex check to catch if it misspelled {name} like [name]
                                # or {الاسم}. If any {.*?\} doesn't match our allowed vars, we
                                # might want to flag it, but the main issue is missing the
                                # EN exact brackets.
                                if is_valid:
                                    new_templates.append(msg)

                        if new_templates:
                            message_templates = new_templates
                            self.log(
                                f"تم توليد واعتماد {len(message_templates)} "
                                "صيغة لتبديلها عشوائياً.",
                                "OK"
                            )
                except Exception as e:  # pylint: disable=broad-exception-caught
                    self.log(
                        t(
                            "sender.logs.ai_rephrase_error",
                            f"خطأ في توليد स्पिनطكس: {e}. سيتم استخدام الرسائل الأصلية."
                        ),
                        "WARN"
                    )
            # -----------------------------------------------------

            # Send Loop
            for idx, member in enumerate(members, 1):
                if not self.is_running:
                    self.log(
                        t("sender.logs.stopped_by_user", "تم إيقاف الحملة من المستخدم"),
                        "STOP",
                    )
                    break

                phone = member.get("phone", "")
                name = member.get("name", "العميل")

                if not phone:
                    continue

                # --- SAAS-013: Messaging Quota Check ---
                quota = self.db_manager.get_user_quota_info(self.user_id)
                if quota["message_count"] >= quota["daily_limit"]:
                    self.log(
                        t(
                            "sender.logs.quota_exceeded",
                            "فشل: تم تجاوز الحد اليومي للرسائل ({limit})",
                        ).format(limit=quota["daily_limit"]),
                        "ERROR",
                    )
                    self.log(
                        t("sender.logs.upgrade_notice", "يرجى ترقية الباقة للاستمرار."),
                        "WARN",
                    )
                    self.is_running = False
                    break
                # ---------------------------------------

                self.log(
                    t(
                        "sender.logs.sending_to",
                        "[{idx}/{total}] إرسال إلى: {phone} ({name})",
                    ).format(idx=idx, total=len(members), phone=phone, name=name)
                )

                # اختيار رسالة وتقصير الروابط
                message_idx = (idx - 1) % len(message_templates)
                import asyncio  # pylint: disable=import-outside-toplevel
                # Run the async process_message in the current event loop if we are in one,
                # but since run_campaign is synchronous currently, let's use asyncio.run
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context but calling a sync function? Not ideal.
                        # Actually, background_tasks in fastapi runs sync functions in a threadpool.
                        message_str = message_templates[message_idx]
                        message = asyncio.run_coroutine_threadsafe(
                            self._process_message(message_str, member), loop
                        ).result()
                    else:
                        message_str = message_templates[message_idx]
                        message = loop.run_until_complete(
                            self._process_message(message_str, member)
                        )
                except RuntimeError:
                    message_str = message_templates[message_idx]
                    message = asyncio.run(self._process_message(message_str, member))

                # API Call to Cloud
                try:
                    # (يمكننا استخدام cloud.start_campaign_cloud لقائمة كاملة،
                    # لكن هنا نريد التحكم المحلي في الوقت)
                    response = self.cloud.start_campaign_cloud(
                        [phone], message, instance_name=self.instance_name
                    )

                    if response.get("success"):
                        self.log(t("sender.logs.sent_ok", "تم الإرسال بنجاح"), "OK")
                        success_count += 1
                        # SAAS-013: Atomic Accounting
                        self.db_manager.increment_daily_usage(self.user_id, "message_count")
                    else:
                        details = response.get("details", [])
                        error_msg = response.get("error")
                        if not error_msg and details:
                            error_msg = (
                                details[0].get("error") if details else "Unknown Error"
                            )

                        self.log(
                            t("sender.logs.send_failed", "فشل الإرسال: {error}").format(
                                error=error_msg
                            ),
                            "ERROR",
                        )
                        fail_count += 1

                except Exception as ex:  # pylint: disable=broad-exception-caught
                    self.log(
                        t(
                            "sender.logs.connection_error", "خطأ في الاتصال: {err}"
                        ).format(err=ex),
                        "ERROR",
                    )
                    fail_count += 1

                # تأخير عشوائي
                if idx < len(members) and self.is_running:
                    delay = random.randint(
                        self.config["delays"]["min_seconds"],
                        self.config["delays"]["max_seconds"],
                    )
                    self.log(
                        t(
                            "sender.logs.waiting_seconds", "انتظار {sec} ثانية..."
                        ).format(sec=delay),
                        "WAIT",
                    )
                    time.sleep(delay)

            self.log(t("sender.logs.separator", "=" * 50))
            self.log(
                t(
                    "sender.logs.campaign_complete",
                    "اكتملت الحملة! نجح: {succ} | فشل: {fail}",
                ).format(succ=success_count, fail=fail_count),
                "COMPLETE",
            )
            self.log(t("sender.logs.separator", "=" * 50))

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.log(
                t("sender.logs.unexpected_error", "خطأ غير متوقع: {err}").format(err=e),
                "FATAL",
            )
        finally:
            self.is_running = False
            self.log(t("sender.logs.done", "انتهت العملية."), "END")

    def stop_campaign(self):
        """Stop sending messages."""
        self.is_running = False
