"""
Data Grabber Module - Enhanced Version
Handles WhatsApp group data extraction with improved Virtual Scrolling support.
Uses multiple extraction strategies for maximum reliability.
"""

import time
import re
import os
import random
import logging
from datetime import datetime
import pandas as pd
from typing import List, Dict, Tuple, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from backend.browser_core import WhatsAppBrowser
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from browser_core import WhatsAppBrowser

logger = logging.getLogger(__name__)


class DataGrabber(WhatsAppBrowser):
    """
    Handles extraction of members from WhatsApp groups.
    Enhanced with multiple extraction strategies.
    """
    
    def __init__(self, headless: bool = False):
        """Initialize the DataGrabber."""
        super().__init__(headless=headless)

    def scrape_interactive_mode(self) -> tuple:
        """
        المنطق المحسّن الرئيسي للاستخراج.
        يستخدم استراتيجية مزدوجة:
        1. استخراج مباشر من العناصر (Direct Element Access)
        2. معالجة Virtual Scrolling بذكاء
        """
        logger.info("[Grabber] Starting Enhanced Interactive Scraping...")
        
        if not self.driver:
            self.initialize_driver()
            if not self.load_whatsapp():
                return None, "WhatsApp load failed"

        try:
            # 1. الاستحواذ على اسم المجموعة أولاً
            group_name = self._get_group_name()
            logger.info(f"[Grabber] Target Group: {group_name}")

            # 2. التحقق من وجود الـ Dialog
            try:
                # Dialog selector
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
                )
                logger.info("[Grabber]  Dialog detected!")
            except TimeoutException:
                return None, " Dialog not found! Please open 'Group Info' -> 'View all' first."

            # 3. استخدام الاستراتيجية المحسّنة
            result = self._enhanced_extraction_strategy(group_name)
            
            if result[0]:  # إذا نجحت الاستراتيجية الأولى
                return result
            
            # 4. Fallback: محاولة الطريقة البديلة
            logger.info("[Grabber] Primary strategy returned 0 results. Trying fallback...")
            return self._fallback_selenium_extraction(group_name)

        except Exception as e:
            import traceback
            error = traceback.format_exc()
            logger.error(f"[Grabber] Critical Error:\n{error}")
            return None, str(e)

    def _enhanced_extraction_strategy(self, group_name: str) -> Tuple[Optional[str], str]:
        """
        الاستراتيجية المحسّنة: استخراج مباشر من العناصر.
        
        المنطق:
        - استهداف div[role='listitem'] مباشرة
        - استخراج البيانات من كل عنصر فور ظهوره
        - استخدام Dict للتتبع ومنع التكرار
        - التوقف عند عدم ظهور بيانات جديدة
        """
        logger.info("[Strategy 1] Direct Element Extraction...")
        
        # JavaScript للاستخراج المباشر
        extract_script = """
        var dialog = document.querySelector('div[role="dialog"]');
        if (!dialog) return [];
        
        var members = [];
        
        // محاولة Selectors متعددة
        var selectors = [
            'div[role="listitem"]',
            'div[data-testid*="cell"]',
            'div[class*="_1WliW"]',  // Selector قديم
            'div[class*="x1n2onr6"]'  // Selector جديد
        ];
        
        var items = [];
        for (var i = 0; i < selectors.length; i++) {
            var found = dialog.querySelectorAll(selectors[i]);
            if (found.length > items.length) {
                items = found;
            }
        }
        
        // console.log('[WhatsApp Scraper] Found without items.length log');
        
        items.forEach(function(item, index) {
            try {
                // استخراج النص بطرق متعددة
                var fullText = item.innerText || item.textContent || '';
                
                if (!fullText || fullText.length < 5) {
                    // محاولة البحث في الـ children
                    var spans = item.querySelectorAll('span');
                    fullText = Array.from(spans).map(s => s.innerText || s.textContent).join(' ');
                }
                
                // البحث عن رقم الهاتف using regex
                var phoneRegex = /\\+\\d[\\d\\s\\-()]{8,}/g;
                var phoneMatches = fullText.match(phoneRegex);
                
                if (phoneMatches) {
                    phoneMatches.forEach(function(rawPhone) {
                        var cleanPhone = rawPhone.replace(/\\D/g, '');
                        
                        if (cleanPhone.length >= 10) {
                            // استخراج الاسم
                            var nameText = fullText.replace(rawPhone, '').trim();
                            
                            // تنظيف الاسم من الأسطر الزائدة
                            var lines = nameText.split('\\n').filter(l => l.trim());
                            nameText = lines[0] || 'Unknown';
                            
                            // تنظيف إضافي
                            nameText = nameText.replace(/[~@#]/g, '').trim();
                            
                            members.push({
                                name: nameText,
                                phone: cleanPhone,
                                index: index
                            });
                        }
                    });
                }
            } catch(e) {
                // console.error('[WhatsApp Scraper] Error processing item:', e);
            }
        });
        
        return members;
        """

        collected_members: Dict[str, dict] = {}
        max_iterations = 150  # Increased for larger groups
        no_new_data_count = 0
        max_no_new = 8  # Increased tolerance for network lag
        
        for iteration in range(max_iterations):
            # A. استخراج العناصر الحالية
            try:
                current_batch = self.driver.execute_script(extract_script)
            except Exception as e:
                logger.error(f"[Strategy 1] JS execution error: {e}")
                current_batch = []
            
            # B. معالجة البيانات
            new_members_count = 0
            if current_batch:
                for member in current_batch:
                    phone = member['phone']
                    if phone not in collected_members:
                        collected_members[phone] = member
                        new_members_count += 1
            
            # C. طباعة التقدم
            total = len(collected_members)
            logger.info(f"[Scroll {iteration + 1:02d}/{max_iterations}] "
                  f"Total: {total:4d} | New: {new_members_count:3d}")
            
            # D. التحقق من توقف البيانات
            if new_members_count == 0:
                no_new_data_count += 1
                if no_new_data_count >= max_no_new:
                    logger.info(f"[Strategy 1]  No new data for {max_no_new} iterations. Stopping.")
                    break
            else:
                no_new_data_count = 0
            
            # E. التمرير
            scroll_result = self._smart_scroll()
            if not scroll_result:
                logger.warning("[Strategy 1]  Scroll failed")
            
            # F. انتظار التحميل
            time.sleep(0.4)
        
        # G. النتائج
        if not collected_members:
            logger.info("[Strategy 1]  No members found")
            return None, "No members found with primary strategy"
        
        # H. الحفظ
        return self._save_members(collected_members, "enhanced", group_name)

    def _smart_scroll(self, element=None) -> bool:
        """
        تمرير ذكي مع محاولات متعددة.
        accepts optional element for testing compatibility
        """
        scroll_script = """
        var dialog = document.querySelector('div[role="dialog"]');
        if (!dialog) return false;
        
        // استراتيجيات متعددة للعثور على الـ scrollable container
        var scrollable = null;
        
        // 1. البحث بـ style attribute
        scrollable = dialog.querySelector('div[style*="overflow"]');
        
        // 2. البحث بـ computed style
        if (!scrollable) {
            var divs = dialog.querySelectorAll('div');
            for (var i = 0; i < divs.length; i++) {
                var style = window.getComputedStyle(divs[i]);
                if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
                    var height = divs[i].scrollHeight;
                    if (height > 500) {  // التأكد من أنه الـ container الصحيح
                        scrollable = divs[i];
                        break;
                    }
                }
            }
        }
        
        // 3. Fallback: الـ dialog نفسه
        if (!scrollable) {
            scrollable = dialog;
        }
        
        if (scrollable) {
            var before = scrollable.scrollTop;
            
            // التمرير بمقدار أصغر لضمان عدم تخطي عناصر
            scrollable.scrollTop = scrollable.scrollTop + 250;
            
            var after = scrollable.scrollTop;
            
            return {
                success: true,
                scrolled: after > before,
                position: after,
                height: scrollable.scrollHeight
            };
        }
        
        return false;
        """
        
        try:
            result = self.driver.execute_script(scroll_script)
            return bool(result)
        except:
            return False

    def _fallback_selenium_extraction(self, group_name: str) -> Tuple[Optional[str], str]:
        """
        الطريقة البديلة: استخدام Selenium المباشر بدون JavaScript.
        """
        logger.info("[Fallback] Using Selenium direct access...")
        
        try:
            # محاولة Selectors متعددة
            selectors = [
                "div[role='dialog'] div[role='listitem']",
                "div[role='dialog'] div[data-testid*='cell']",
                "div[role='dialog'] div[class*='_1WliW']",
                "div[role='dialog'] div[class*='x1n2onr6']"
            ]
            
            items = []
            for selector in selectors:
                found = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(found) > len(items):
                    items = found
                    logger.info(f"[Fallback] Found {len(items)} items with selector: {selector}")
            
            if not items:
                logger.info("[Fallback]  No items found with any selector")
                return None, "No elements found in dialog"
            
            members: Dict[str, dict] = {}
            
            for idx, item in enumerate(items):
                try:
                    text = item.text
                    if not text:
                        continue
                    
                    phone_match = re.search(r'\+\d[\d\s\-()]{8,}', text)
                    if phone_match:
                        raw_phone = phone_match.group(0)
                        clean_phone = re.sub(r'\D', '', raw_phone)
                        
                        if len(clean_phone) >= 10 and clean_phone not in members:
                            name = text.replace(phone_match.group(0), '').strip()
                            name = name.split('\n')[0].strip()
                            name = re.sub(r'[~@#]', '', name).strip()
                            
                            members[clean_phone] = {
                                'name': name or 'Unknown',
                                'phone': clean_phone,
                                'index': idx
                            }
                except Exception as e:
                    continue
            
            if not members:
                return None, "No valid phone numbers found"
            
            return self._save_members(members, "fallback", group_name)
            
        except Exception as e:
            import traceback
            logger.error(f"[Fallback] Error:\n{traceback.format_exc()}")
            return None, f"Fallback error: {str(e)}"

    def _get_group_name(self) -> str:
        """
        Extracts group name specifically from the ACTIVE chat in the sidebar list.
        Targeting div[aria-selected='true'] is the most reliable method.
        """
        try:
            logger.info("[Grabber] Attempting to get name from active sidebar item...")
            
            # Selector strategies, ordered by reliability
            selectors = [
                # 1. Standard active item title
                "div[id='pane-side'] div[aria-selected='true'] span[title]",
                # 2. Relaxed active item title
                "div[aria-selected='true'] span[title]",
                # 3. Active item text (fallback if title attribute is missing)
                "div[id='pane-side'] div[aria-selected='true'] div[role='gridcell']"
            ]

            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elements:
                        # If we found a gridcell, try to find the title inside it
                        if "gridcell" in selector:
                            try:
                                text_el = el.find_element(By.CSS_SELECTOR, "span[title]")
                                text = text_el.get_attribute("title")
                            except:
                                text = el.text.split('\n')[0] # First line is usually the name
                        else:
                            text = el.get_attribute("title")
                            if not text:
                                text = el.text

                        # Validation
                        if text and len(text) > 1:
                            # Cleanup
                            text = text.strip()
                            # 1. Exclude "Click here for contact info"
                            if "click here" in text.lower():
                                continue
                            # 2. Exclude member lists (lots of commas)
                            if text.count(',') > 3:
                                continue
                            # 3. Exclude time-only strings (simple heuristic)
                            if len(text) < 6 and ":" in text:
                                continue

                            logger.info(f"[Grabber] Found Active Group Name: '{text}'")
                            return text
                except Exception as loop_e:
                    continue
            
            logger.info("[Grabber]  Could not find name in sidebar, checking main header as fallback...")
            # Fallback to main header if sidebar fails completely
            try:
                header_title = self.driver.find_element(By.CSS_SELECTOR, "#main header span[title]").text
                if header_title:
                   return header_title
            except:
                pass

            return "Unknown_Group"

        except Exception as e:
            logger.error(f"[Grabber] Error getting group name: {e}")
            return "Unknown_Group"

    def _save_members(self, members: Dict[str, dict], method: str, group_name: str = "Unknown") -> Tuple[str, str]:
        """
        حفظ الأعضاء في ملف Excel موحد.
        يستخدم اسم المجموعة كاسم للـ Sheet.
        """
        try:
            # 1. Clean Data
            cleaned_data = [
                {
                    'name': member['name'],
                    'phone': member['phone'],
                    'extraction_method': method,
                    'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                for member in members.values()
            ]
            
            output_dir = os.path.join(self.project_root, 'data')
            os.makedirs(output_dir, exist_ok=True)
            
            # 2. Prepare Group Name for Excel Sheet (Sanitize)
            # Remove invalid chars for excel sheet names: : \ / ? * [ ]
            safe_sheet_name = re.sub(r'[\\/:\?\*\[\]]', '', group_name)
            safe_sheet_name = safe_sheet_name[:30]  # Excel max sheet name length is 31
            
            if not safe_sheet_name or safe_sheet_name.strip() == "":
                safe_sheet_name = f"Group_{datetime.now().strftime('%M%S')}"

            # 3. Define Main Workbook Path
            main_file = "whatsapp_marketing_leads.xlsx"
            filepath = os.path.join(output_dir, main_file)
            
            df = pd.DataFrame(cleaned_data)

            # 4. Smart Save (Append or Create)
            if os.path.exists(filepath):
                try:
                    # Try to append to existing file
                    with pd.ExcelWriter(filepath, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                        df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                    message = f" Updated existing workbook. Added sheet: '{safe_sheet_name}' ({len(cleaned_data)} members)"
                except Exception as file_error:
                    logger.warning(f"[Save] Could not append to {main_file} ({file_error}). creating new file...")
                    # Fallback incase file is corrupted or locked
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filepath = os.path.join(output_dir, f"leads_backup_{timestamp}.xlsx")
                    df.to_excel(filepath, sheet_name=safe_sheet_name, index=False)
                    message = f" Main file locked/error. Saved to new file: {filepath}"
            else:
                # Create new file
                df.to_excel(filepath, sheet_name=safe_sheet_name, index=False)
                message = f" Created new workbook. Sheet: '{safe_sheet_name}' ({len(cleaned_data)} members)"
            
            logger.info(f"[Save] {message}")
            return filepath, message
            
        except Exception as e:
            logger.error(f"[Save] Error: {e}")
            raise

    # ============================================================================
    # الوظائف الأخرى (Group Joiner, Number Filter, etc.)
    # ============================================================================

    def group_joiner(self, group_links: List[str]) -> List[str]:
        """
        Joins multiple WhatsApp groups from provided links.
        """
        if not self.driver:
            self.initialize_driver()
            if not self.load_whatsapp():
                return []
        
        joined_groups = []
        logger.info(f"[Joiner] Processing {len(group_links)} links...")
        
        for i, link in enumerate(group_links, 1):
            try:
                logger.info(f"[Joiner] ({i}/{len(group_links)}) Opening: {link}")
                self.driver.get(link)
                time.sleep(3)
                
                try:
                    join_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@role='button']//div[contains(text(), 'Join')]"))
                    )
                    join_btn.click()
                    logger.info(f"[Joiner]  Clicked Join for: {link}")
                    
                    time.sleep(2)
                    joined_groups.append(link)
                    time.sleep(random.randint(5, 15))
                    
                except TimeoutException:
                    logger.warning(f"[Joiner]  Join button not found for: {link}")
                except Exception as e:
                    logger.error(f"[Joiner]  Error joining: {e}")
                    
            except Exception as e:
                logger.error(f"[Joiner] Fatal error processing {link}: {e}")
        
        return joined_groups

    def number_filter(self, numbers: List[str]) -> List[str]:
        """
        Verifies which numbers have valid WhatsApp accounts.
        """
        if not self.driver:
            self.initialize_driver()
            if not self.load_whatsapp():
                return []
                
        valid_numbers = []
        logger.info(f"[Filter] Checking {len(numbers)} numbers...")
        
        for num in numbers:
            try:
                clean_num = re.sub(r'\D', '', num)
                if not clean_num: continue
                
                url = f"https://web.whatsapp.com/send?phone={clean_num}"
                self.driver.get(url)
                
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.find_elements(By.CSS_SELECTOR, "#main") or 
                                  d.find_elements(By.XPATH, "//div[contains(text(), 'invalid')]")
                    )
                    
                    if self.driver.find_elements(By.CSS_SELECTOR, "#main"):
                        logger.info(f"[Filter]  Valid: {clean_num}")
                        valid_numbers.append(clean_num)
                    else:
                        logger.info(f"[Filter]  Invalid: {clean_num}")
                
                except TimeoutException:
                    logger.warning(f"[Filter]  Timeout: {clean_num}")
                    
            except Exception as e:
                logger.error(f"[Filter] Error checking {num}: {e}")
                
        return valid_numbers

    def create_poll(self, question: str, options: List[str]):
        """
        Creates a poll in the currently open chat.
        """
        logger.info("[Poll] Poll creation feature - implementation pending")
        pass

