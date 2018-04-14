import scrapy
import re
from urllib.parse import urlparse
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import sys

class AdoptingSpider(scrapy.Spider):

    BOOLEAN_ATTRIBUTE_TRUE = 'SI'
    BOOLEAN_ATTRIBUTE_FALSE = 'NO'
    ATTRIBUTE_NA = 'NA'

    name = "adopting"

    start_urls = [
        "http://bambu-cms.org/quien-usa"
    ]

    def parse(self, response):
        # All active shelters are in the first list
        active_shelters = response.xpath('//div[@id="contenidos"]//ul[@id="protes"][1]//li//a/@href')

        # Follow link to shelter page (if exists)
        for shelter in active_shelters:
            url_shelter = shelter.extract()

            # Some URLs do not finish with a slash
            if(url_shelter[-1] == '/'):
                url_shelter = url_shelter + 'listado'
            else:
                url_shelter = url_shelter + '/listado'

            yield response.follow(url_shelter, self.scrap_shelter, errback=self.url_error)

    def scrap_shelter(self, response):
        # Follow links to pet profiles
        for in_adoption in response.css('div.cuadro_listado'):
            url_profile = in_adoption.css('p.leer_completo  a::attr(href)').extract_first()
            yield response.follow(url_profile, self.scrap_profile, errback=self.url_error)

        # Follow links to next dynamic pages
        paginator = response.css('div.contNavPaginado')
        next_page = paginator.xpath('//a[text()="»"]/@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse, errback=self.url_error)

    def url_error(self, failure):
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    def scrap_profile(self, response):
        pet_container = response.css('div.ficha_animal')

        data = {
            'id': self.extract_id(pet_container),
            'nombre': self.extract_name(pet_container),
            'estado': self.extract_status(pet_container),
            'urgente': self.extract_urgency(pet_container),
            'clase': self.extract_class(pet_container),
            'desde': self.extract_since(pet_container),
            'sexo': self.extract_gender(pet_container),
            'edad': self.extract_age(pet_container),
            'nacimiento': self.extract_birthday(pet_container),
            'raza': self.extract_race(pet_container),
            'tamano': self.extract_size(pet_container),
            'localidad': self.extract_state(pet_container),
            'salud': self.extract_health(pet_container),
            'descripcion': self.extract_description(pet_container),
            'dominio': self.get_domain(response),
        }

        for key, value in data.items():
            data[key] = self.format_attribute(value)

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

    def format_attribute(self, attr):
        if attr is None:
            return self.ATTRIBUTE_NA

        attr = re.sub("\n\t\r", "", attr)
        attr = re.sub("\s+", " ", attr) #Consecutive whitespaces
        attr.strip()
        return attr

    def get_domain(self, response):
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return domain

    def try_multiple_css_selectors(self, queries, container):
        for query in queries:
            res = self.extract_with_css(query, container)
            if res is not None:
                return res

    def extract_id(self, pet_container):
        id = self.try_multiple_css_selectors(
            ['.ficha_id span::text', 'dd.ficha_id::text'],
            pet_container
        )
        return id


    def extract_name(self, pet_container):
        name = self.try_multiple_css_selectors(
            ['.ficha_nombre span::text', 'dd.ficha_nombre::text'],
            pet_container
        )
        return name

    def extract_class(self, pet_container):
        _class = self.try_multiple_css_selectors(
            ['.ficha_clase span::text', 'dd.ficha_clase::text'],
            pet_container
        )
        return _class

    def extract_since(self, pet_container):
        since = self.try_multiple_css_selectors(
            ['.ficha_since span::text', 'dd.ficha_since::text'],
            pet_container
        )
        return since

    def extract_gender(self, pet_container):
        gender = self.try_multiple_css_selectors(
            ['.ficha_desde span::text', 'dd.ficha_desde::text'],
            pet_container
        )
        return gender

    def extract_age(self, pet_container):
        age = self.try_multiple_css_selectors(
            ['.ficha_edad span::text', 'dd.ficha_edad::text'],
            pet_container
        )
        return age

    def extract_birthday(self, pet_container):
        birthday = self.try_multiple_css_selectors(
            ['.ficha_nacimiento span::text', 'dd.ficha_nacimiento::text'],
            pet_container
        )
        return birthday

    def extract_race(self, pet_container):
        race = self.try_multiple_css_selectors(
            ['.ficha_raza span::text', 'dd.ficha_raza::text'],
            pet_container
        )
        return race

    def extract_size(self, pet_container):
        size = self.try_multiple_css_selectors(
            ['.ficha_tamano span::text', 'dd.ficha_tamano::text'],
            pet_container
        )
        return size

    def extract_state(self, pet_container):
        state = self.try_multiple_css_selectors(
            ['.ficha_localidad span::text', 'dd.ficha_localidad::text'],
            pet_container
        )
        return state

    def extract_health(self, pet_container):
        health = self.try_multiple_css_selectors(
            ['.ficha_salud::text', 'dd.ficha_salud::text'],
            pet_container
        )
        return health

    def extract_description(self, pet_container):
        desc = self.try_multiple_css_selectors(
            ['.ficha_descripcion div::text', 'dd.ficha_descripcion div::text'],
            pet_container
        )
        return desc
