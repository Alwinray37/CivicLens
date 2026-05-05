import re
import pymupdf

class PdfExtraction:

    @staticmethod
    def extract_pdf_raw_text(pdf_filename: str):
        parts = []
        with pymupdf.open(pdf_filename) as doc:
            for page in doc:
                parts.append(page.get_text())
        return "\n".join(parts)
    
    @staticmethod
    def extract_agenda_items(pdf_text: str):
        pattern = re.compile(
            r"\((\d+)\)\s*"                       
            r"(\d{2}-\d{4}(?:-S\d+)?)\s*"        
            r"(?:CD\s*\d+)?\s*"                 
            r"(.+?)(?=\n\(\d+\)\s|$)",           
            re.DOTALL
        )

        junk_line = re.compile(
            r"^(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b"
            r"|^PAGE\b|^- .* -$|^(?:https?://|www\.)",
            re.I
        )

        first_sentence = re.compile(
            r"^(.*?\.)\s*(?=(?:Recommendations?|Fiscal|Community|URGENCY|Items\b|\()|$)",
            re.I | re.DOTALL
        )

        items = []
        for m in pattern.finditer(pdf_text):
            item_no, file_no, block = m.groups()

            block = block.split("\n(", 1)[0]

            lines = [ln.strip() for ln in block.splitlines()
                    if ln.strip() and not junk_line.match(ln.strip())]
            text = re.sub(r"\s+", " ", " ".join(lines)).strip(" -")

            mm = first_sentence.match(text)
            title = (mm.group(1) if mm else text).strip()

            _, _, after_title = text.partition(title)
            after_title = after_title.strip()

            if title:
                items.append({"item_number": item_no, "file_number": file_no, "title": title, "description": after_title})
        return items
    
    @staticmethod
    def extract_roll_call(text: str):
        # Grab everything between "Roll Call" and "Approval of the Minutes"
        m = re.search(r"Roll Call(.*?)(Approval of the Minutes)",
                    text, re.DOTALL | re.IGNORECASE)
        if not m:
            return None

        rc_block = m.group(1)
        norm = re.sub(r"\s+", " ", rc_block).strip()

        m2 = re.search(
            r"Members Present:\s*(?P<present>.+?)\s*;?\s*Absent:\s*(?P<absent>.+)",
            norm,
            re.IGNORECASE
        )
        if not m2:
            return {"raw_text": norm}

        present_str = m2.group("present").strip()
        absent_str = m2.group("absent").strip()

        def parse_names_and_count(seg: str):
            seg = seg.strip()
            count = None

            # counts like "(1 4)" or "( 1)"
            mcount = re.search(r"\(([\d\s]+)\)\s*$", seg)
            if mcount:
                digits = "".join(ch for ch in mcount.group(1) if ch.isdigit())
                if digits:
                    count = int(digits)
                seg = seg[:mcount.start()].strip(" ,;")

            names = [n.strip() for n in seg.split(",") if n.strip()]
            return names, count

        present_names, present_count = parse_names_and_count(present_str)
        absent_names, absent_count = parse_names_and_count(absent_str)

        return {
            "members_present": present_names,
            "present_count": present_count if present_count is not None else len(present_names),
            "members_absent": absent_names,
            "absent_count": absent_count if absent_count is not None else len(absent_names),
            "raw_text": norm,
        }

    @staticmethod
    def extract_minutes_items(text: str):
        # Each item block in the minutes
        item_pattern = re.compile(
            r"\((\d+)\)\s*"                        # (item_number)
            r"(\d{2}-\d{4}(?:-S\d+)?)\s*"          # file_number
            r"(?:CD\s*\d+)?\s*"                    # optional "CD 1" etc
            r"(.+?)(?=\n\(\d+\)\s|\Z)",            # block until next "(n)" or end
            re.DOTALL
        )

        junk_line = re.compile(
            r"^(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b"
            r"|^PAGE\b|^- .* -$|^(?:https?://|www\.)",
            re.I
        )

        # Use the first sentence as "title", stop before Recommendations/Fiscal/etc.
        first_sentence = re.compile(
            r"^(.*?\.)\s*(?=(?:Recommendations?|Recommendation|Fiscal|Community|URGENCY|Items\b|\()|$)",
            re.I | re.DOTALL
        )

        # For votes we need both "Adopted Item" and "Adopted Motion ..."
        # Tighten this so the vote block stops right after "Absent: ... (count)"
        vote_block_pattern = re.compile(
            r"(Adopted (?:Item|Motion).*?)"                 # adoption phrase
            r"(Ayes:.*?Absent:[^()]*\([\d\s]+\))",         # from Ayes: ... through Absent (...) only
            re.IGNORECASE | re.DOTALL
        )

        # Ayes/Nays/Absent line – only allow names (no parentheses) in the name parts
        vote_line_pattern = re.compile(
            r"Ayes:\s*(?P<ayes_names>[^()]*?)\s*\((?P<ayes_count>[\d\s]+)\)\s*;\s*"
            r"Nays:\s*(?P<nays_names>[^()]*?)\s*\((?P<nays_count>[\d\s]+)\)\s*;\s*"
            r"Absent:\s*(?P<absent_names>[^()]*?)\s*\((?P<absent_count>[\d\s]+)\)",
            re.IGNORECASE
        )

        def split_names(s: str):
            s = s.strip(" ,;")
            if not s:
                return []
            return [n.strip() for n in s.split(",") if n.strip()]

        def parse_count(raw: str, names_list):
            if raw:
                digits = "".join(ch for ch in raw if ch.isdigit())
                if digits:
                    return int(digits)
            return len(names_list) if names_list else None

        items = []

        for m in item_pattern.finditer(text):
            item_no, file_no, block = m.groups()

            # --- votes inside this block ---
            vb = vote_block_pattern.search(block)
            vote_info = None

            if vb:
                adoption_phrase = re.sub(r"\s+", " ", vb.group(1)).strip()
                vote_text = re.sub(r"\s+", " ", vb.group(2)).strip()

                vm = vote_line_pattern.search(vote_text)
                if vm:
                    ayes_names = split_names(vm.group("ayes_names") or "")
                    nays_names = split_names(vm.group("nays_names") or "")
                    absent_names = split_names(vm.group("absent_names") or "")

                    ayes_count = parse_count(vm.group("ayes_count"), ayes_names)
                    nays_count = parse_count(vm.group("nays_count"), nays_names)
                    absent_count = parse_count(vm.group("absent_count"), absent_names)

                    vote_info = {
                        "adoption_phrase": adoption_phrase,
                        "ayes": ayes_names,
                        "nays": nays_names,
                        "absent": absent_names,
                        "ayes_count": ayes_count,
                        "nays_count": nays_count,
                        "absent_count": absent_count,
                        "raw_vote_text": vote_text,
                    }
                else:
                    vote_info = {
                        "adoption_phrase": adoption_phrase,
                        "raw_vote_text": vote_text,
                    }

                narrative_block = block[:vb.start()]
            else:
                narrative_block = block

            # Just in case, nuke any stray "Adopted Item/Motion" text
            narrative_block = re.split(r"\nAdopted (?:Item|Motion)\b", narrative_block, 1)[0]

            # Clean up into a single string
            lines = [
                ln.strip()
                for ln in narrative_block.splitlines()
                if ln.strip() and not junk_line.match(ln.strip())
            ]
            text_clean = re.sub(r"\s+", " ", " ".join(lines)).strip(" -")

            mm = first_sentence.match(text_clean)
            title = (mm.group(1) if mm else text_clean).strip()
            _, _, after_title = text_clean.partition(title)
            description = after_title.strip()

            items.append({
                "item_number": item_no,
                "file_number": file_no,
                "title": title,
                "description": description,
                "vote": vote_info,
            })

        return items

    @staticmethod
    def extract_motions(text: str):
        # Each motion block from the back of the minutes
        motion_pattern = re.compile(
            r"ITEM NO\.\s*(\d+)\s+.*?MOTION\s+(.+?)(?=\nITEM NO\.|\Z)",
            re.DOTALL
        )

        motions = []

        for m in motion_pattern.finditer(text):
            item_no, body = m.groups()

            # Drop PRESENTED/SECONDED signature boilerplate from the motion text
            body_main = body.split("PRESENTED BY", 1)[0]
            motion_text = re.sub(r"\s+", " ", body_main).strip()

            motions.append({
                "item_number": item_no,
                "motion_text": motion_text,
            })

        return motions

    @staticmethod
    def extract_minutes_structured(pdf_text: str):
        roll = PdfExtraction.extract_roll_call(pdf_text)
        items = PdfExtraction.extract_minutes_items(pdf_text)
        motions = PdfExtraction.extract_motions(pdf_text)

        # Attach motions to the matching items by item_number
        motion_map = {m["item_number"]: m for m in motions}
        for it in items:
            m = motion_map.get(it["item_number"])
            if m:
                it["motion"] = m["motion_text"]

        return {
            "roll_call": roll,
            "items": items,
        }
