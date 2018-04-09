import scrapy
import re
import sys

class AdoptingSpider(scrapy.Spider):
    name = "adopting"
    start_urls = [
        'http://vydanimal.org/listado'
    ]

    def parse(self, response):
        # Follow links to cat profiles
        for in_adoption in response.css('div.cuadro_listado'):
            url_profile = in_adoption.css('p.leer_completo  a::attr(href)').extract_first()
            yield response.follow(url_profile, self.scrap_profile)

        # Follow links to next dynamic pages
        paginator = response.css('div.contNavPaginado')
        next_page = paginator.xpath('//a[text()="»"]/@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def scrap_profile(self, response):
        # Create small function to avoid repeating code
        def extract_with_css(query):
            container = response.css('div.ficha_animal')
            field = container.css(query).extract_first()
            if field is not None:
                return field.strip()
            else:
                return None

        # Look for cat status
        status = extract_with_css('strong.estado span::text')

        if status is None:
            status = '-'

        # Look for urgency on adoption
        urgent = extract_with_css('strong.urgente span::text')

        if urgent is not None:
            urgent = 'Sí'
        else:
            urgent = 'NO'

        yield {
            'id': extract_with_css('dd.ficha_id::text'),
            'nombre': extract_with_css('dd.ficha_nombre::text'),
            'estado': status,
            'urgente': urgent,
            'clase': extract_with_css('dd.ficha_tipo::text'),
            'desde': extract_with_css('dd.ficha_desde::text'),
            'sexo': extract_with_css('dd.ficha_sexo::text'),
            'edad': extract_with_css('dd.ficha_edad::text'),
            'nacimiento': extract_with_css('dd.ficha_nacimiento::text'),
            'raza': extract_with_css('dd.ficha_raza::text'),
            'tamano': extract_with_css('dd.ficha_tamanio::text'),
            'localidad': re.sub('\xa0\n\t\t', '', extract_with_css('dd.ficha_localidad::text')),
            'salud': extract_with_css('dd.ficha_salud::text'),
            'descripcion': re.sub('\r\n', '', extract_with_css('dd.descripcion div::text')),


        }

