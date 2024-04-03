import scrapy
import time


class FixpricespiderSpider(scrapy.Spider):
    name = "fixpricespider"
    allowed_domains = ["fix-price.com"]
    start_urls = ["https://fix-price.com/catalog"]

    custom_settings ={
        'FEEDS':{
            'resultfixprice.json': {'format': 'json',
                                    'overwrite': True}
        }
    }

    def parse(self, response):

        spisok_dlya_parsa = ['https://fix-price.com/catalog/sad-i-ogorod']  # !!! Список ссылок на каталоги для обработки

        categories = response.xpath("//a[@class='title']")
        subcategories = response.xpath('//a[@class="title subtitle"]')

        for category in categories:
            link = 'https://fix-price.com' + category.attrib['href']
            link_to_pass = {'link_to_pass': link}
            if link in spisok_dlya_parsa:
                print('Нашел один в списке')
                yield response.follow(link, callback=self.parse_category, cb_kwargs=link_to_pass)

        for subcategory in subcategories:
            link = 'https://fix-price.com' + subcategory.attrib['href']
            link_to_pass = {'link_to_pass': link}
            if link in spisok_dlya_parsa:
                print('Нашел один в списке')
                yield response.follow(link,  callback=self.parse_category, cb_kwargs=link_to_pass)

    def parse_category(self, response, link_to_pass):

        link_to_pass = {'link_to_pass': link_to_pass}

        products = response.xpath("//div[@class='details']/div/div/a")
        for product in products:
            link = 'https://fix-price.com' + product.attrib['href']
            yield response.follow(link,  callback=self.parse_product)

        current_page = response.xpath("//a[@class = 'button active number']")
        if current_page:
            current_page_number = int(current_page.attrib['data-page'])
            max_page_number = int(
                response.xpath('//div[@class="pagination pagination"]/a[@class="button number"][last()]').attrib[
                    'data-page'])

        else:
            current_page_number = int(
                response.xpath("//a[@class = 'button nuxt-link-exact-active nuxt-link-active active number']").attrib['data-page'])
            max_page_number = int(
                response.xpath('//div[@class="pagination pagination"]/a[@class="button nuxt-link-active number"][last()]').attrib['data-page'])

        if current_page_number < max_page_number:
            current_page_number += 1
            link = f'{link_to_pass["link_to_pass"]}?page={current_page_number}'
            yield response.follow(link, callback=self.parse_category, cb_kwargs=link_to_pass)


    def parse_product(self, response):
        section = []

        timestamp = int(time.time())

        RPC = response.xpath("//span[text()='Код товара']/following-sibling::span/text()").get()

        url = response.request.url

        title = response.xpath("//h1[@class='title']/text()").get()

        brand = response.xpath("//span[text()='Бренд']/following-sibling::span//text()").get()
        if brand:
            pass

        section.append(response.xpath("//div[@id='bx_breadcrumb_0']//text()").get())
        section.append(response.xpath("//div[@id='bx_breadcrumb_1']//text()").get())
        section.append(response.xpath("//div[@id='bx_breadcrumb_2']//text()").get())


        #current = response.xpath("//div[@class='price-quantity-block']//div[@class='special-price']/text()").get()
        current = None
        original = response.xpath("//meta[@itemprop='price']").attrib['content']
        sale_tag = None
        price_data = {
            'current': current,
            'original': original,
            'sale_tag': sale_tag
        }

        main_image = response.xpath("//div[@class='slider gallery']//link").attrib['href']
        product_images = response.xpath("//div[@instancename='product-images']/div[1]/div//link")
        set_images = []
        for image in product_images:
            set_images.append(image.attrib['href'])
        assets = {'main_image': main_image,
                  'set_images': set_images}





        description = response.xpath("//div[@itemscope='itemscope']/div[@class='description']/text()").get()
        meta_title = response.xpath("//div[@class='properties']//p[@class='property']//span[@class='title']/text()").getall()
        meta_value = response.xpath("//div[@class='properties']//p[@class='property']//span[@class='value']/text()").getall()
        metadata = dict(zip(meta_title, meta_value))
        metadata['description'] = description

        yield {
            "timestamp": timestamp,
            "RPC": RPC,
            "url": url,
            "title": title,
            "brand": brand,
            "section": section,
            "price_data": price_data,
            'assets': assets,
            'metadata': metadata
        }

