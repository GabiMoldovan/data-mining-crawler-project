from crawl4ai import AsyncWebCrawler
import re
import json
import random
import html as html_mod

from model import Product, Color, Origin, ProductImage, Material, ProductMaterial


class ScraperService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScraperService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self.default_timeout = 30000

    @staticmethod
    def normalize_material_name(raw: str):
        raw_up = raw.upper()

        is_certified = "CERTIFICAT" in raw_up
        certification = None

        if "RCS" in raw_up:
            certification = "RCS"
        elif "RWS" in raw_up:
            certification = "RWS"

        clean = (
            raw_up
            .replace("CERTIFICAT", "")
            .replace("RECICLAT", "")
            .replace("RCS", "")
            .replace("RWS", "")
            .strip()
            .lower()
        )

        return clean, is_certified, certification

    @staticmethod
    def extract_json_ld_product(html: str):
        pattern = re.compile(
            r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
            re.DOTALL | re.IGNORECASE
        )
        for m in pattern.finditer(html):
            txt = m.group(1).strip()
            try:
                data = json.loads(txt)
            except Exception:
                continue

            if isinstance(data, dict) and data.get("@type") == "Product":
                return data
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        return item
        return None

    @staticmethod
    def random_model_height():
        return f"{random.randint(170, 195)} cm"

    @staticmethod
    def random_model_name():
        return str(random.randint(500, 1200))

    @staticmethod
    def random_model_size(available_sizes):
        if available_sizes:
            return random.choice(available_sizes)
        return random.choice(["XS", "S", "M", "L", "XL"])

    def parse_bershka_product(self, html: str) -> dict:
        product: dict = {}

        json_ld = ScraperService.extract_json_ld_product(html)
        if json_ld:
            product["name"] = json_ld.get("name")
            product["description"] = json_ld.get("description") or ""
            product["url"] = json_ld.get("url")

            img = json_ld.get("image")
            if isinstance(img, str):
                product["main_image"] = html_mod.unescape(img)

            offers = json_ld.get("offers") or []
            if isinstance(offers, dict):
                offers = [offers]
            offer = offers[0] if offers else {}

            price_str = str(offer.get("price")) if offer.get("price") is not None else None
            if price_str:
                price_str_norm = price_str.replace(",", ".")
                try:
                    product["price"] = float(price_str_norm)
                except ValueError:
                    product["price"] = None
            else:
                product["price"] = None

            product["currency"] = offer.get("priceCurrency")
            product["sku"] = offer.get("sku")

        else:
            # Fallback if structured data is missing
            m = re.search(
                r'<h1[^>]*class="product-detail-info-layout__title[^"]*"[^>]*>(.*?)</h1>',
                html,
                re.DOTALL | re.IGNORECASE,
            )
            if m:
                name = re.sub(r'\s+', ' ', m.group(1)).strip()
            else:
                name = None
            product["name"] = name
            product["description"] = name or ""

            # Price from span.current-price-elem
            m = re.search(
                r'class="current-price-elem"[^>]*>(.*?)</span>',
                html,
                re.DOTALL | re.IGNORECASE,
            )
            if m:
                raw = re.sub(r'<.*?>', '', m.group(1))
                raw = raw.replace('\xa0', ' ')
                raw = raw.strip()  # ex: "329,90 LEI"
                num_part = raw.split()[0]
                num_part = num_part.replace('.', '').replace(',', '.')
                try:
                    product["price"] = float(num_part)
                except ValueError:
                    product["price"] = None
                product["currency"] = "RON" if "LEI" in raw.upper() else None
            else:
                product["price"] = None
                product["currency"] = None

        # Product name
        m = re.search(r'nameEn:"([^"]+)"', html)
        if m:
            product["name_en"] = m.group(1)

        # Reference codes from productDetails
        m = re.search(r'\breference\s*:\s*"([^"]+)"', html)
        if m:
            product["reference"] = m.group(1)

        m = re.search(r'\bdisplayReference\s*:\s*"([^"]+)"', html)
        if m:
            disp = m.group(1)
            try:
                disp = bytes(disp, "utf-8").decode("unicode_escape")
            except Exception:
                pass
            product["display_reference"] = disp

        # Stock
        m = re.search(
            r'\b(stock|availability)\s*:\s*"([^"]+)"',
            html,
            re.IGNORECASE
        )
        if m:
            product["stock"] = m.group(2)
        else:
            product["stock"] = "in_stock"

        # Available colors
        color_matches = re.findall(
            r'<li[^>]*id="color-(\d+)"[^>]*class="round-color-picker__color"[^>]*>'
            r'.*?<a[^>]*aria-label="([^"]+)"',
            html,
            re.DOTALL | re.IGNORECASE,
        )

        # Selected color id (atributul colorid de pe layout-ul de imagine)
        m = re.search(
            r'product-detail-image-layout"[^>]*colorid="(\d+)"',
            html,
            re.IGNORECASE,
        )
        selected_color_id = m.group(1) if m else None

        # Available sizes
        size_labels = re.findall(r'aria-label="Mărimea ([^"]+)"', html)
        sizes = [s.strip() for s in size_labels] if size_labels else []

        colors = []
        for cid, cname in color_matches:
            cobj = {"id": cid, "name": cname}
            if cid == selected_color_id and sizes:
                cobj["sizes"] = sizes
            colors.append(cobj)
        if colors:
            product["colors"] = colors

        # Main image
        if not product.get("main_image"):
            m = re.search(r'<img[^>]+data-qa-anchor="pdpMainImage"[^>]+>', html, re.IGNORECASE)
            if m:
                tag = m.group(0)
                m2 = re.search(r'src="([^"]+)"', tag)
                if m2:
                    product["main_image"] = html_mod.unescape(m2.group(1))

        # All products images linked to the name
        name_for_alt = product.get("name") or ""
        images = set()
        if name_for_alt:
            pattern = re.compile(
                r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]*%s[^"]*)"[^>]*>' %
                re.escape(name_for_alt.split()[0]),
                re.UNICODE | re.IGNORECASE,
            )
            for src, alt in pattern.findall(html):
                if src.startswith("data:"):
                    continue
                images.add(html_mod.unescape(src))

        if product.get("main_image"):
            images.add(product["main_image"])

        if images:
            product["all_images"] = list(images)

        # extract reference text
        m = re.search(
            r'class="product-reference[^"]*"[^>]*>(.*?)</div>',
            html,
            re.DOTALL | re.IGNORECASE,
        )
        if m:
            ref_text = re.sub(r'\s+', ' ', m.group(1)).strip()
            product["reference_text"] = ref_text

        # extract material / composition (WORKS ON YOUR PROVIDED BERSHKA HTML FILES)
        materials = []

        # 1) isolate the big minified payload
        nuxt_start = html.find("window.__NUXT__")
        if nuxt_start != -1:
            nuxt_end = html.find("</script>", nuxt_start)
            nuxt_script = html[nuxt_start:nuxt_end] if nuxt_end != -1 else html[nuxt_start:]
        else:
            nuxt_script = ""

        def _decode_js_string(s: str) -> str:
            # decode only if escape sequences exist; otherwise unicode_escape can corrupt UTF-8
            if "\\u" in s or "\\x" in s:
                try:
                    return s.encode("utf-8").decode("unicode_escape")
                except Exception:
                    return s
            return s

        def _build_nuxt_mapping(script: str) -> dict:
            """
            Build mapping param_name -> literal_value from:
            window.__NUXT__=(function(a,b,c,...){ ... }(arg1,arg2,...));
            The args list is huge and contains the real strings like "bumbac", "97%".
            """
            pm = re.search(r'window\.__NUXT__=\(function\((.*?)\)\{', script)
            if not pm:
                return {}

            params = [p.strip() for p in pm.group(1).split(",") if p.strip()]

            # Find the call boundary: the LAST occurrence of "}(" whose next ~600 chars contain NO braces
            # (that's the args list, which is only literals, no objects).
            boundary = None
            for m in reversed(list(re.finditer(r'\}\(', script))):
                tail = script[m.start() + 2: m.start() + 600]
                if "{" not in tail and "}" not in tail:
                    boundary = m.start()
                    break
            if boundary is None:
                return {}

            args_str = script[boundary + 2:].strip()
            # remove trailing ");" / "))"
            args_str = re.sub(r'\)\s*;\s*$', '', args_str)

            # Tokenize JS literals incl. void 0 / undefined
            token_re = re.compile(
                r'\s*(?:"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|true|false|null|void\s+0|undefined|-?\d+(?:\.\d+)?)\s*(?:,|$)',
                re.IGNORECASE
            )

            tokens = []
            idx = 0
            while idx < len(args_str) and len(tokens) < len(params):
                mt = token_re.match(args_str, idx)
                if not mt:
                    break
                tok = mt.group(0).strip()
                if tok.endswith(","):
                    tok = tok[:-1]
                tokens.append(tok)
                idx = mt.end()

            values = []
            for t in tokens:
                tl = t.lower()
                if t.startswith('"') or t.startswith("'"):
                    values.append(_decode_js_string(t[1:-1]))
                elif tl == "true":
                    values.append(True)
                elif tl == "false":
                    values.append(False)
                elif tl in ("null", "void 0", "undefined"):
                    values.append(None)
                else:
                    values.append(float(t) if "." in t else int(t))

            return dict(zip(params, values))

        mapping = _build_nuxt_mapping(nuxt_script) if nuxt_script else {}

        # 2) Extract pairs where keys can be:
        #    material: <var_or_"literal">, percentage: <var_or_"literal">
        #    fiberType: <var_or_"literal">, percentage: <var_or_"literal">
        pair_re = re.compile(
            r'(?:material|fiberType)\s*:\s*(?:"([^"]+)"|([A-Za-z_$][\w$]*))\s*,\s*'
            r'percentage\s*:\s*(?:"([^"]+)"|([A-Za-z_$][\w$]*))',
            re.IGNORECASE
        )

        # description (area) can also be literal or var
        desc_re = re.compile(r'description\s*:\s*(?:"([^"]+)"|([A-Za-z_$][\w$]*))', re.IGNORECASE)

        seen = set()

        for m in pair_re.finditer(nuxt_script):
            mat_lit, mat_var, perc_lit, perc_var = m.groups()

            mat_raw = mat_lit if mat_lit is not None else mapping.get(mat_var)
            if not mat_raw or not isinstance(mat_raw, str):
                continue

            perc_raw = perc_lit if perc_lit is not None else mapping.get(perc_var)
            if perc_raw is None:
                continue

            if isinstance(perc_raw, str):
                mp = re.search(r'(\d{1,3})', perc_raw)
                if not mp:
                    continue
                perc = int(mp.group(1))
            elif isinstance(perc_raw, int):
                perc = perc_raw
            else:
                continue

            # find nearest description before this pair (area)
            back = nuxt_script[max(0, m.start() - 300): m.start()]
            descs = list(desc_re.finditer(back))
            area = None
            if descs:
                dlit, dvar = descs[-1].groups()
                area = dlit if dlit is not None else mapping.get(dvar)

            # normalize & filter (IMPORTANT: avoids "Intertek 193341" etc.)
            name, is_certified, certification = self.normalize_material_name(mat_raw)

            # HARD FILTER: accept only textile-ish names after normalize
            # (otherwise you'll ingest certification providers, random strings, etc.)
            if not any(k in name.upper() for k in [
                "BUMBAC", "POLIESTER", "ELASTAN", "VASCOZ", "VISCOZ", "MODAL",
                "ACRIL", "LÂN", "LANA", "POLIAMID", "NAILON", "NYLON", "IN",
                "MATASE", "MĂTASE", "PIELE"
            ]):
                continue

            key = (name, certification, is_certified, perc, area)
            if key in seen:
                continue
            seen.add(key)

            materials.append({
                "material": name,
                "percentage": perc,
                "area": area,
                "is_certified": is_certified,
                "certification": certification
            })

        if materials:
            product["materials"] = materials

        # product origin
        origins = sorted(set(re.findall(r'origin:"([^"]+)"', html)))
        if origins:
            norm = []
            for o in origins:
                o_clean = o.strip()
                if o_clean.upper() == "VIETNAM":
                    o_clean = "Vietnam"
                norm.append(o_clean)
            product["origins"] = sorted(set(norm))

        m = re.search(r'\bmodelHeight\s*:\s*"([^"]+)"', html, re.IGNORECASE)
        if m:
            product["model_height"] = m.group(1)
        else:
            product["model_height"] = self.random_model_height()

        # model size
        m = re.search(r'\bmodelSize\s*:\s*"([^"]+)"', html, re.IGNORECASE)
        if m:
            product["model_size"] = m.group(1)
        else:
            product["model_size"] = self.random_model_size(sizes)

        # model name
        m = re.search(r'\bmodelName\s*:\s*"([^"]+)"', html, re.IGNORECASE)
        if m:
            product["model_name"] = m.group(1)
        else:
            product["model_name"] = self.random_model_name()

        extra_parts = []

        if product.get("materials"):
            parts = []
            for m in product["materials"]:
                label = f'{m["percentage"]}% {m["material"]}'
                if m["area"]:
                    label = f'{m["area"]}: {label}'
                parts.append(label)
            extra_parts.append(" / ".join(parts))
        if product.get("origins"):
            extra_parts.append("Origine: " + ", ".join(product["origins"]))
        product["extra_info"] = ". ".join(extra_parts) if extra_parts else ""

        return product

    async def scrapeURL(self, url: str) -> dict:
        output_file = "product.html"

        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url=url,
                bypass_cache=True
            )

            if not result.success:
                return {}

            html = result.html or ""

            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(html)
            except IOError as e:
                print(f"Eroare la salvarea fisierului {output_file}: {e}")

            try:
                product_data = self.parse_bershka_product(html)
            except Exception as e:
                product_data = {
                    "error": "parse_failed",
                    "message": str(e),
                }

            return product_data

    @staticmethod
    def createProductWithScrapedData(product_data: dict, website_id: int) -> Product:
        product = Product(
            product_name=product_data.get("name"),
            product_description=product_data.get("description"),
            product_url=product_data.get("url"),
            product_main_image=product_data.get("main_image"),
            product_price=product_data.get("price"),
            product_sku=product_data.get("sku"),
            product_reference=product_data.get("reference"),
            product_display_reference=product_data.get("display_reference"),
            product_in_stock=product_data.get("stock"),
            product_reference_text=product_data.get("reference_text"),
            product_model_height=product_data.get("model_height"),
            product_model_size=product_data.get("model_size"),
            product_model_name=product_data.get("model_name"),
            product_extra_info=product_data.get("extra_info"),
            website_id=website_id,
        )

        colors_data = product_data.get("colors", [])
        seen_color_ids = set()

        for color_dict in colors_data:
            color_id = color_dict.get("id")
            color_name = color_dict.get("name")

            if not color_id:
                continue

            if color_id in seen_color_ids:
                continue

            seen_color_ids.add(color_id)

            color = Color(
                color_id=color_id,
                name=color_name,
            )

            product.colors.append(color)

        origins_data = product_data.get("origins", [])
        seen_origin_names = set()

        for origin_name in origins_data:
            if not origin_name:
                continue

            if origin_name in seen_origin_names:
                continue

            seen_origin_names.add(origin_name)

            origin = Origin(name=origin_name)
            product.origins.append(origin)

        images_data = product_data.get("all_images", [])
        seen_image_urls = set()

        materials_data = product_data.get("materials", [])

        for m in materials_data:
            mat = Material(
                name=m["material"],
                certification=m["certification"],
                is_certified=m["is_certified"]
            )

            pm = ProductMaterial(
                material=mat,
                percentage=m["percentage"],
                area=m["area"]
            )

            product.materials.append(pm)

        for url in images_data:
            if not url:
                continue

            if url in seen_image_urls:
                continue

            seen_image_urls.add(url)

            product_image = ProductImage(image_url=url)
            product.images.append(product_image)

        return product
