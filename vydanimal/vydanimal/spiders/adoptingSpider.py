import scrapy

class AdoptingSpider(scrapy.Spider):
    name = "adopting"
    start_urls = [
        'http://vydanimal.org/listado'
    ]

    def parse(self, response):
        for in_adoption in response.css('div.cuadro_listado'):
            yield {
                'name': in_adoption.css('h2::text').extract_first(),
                'description': in_adoption.css('p.cuadro_listado_descripcion::text').extract_first(),
            }

        paginator = response.css('div.contNavPaginado')
        next_page = paginator.css('a[title="Página siguiente"]::attr(href)').extract_first()
        next_page = paginator.xpath('//a[text()="»"]/@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
