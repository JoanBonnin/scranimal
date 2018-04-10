import scrapy
import re
import sys

class AdoptingSpider(scrapy.Spider):

    BOOLEAN_ATTRIBUTE_TRUE = 'SI'
    BOOLEAN_ATTRIBUTE_FALSE = 'NO'
    ATTRIBUTE_NA = 'NA'

    name = "adopting"
    start_urls = [
        'http://vydanimal.org/listado'
    ]

    def parse(self, response):
        # Follow links to pet profiles
        for in_adoption in response.css('div.cuadro_listado'):
            url_profile = in_adoption.css('p.leer_completo  a::attr(href)').extract_first()
            yield response.follow(url_profile, self.scrap_profile)

        # Follow links to next dynamic pages
        paginator = response.css('div.contNavPaginado')
        next_page = paginator.xpath('//a[text()="»"]/@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def scrap_profile(self, response):
        pet_container = response.css('div.ficha_animal')

        data = {
            'id': self.extract_with_css('.ficha_id span::text', pet_container),
            'nombre': self.extract_with_css('.ficha_nombre span::text', pet_container),
            'estado': self.extract_status(pet_container),
            'urgente': self.extract_urgency(pet_container),
            'clase': self.extract_with_css('.ficha_tipo span::text', pet_container),
            'desde': self.extract_with_css('.ficha_desde span::text', pet_container),
            'sexo': self.extract_with_css('.ficha_sexo span::text', pet_container),
            'edad': self.extract_with_css('.ficha_edad span::text', pet_container),
            'nacimiento': self.extract_with_css('.ficha_nacimiento span::text', pet_container),
            'raza': self.extract_with_css('.ficha_raza span::text', pet_container),
            'tamano': self.extract_with_css('.ficha_tamanio span::text', pet_container),
            'localidad': self.extract_with_css('.ficha_localidad span::text', pet_container),
            'salud': self.extract_with_css('.ficha_salud::text', pet_container),
            'descripcion': self.extract_with_css('.ficha_descripcion  div::text', pet_container),
        }

        for key, value in data.items():
            data[key] = self.clean_attribute(value)

        yield data

    def extract_status(self, container):
        status = self.extract_with_css('strong.estado span::text', container)
        if status is None:
            return self.ATTRIBUTE_NA
        return status

    def extract_urgency(self, container):
        urgent = self.extract_with_css('strong.urgente span::text', container)
        if urgent is not None:
            urgent = self.BOOLEAN_ATTRIBUTE_TRUE
        else:
            urgent = self.BOOLEAN_ATTRIBUTE_FALSE
        return urgent

    # Create small function to avoid repeating code
    def extract_with_css(self, query, container):
        field = container.css(query).extract_first()

        if field is None:
            return self.ATTRIBUTE_NA
        return field

    def clean_attribute(self, attr):
        attr = re.sub("\n\t\r", "", attr)
        attr = re.sub("\s+", " ", attr) #Consecutive whitespaces
        attr.strip()
        return attr
