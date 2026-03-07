import asyncio
import pandas as pd
from typing import List, Dict, Optional
from backend.cloud_service import cloud_service


class MembersGrabberController:
    """
    Stateless Controller for Members Grabber (SaaS Multitenant).
    """

    async def fetch_groups(self, instance_name: str) -> List[Dict]:
        """Fetches available groups using user's WhatsApp instance."""
        try:
            # Pass instance_name to cloud_service (needs update in cloud_service too)
            res = await asyncio.to_thread(
                cloud_service.fetch_all_groups, instance_name=instance_name
            )

            def extract_group_name(g):
                name = (
                    g.get("name") or g.get("subject") or g.get("groupName") or "Unknown"
                )
                if isinstance(name, dict):
                    name = name.get("text") or name.get("name") or str(name)
                elif not isinstance(name, str):
                    name = str(name) if name else "Unknown"
                if "[object" in name.lower():
                    name = g.get("id", "Unknown Group")
                return name

            def extract_group_id(g):
                gid = g.get("id") or g.get("jid") or g.get("groupId")
                if isinstance(gid, dict):
                    gid = gid.get("_serialized") or str(gid)
                return gid

            groups = []
            if isinstance(res, list):
                for g in res:
                    if isinstance(g, dict):
                        gid = extract_group_id(g)
                        if gid:
                            groups.append(
                                {"label": extract_group_name(g), "value": gid}
                            )
            elif isinstance(res, dict):
                data = res.get("data") or res.get("groups") or []
                if isinstance(data, list):
                    for g in data:
                        if isinstance(g, dict):
                            gid = extract_group_id(g)
                            if gid:
                                groups.append(
                                    {"label": extract_group_name(g), "value": gid}
                                )

            return groups
        except Exception as e:
            print(f"[ERROR] Fetch Groups SaaS: {e}")
            return []

    async def grab_members(self, jid: str, instance_name: str) -> List[Dict]:
        """Grabs participants from a specific group using user instance."""
        try:
            members_res = await asyncio.to_thread(
                cloud_service.fetch_group_participants, jid, instance_name=instance_name
            )

            members = []
            if isinstance(members_res, list):
                members = members_res
            elif isinstance(members_res, dict):
                if "participants" in members_res:
                    members = members_res["participants"]
                elif "data" in members_res:
                    data_val = members_res["data"]
                    if isinstance(data_val, list):
                        members = data_val
                    elif isinstance(data_val, dict) and "participants" in data_val:
                        members = data_val["participants"]

            formatted = []
            for m in members:
                jid_str = ""
                admin_status = False

                if isinstance(m, dict):
                    jid_str = m.get("id") or m.get("jid") or m.get("number") or str(m)
                    admin_status = (
                        m.get("admin")
                        or m.get("isAdmin")
                        or m.get("isSuperAdmin", False)
                    )
                elif isinstance(m, str):
                    jid_str = m
                else:
                    jid_str = str(m) if m else "unknown"

                if not isinstance(jid_str, str):
                    jid_str = str(jid_str) if jid_str else "unknown"

                if "[object" in jid_str.lower() or jid_str == "unknown":
                    continue

                phone = jid_str.split("@")[0] if "@" in jid_str else jid_str
                phone_clean = "".join(c for c in phone if c.isdigit() or c == "+")

                formatted.append(
                    {
                        "name": jid_str,
                        "phone": phone_clean if phone_clean else phone,
                        "status": "Admin" if admin_status else "Member",
                    }
                )

            return formatted
        except Exception as e:
            print(f"[ERROR] Grab Members SaaS: {e}")
            return []

    def export_to_excel(self, members: List[Dict], path: str) -> Optional[str]:
        """Exports the provided members list to an Excel file."""
        if not members:
            return None

        try:
            df = pd.DataFrame(members)
            df.to_excel(path, index=False)
            return path
        except Exception as e:
            print(f"[ERROR] Export Excel SaaS: {e}")
            return None
