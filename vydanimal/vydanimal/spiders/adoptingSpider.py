import scrapy
import re
from urllib.parse import urlparse
import sys

class AdoptingSpider(scrapy.Spider):

    start_urls = [
        "http://adamprotectora.org/listado",
        "http://protectoradeibi.com/listado",
        "http://asokaelgrande.org/listado",
        "http://nuevavida-adopciones.org/listado",
        "http://caballoastur.com/listado",
        "http://protectoraoriolana.org/listado",
        "http://adoptam.org/listado",
        "http://protectora-apadac.org/listado",
        "http://adoptamics.org/listado",
        "http://laperritavaliente.org/listado",
        "http://saraprotectora.org/listado",
        "http://protectorayecla.com/listado",
        "http://protectoradecastalla.org/listado",
        "http://proteccionfelina.org/listado",
        "http://barcelonagatigos.org/listado",
        "http://fundaciosilvestre.org/listado",
        "http://www.vydanimal.org/listado",
        "http://adoptasalvaunavida.com/listado",
        "http://protectoraosbiosbardos.org/listado",
        "http://alicanteadopta.org/listado",
        "http://argos-sevilla.org/listado",
        "http://universigats.org/listado",
        "http://adopcioneslamadrilena.org/listado",
        "http://protectoradeayamonte.org/listado",
        "http://adopcionescereco.org/listado",
        "http://rivanimal.org/listado",
        "http://protectoradepalencia.org/listado",
        "http://acogenos.org/listado",
        "http://asociacion-rescat.org/listado",
        "http://masquechuchos.org/listado",
        "http://asociacioneltrasgu.com/listado",
        "http://almeriadefensaanimal.com/listado",
        "http://pro-sabuesos.org/listado",
        "http://chuchos-gr.org/listado",
        "http://protectoramossets.org/listado",
        "http://animalssensesostre.org/listado",
        "http://defensafelina.org/listado",
        "http://asociacionzooland.org/listado",
        "http://terraviva-adopcions.org/listado",
        "http://peludinesalhama.org/listado",
        "http://manopata.org/listado",
        "http://adap-penedes.org/listado",
        "http://feliur.org/listado",
        "http://protectoravilagarcia.org/listado",
        "http://protectoraporlospelos.org/listado",
        "http://asociacionnaturaliahuelva.org",
        "http://gatsdevilafranca.org/listado",
        "http://gatosdeapapa.org/listado",
        "http://olescan.org/listado",
        "http://adoptaunamic.org/listado",
        "http://protectoracabrils.org/listado",
        "http://asociacion-proccan.org/listado",
        "http://protectorabaix.org/listado",
        "http://aspamasqueperros.org/listado",
        "http://badagats.org/listado",
        "http://gatsdelcarrer.org/listado",
        "http://amicsdelsanimalsdelanoguera.org/listado",
        "http://salvanos.es/listado",
        "http://animalessinhogardebaena.org/listado",
        "http://asociacionhada.org.es/listado",
        "http://arcadenoe.org/listado",
        "http://huellaahuella.org/listado",
        "http://heroesde4patas.org/listado",
        "http://darmur.org/listado",
        "http://adoptababycan.org/listado",
        "http://amicsdelsanimals.org",
        "http://ronroneosazules.org/listado",
        "http://zarpasyhuellas.org/listado",
        "http://soscalahonda.org/listado",
        "http://protectoradeanimalesalicante.org/listado",
        "http://gatets.org/listado",
        "http://arda.es/listado",
        "http://spac.es/listado",
        "http://animalrescueemporda.org/listado"
    ]

    BOOLEAN_ATTRIBUTE_TRUE = 'SI'
    BOOLEAN_ATTRIBUTE_FALSE = 'NO'
    ATTRIBUTE_NA = 'NA'

    name = "adopting"
    # start_urls = [
    #     'http://vydanimal.org/listado'
    # ]

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
        health = self.extract_with_css('.ficha_salud::text', pet_container)
        return health

    def extract_description(self, pet_container):
        desc = self.extract_with_css('.ficha_descripcion div::text', pet_container),
        return desc
