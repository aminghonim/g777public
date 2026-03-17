"""
WhatsApp Sender Engine - Antigravity Suite (Hybrid Mode)
Uses Cloud API for reliable sending instead of fragile browser automation.
"""

import time
import random
from datetime import datetime
from pathlib import Path
from .cloud_service import AzureCloudService
from backend.core.i18n import t
from backend.database_manager import db_manager


class WhatsAppSender:
    """محرك إرسال رسائل WhatsApp (يعتمد على السحابة)"""

    def __init__(
        self, config_path=None, instance_name: str = None, user_id: str = None
    ):
        self.cloud = AzureCloudService()
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
            except:
                pass

    def set_callback(self, callback_func):
        self.callback = callback_func

    def _replace_variables(self, message, member_data):
        if isinstance(member_data, dict):
            name = member_data.get("name", t("sender.default_name", "العميل"))
        else:
            name = t("sender.default_name", "العميل")

        message = message.replace("{name}", name)
        message = message.replace("{Name}", name)
        message = message.replace("{NAME}", name)
        return message

    def run_campaign(
        self, excel_path, sheet_name, message_templates, media_folder=None
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
            from .excel_processor import ExcelProcessor

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
                quota = db_manager.get_user_quota_info(self.user_id)
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

                # اختيار رسالة
                message_idx = (idx - 1) % len(message_templates)
                message = self._replace_variables(
                    message_templates[message_idx], member
                )

                # API Call to Cloud
                try:
                    # (يمكننا استخدام cloud.start_campaign_cloud لقائمة كاملة، لكن هنا نريد التحكم المحلي في الوقت)
                    response = self.cloud.start_campaign_cloud(
                        [phone], message, instance_name=self.instance_name
                    )

                    if response.get("success"):
                        self.log(t("sender.logs.sent_ok", "تم الإرسال بنجاح"), "OK")
                        success_count += 1
                        # SAAS-013: Atomic Accounting
                        db_manager.increment_daily_usage(self.user_id, "message_count")
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

                except Exception as ex:
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

        except Exception as e:
            self.log(
                t("sender.logs.unexpected_error", "خطأ غير متوقع: {err}").format(err=e),
                "FATAL",
            )
        finally:
            self.is_running = False
            self.log(t("sender.logs.done", "انتهت العملية."), "END")

    def stop_campaign(self):
        self.is_running = False
