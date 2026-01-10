import time
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


class CrawlerService:
    _instance = None
    _driver = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CrawlerService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self._init_driver()

    def _init_driver(self):
        # Initialize Selenium WebDriver
        if self._driver is None:
            try:
                # Configure Chrome options
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_argument(
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

                # Exclude automation flags
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)

                # Setup driver with automatic driver management
                service = Service(ChromeDriverManager().install())
                self._driver = webdriver.Chrome(service=service, options=chrome_options)

                # Execute CDP commands to hide automation
                self._driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                print("Selenium WebDriver initialized successfully")

            except Exception as e:
                print(f"Error initializing WebDriver: {e}")
                raise

    def _normalize_url(self, url):
        # Normalize URL by removing fragments and ensuring consistent format
        url, _ = urldefrag(url)
        # Ensure URL starts with https and has consistent format
        if url.startswith('http://'):
            url = url.replace('http://', 'https://', 1)
        return url.rstrip('/')

    def _is_valid_url(self, url, base_domain, required_path='/ro/'):
        """
        Check if URL is valid and meets our criteria
        - Must be same domain as base_domain
        - Must have /ro/ in the path after domain
        - Must not be excluded file types
        """
        try:
            parsed = urlparse(url)

            # Check if URL has valid scheme
            if parsed.scheme not in ('http', 'https'):
                return False

            # Check if same domain
            if parsed.netloc != base_domain:
                return False

            # CRITICAL: Check if URL contains /ro/ after domain
            # This ensures we only get Romanian pages
            if required_path:
                # Check if the path starts with /ro or contains /ro/
                path = parsed.path
                if not (path.startswith('/ro') or '/ro/' in path):
                    return False

            # Check if it's a file we don't want
            invalid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.zip', '.mp4', '.mp3']
            if any(parsed.path.lower().endswith(ext) for ext in invalid_extensions):
                return False

            # Filter out social media and external links
            social_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com', 'tiktok.com']
            if any(social in parsed.netloc.lower() for social in social_domains):
                return False

            # Additional check: URL must start with https://www.bershka.com/ro
            if not url.startswith(f'https://{base_domain}/ro'):
                return False

            return True
        except Exception:
            return False

    def _get_links_from_page(self, url):
        # Extract all links from a page using Selenium
        links = set()

        try:
            print(f"  Loading page: {url}")
            self._driver.get(url)

            # Wait for page to load
            time.sleep(2)

            # Try to wait for some content to load
            try:
                WebDriverWait(self._driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                print(f"  Timeout waiting for page to load")
                return links

            # Scroll to load dynamic content
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Try to find all links
            try:
                all_links = self._driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href')
                    if href:
                        links.add(href)

            except Exception as e:
                print(f"  Error extracting links: {e}")

            print(f"  Found {len(links)} raw links")
            return links

        except Exception as e:
            print(f"  Error loading page: {e}")
            return links

    def dfsCrawl(self, start_url, max_pages=50):
        # Crawl website using DFS (Depth First Search) Algorithm with Selenium
        visited = set()
        to_visit = deque([start_url])
        parsed_start = urlparse(start_url)
        base_domain = parsed_start.netloc

        print(f"\nStarting crawl of {base_domain}...")
        print(f"Start URL: {start_url}")
        print(f"Required path: /ro/")
        print(f"Max pages: {max_pages}\n")

        try:
            while to_visit and len(visited) < max_pages:
                url = to_visit.pop()
                normalized_url = self._normalize_url(url)

                if normalized_url in visited:
                    continue

                print(f"Crawling [{len(visited) + 1}/{max_pages}]: {normalized_url}")

                # Get links from current page
                new_links = self._get_links_from_page(normalized_url)
                visited.add(normalized_url)

                # Process found links
                valid_links = 0
                for link in new_links:
                    try:
                        absolute_url = urljoin(normalized_url, link)
                        normalized_absolute = self._normalize_url(absolute_url)

                        if self._is_valid_url(normalized_absolute, base_domain, required_path='/ro/'):
                            if (normalized_absolute not in visited and
                                    normalized_absolute not in to_visit):
                                to_visit.append(normalized_absolute)
                                valid_links += 1
                    except Exception as e:
                        continue

                print(f"  Added {valid_links} new URLs to crawl queue")
                print(f"  Total in queue: {len(to_visit)}, Visited: {len(visited)}\n")

        except KeyboardInterrupt:
            print("\nCrawl interrupted by user")
        except Exception as e:
            print(f"\nError during crawl: {e}")
        finally:
            print(f"\nCrawl completed!")
            print(f"Total unique pages crawled: {len(visited)}")
            print(f"Remaining in queue: {len(to_visit)}")

            return list(visited)

    def filter_ro_urls(self, urls):
        # Filter URLs to keep only those containing /ro/ after domain
        filtered = []
        for url in urls:
            normalized = self._normalize_url(url)
            if '/ro/' in normalized and normalized.startswith('https://www.bershka.com'):
                filtered.append(normalized)
        return filtered

    def categorize_urls(self, urls):
        # Categorize URLs into product pages, category pages, and other pages
        product_urls = [url for url in urls if 'c0p' in url.lower()]
        category_urls = [url for url in urls if '/ro/' in url.lower() and 'c0p' not in url.lower()]
        other_urls = [url for url in urls if url not in product_urls and url not in category_urls]

        return {
            'product_urls': product_urls,
            'category_urls': category_urls,
            'other_urls': other_urls,
            'total': len(urls),
            'product_count': len(product_urls),
            'category_count': len(category_urls),
            'other_count': len(other_urls)
        }

    def validate_urls(self, urls):
        # Validate that all URLs start with https://www.bershka.com/ro and contain /ro/ pattern
        invalid_start_urls = []
        missing_ro_pattern_urls = []

        for url in urls:
            if not url.startswith('https://www.bershka.com/ro'):
                invalid_start_urls.append(url)
            if '/ro/' not in url:
                missing_ro_pattern_urls.append(url)

        return {
            'invalid_start_urls': invalid_start_urls,
            'missing_ro_pattern_urls': missing_ro_pattern_urls,
            'all_valid_start': len(invalid_start_urls) == 0,
            'all_have_ro_pattern': len(missing_ro_pattern_urls) == 0
        }

    def save_results(self, urls, categorization, validation, start_url, output_files=True):
        # Save crawl results to files
        if not output_files:
            return

        # Save all URLs to file
        if urls:
            with open('crawled_urls.txt', 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(url + '\n')
            print(f"\nFull list saved to 'crawled_urls.txt'")

            # Save summary
            #with open('crawl_summary.txt', 'w', encoding='utf-8') as f:
            #    f.write(f"Crawl Summary\n")
            #    f.write(f"==============\n")
            #    f.write(f"Start URL: {start_url}\n")
            #    f.write(f"Total URLs found: {categorization['total']}\n")
            #    f.write(f"Product pages: {categorization['product_count']}\n")
            #    f.write(f"Category pages: {categorization['category_count']}\n")
            #    f.write(f"Other pages: {categorization['other_count']}\n\n")
            #    f.write(f"All URLs start with https://www.bershka.com/ro: {'Yes' if validation['all_valid_start'] else 'No'}\n")
            #    f.write(f"All URLs contain /ro/: {'Yes' if validation['all_have_ro_pattern'] else 'No'}\n")
            #print(f"Summary saved to 'crawl_summary.txt'")

            # Save categorized URLs
            with open('product_urls.txt', 'w', encoding='utf-8') as f:
                for url in categorization['product_urls']:
                    f.write(url + '\n')
            print(f"Product URLs saved to 'product_urls.txt'")

            with open('category_urls.txt', 'w', encoding='utf-8') as f:
                for url in categorization['category_urls']:
                    f.write(url + '\n')
            print(f"Category URLs saved to 'category_urls.txt'")

    def crawl_website(self, start_url, max_pages=50, output_files=True):
        # Main method to crawl website and return all results
        print("=" * 60)
        print("Starting Web Crawler with Selenium")
        print("=" * 60)

        # Start crawling
        raw_result = self.dfsCrawl(start_url, max_pages)

        print("\n" + "=" * 60)
        print("Crawl Results:")
        print("=" * 60)

        # Apply additional filtering to ensure all URLs contain /ro/
        filtered_result = self.filter_ro_urls(raw_result)

        print(f"Found {len(raw_result)} raw URLs")
        print(f"After filtering for /ro/: {len(filtered_result)} URLs\n")

        # Categorize URLs
        categorization = self.categorize_urls(filtered_result)

        print(f"Product pages: {categorization['product_count']}")
        print(f"Category pages: {categorization['category_count']}")
        print(f"Other pages: {categorization['other_count']}")

        # Validate URLs
        print("\n" + "=" * 60)
        print("URL Validation Check:")
        print("=" * 60)

        validation = self.validate_urls(filtered_result)

        if validation['invalid_start_urls']:
            print(f"WARNING: Found {len(validation['invalid_start_urls'])} URLs that don't start with https://www.bershka.com/ro")
            for url in validation['invalid_start_urls']:
                print(f"  [INVALID] {url}")
        else:
            print("[OK] All URLs start with https://www.bershka.com/ro")

        if validation['missing_ro_pattern_urls']:
            print(f"\nWARNING: Found {len(validation['missing_ro_pattern_urls'])} URLs without /ro/ pattern:")
            for url in validation['missing_ro_pattern_urls']:
                print(f"  [INVALID] {url}")
        else:
            print("[OK] All URLs contain /ro/ pattern")

        # Print sample URLs
        if filtered_result:
            print(f"\nValid URLs:")
            for i, url in enumerate(filtered_result):
                status = "[OK]" if url.startswith('https://www.bershka.com/ro') else "[FAIL]"
                print(f"  {i + 1:2d}. {status} {url}")

        # Save results to files
        self.save_results(filtered_result, categorization, validation, start_url, output_files)

        # Return comprehensive results
        return {
            'raw_urls': raw_result,
            'filtered_urls': filtered_result,
            'categorization': categorization,
            'validation': validation,
            'sample_urls': filtered_result if filtered_result else []
        }

    def close(self):
        try:
            if self._driver:
                self._driver.quit()
        except Exception:
            pass
        finally:
            self._driver = None
            self._initialized = False
            CrawlerService._instance = None
            print("WebDriver fully stopped")
