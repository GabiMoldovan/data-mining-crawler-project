from crawl4ai import AsyncWebCrawler
import re
import json
import html as html_mod

from model import Product, Color, Origin, ProductImage


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
    def parse_bershka_product(html: str) -> dict:
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
        m = re.search(r'reference:"([^"]+)"', html)
        if m:
            product["reference"] = m.group(1)

        m = re.search(r'displayReference:"([^"]+)"', html)
        if m:
            disp = m.group(1)
            try:
                disp = bytes(disp, "utf-8").decode("unicode_escape")
            except Exception:
                pass
            product["display_reference"] = disp

        # Stock
        m = re.search(r'currentProduct:{[^}]*stock:"([^"]+)"', html)
        if m:
            product["stock"] = m.group(1)

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

        # extract material/composition
        m = re.search(
            r'title:"UMPLUTURĂ".*?fiberType:"([^"]+)".*?percentage:"([^"]+)"',
            html,
            re.DOTALL | re.IGNORECASE,
        )
        materials = []
        if m:
            fiber, perc = m.groups()
            materials.append(f"Umplutura: {perc} {fiber.title()}")
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

        # model height, model size and model name
        m = re.search(
            r'modelHeight:"([^"]+)",modelSize:"([^"]+)",modelName:"([^"]+)"',
            html,
            re.IGNORECASE,
        )
        if m:
            h, size, name_code = m.groups()
            product["model_height"] = h
            product["model_size"] = size
            product["model_name"] = name_code

        extra_parts = []
        if product.get("materials"):
            extra_parts.append(" / ".join(product["materials"]))
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

    def createProduct(self, product_data: dict, website_id: int) -> Product:
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

        for url in images_data:
            if not url:
                continue

            if url in seen_image_urls:
                continue

            seen_image_urls.add(url)

            product_image = ProductImage(image_url=url)
            product.images.append(product_image)

        return product