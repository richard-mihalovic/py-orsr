from lxml import etree
import requests

__version__ = '1.0'
__author__ = 'Richard Mihalovic'
__contact__ = 'richard@mihalovic.sk'
__licence__ = 'MIT'


class OrSr:
    def __load_html(self, url):
        r = requests.get(url)
        r.encoding = 'windows-1250'
        html = r.text
        r.connection.close()  # fix: ResourceWarning: unclosed

        return html

    def hladaj_podla_ico(self, ico):
        url = 'http://orsr.sk/hladaj_ico.asp?SID=0&ICO=' + ico.replace(' ', '')
        html = self.__load_html(url)

        root = etree.fromstring(html, etree.HTMLParser())
        elements = root.xpath('//div[@class="bmk"][1]/a/@href')
        if len(elements) == 2:
            detail_url = 'http://orsr.sk/' + elements[0]
            detail_html = self.__load_html(detail_url)
            return OrSrDetailParser().parse(detail_html)
        else:
            return None

    def hladaj_podla_nazvu(self, nazov):
        url = 'http://orsr.sk/hladaj_subjekt.asp?PF=0&SID=0&R=on&OBMENO=' + nazov
        html = self.__load_html(url)

        root = etree.fromstring(html, etree.HTMLParser())
        elements = root.xpath('//div[@class="bmk"][1]/a/@href')
        if len(elements) == 2:
            detail_url = 'http://orsr.sk/' + elements[0]
            detail_html = self.__load_html(detail_url)
            return OrSrDetailParser().parse(detail_html)
        else:
            return None


class OrSrDetailParser(object):
    def __init__(self):
        self.__detail = {
            'nazov': '',
            'sidlo': '',
            'ico': '',
            'den_zapisu': '',
            'pravna_forma': '',
            'predmet_cinnosti': [],
            'spolocnici': [],
            'statutarny_organ': [],
            'dozorna_rada': ''
        }

    def parse(self, html):
        parser = etree.HTMLParser()
        root = etree.fromstring(html, parser)
        tables = root.xpath('/html/body/table')

        tmp_name = ''
        for table in tables:
            typ = self.__zisti_typ_zaznamu(table).lower().replace(':', '')

            if typ == 'obchodné meno' or typ == 'obchodné meno organizačnej zložky':
                self.__nacitaj_nazov_spolocnosti(table)
            elif typ == 'sídlo' or typ == 'sídlo organizačnej zložky' or typ == "miesto podnikania":
                self.__nacitaj_sidlo_spolocnosti(table)
            elif typ == 'ičo':
                self.__nacitaj_ico(table)
            elif typ == 'deň zápisu':
                self.__nacitaj_den_zapisu(table)
            elif typ == 'právna forma':
                self.__nacitaj_pravnu_formu(table)
            elif typ == 'predmet činnosti':
                self.__nacitaj_predmet_cinnosti(table)
            elif typ == 'spoločníci':
                self.__nacitaj_spolocnikov(table)
            elif typ == 'výška vkladu každého spoločníka':
                self.__nacitaj_vklady(table)
            elif typ == 'štatutárny orgán':
                self.__nacitaj_statutarny_organ(table)
            elif typ == 'dozorná rada':
                self.__nacitaj_dozornu_radu(table)
            elif typ == 'údaje o podnikateľovi' or typ == 'bydlisko':
                tmp_name += self.__process_udaje_o_podnikatelovi(table, typ)

        if tmp_name != '':
            self.__detail['spolocnici'].append(tmp_name.strip())
            self.__detail['statutarny_organ'].append(tmp_name.strip())

        return self.__detail

    def __zisti_typ_zaznamu(self, table):
        record_type = table.xpath('tr/td[1]/span/text()')
        record_type = ' '.join(record_type)
        record_type = record_type.strip().replace(':', '')
        return record_type

    def __nacitaj_nazov_spolocnosti(self, table):  # nazov
        elements = table.xpath('tr/td[2]/table/tr/td[1]/span[1]/text()')
        self.__detail['nazov'] = ''.join(elements).strip()

    def __nacitaj_sidlo_spolocnosti(self, table):  # sidlo
        spans = table.xpath('tr/td[2]//span')

        address = ''
        if len(spans) >= 4:
            address = spans[0].text.strip() + ' ' + spans[1].text.strip() + ', '
            address += spans[2].text.strip() + ', '
            address += spans[3].text.strip()

            pos = address.find(', (od:')
            if pos != -1:
                address = address[0:pos]
        else:
            # TODO
            #address = tds[0].get_text()
            pass

        self.__detail['sidlo'] = address.strip()

    def __nacitaj_ico(self, table):  # ico
        ico = ''.join(table.xpath('tr/td[2]/table/tr/td[1]/span[1]/text()')).strip()
        self.__detail['ico'] = ico

    def __nacitaj_den_zapisu(self, table):  # den zapisu
        den_zapisu = ''.join(table.xpath('tr/td[2]/table/tr/td[1]/span[1]/text()')).strip()
        self.__detail['den_zapisu'] = den_zapisu

    def __nacitaj_pravnu_formu(self, table):  # pravna forma
        pravna_forma = ''.join(table.xpath('tr/td[2]/table/tr/td[1]/span[1]/text()')).strip()
        self.__detail['pravna_forma'] = pravna_forma

    def __nacitaj_predmet_cinnosti(self, table):  # predmet cinnosti
        elements = (table.xpath('tr/td[2]/table/tr/td[1]/span[1]'))
        self.__detail['predmet_cinnosti'] = [e.text.strip() for e in elements]

    def __nacitaj_spolocnikov(self, table):  # spolocnici
        spolocnici = []

        tds = table.xpath('tr/td[2]/table/tr/td[1]')
        for td in tds:
            elements = td.xpath('child::span | child::br | child::a/span')

            br = 0
            meno = ''
            adresa_l = []
            for e in elements:
                if e.tag == 'br':
                    br += 1

                if 'span' and br == 0:
                    meno += e.text.strip() + ' '
                elif e.tag == 'span' and br > 0:
                    adresa_l.append(e.text.strip())

            adresa = ''
            if br == 3:
                if len(adresa_l) == 3:
                    adresa = adresa_l[0] + ' ' + adresa_l[1] + ', ' + adresa_l[2]
                elif len(adresa_l) == 4:
                    adresa = adresa_l[0] + ' ' + adresa_l[1] + ', ' + ', '.join(adresa_l[2:])

                spolocnici.append(meno + '( ' + adresa + ' )')
            elif br > 3:
                adresa = adresa_l[0] + ' ' + adresa_l[1] + ', ' + ', '.join(adresa_l[2:])
                spolocnici.append(meno + '( ' + adresa + ' )')

        self.__detail['spolocnici'] = spolocnici

    def __nacitaj_vklady(self, table):  # vklady
        vklady = []
        self.__detail['vklady'] = vklady

    def __nacitaj_statutarny_organ(self, table):  # statutarny organ
        statutarny_organ = []

        elements = table.xpath('tr/td[2]/table/tr/td[1]//span | tr/td[2]/table/tr/td[1]//br')

        statutarny_organ.append(elements.pop(0).text.strip())

        br_counter = 0
        meno_tmp = []
        adresa_tmp = []
        for e in elements:
            if e.tag == 'br':
                br_counter += 1
            else:
                text = e.text.strip()

                if 'Vznik funkcie' in text:
                    adresa = ' '.join(adresa_tmp[:2]) + ', '
                    adresa += ', '.join(adresa_tmp[2:])
                    item = ' '.join(meno_tmp) + ' ( ' + adresa + ' )'
                    statutarny_organ.append(item)

                    br_counter = 0
                    meno_tmp = []
                    adresa_tmp = []
                elif br_counter == 1:
                    meno_tmp.append(e.text.strip())
                elif 'pobyt na území SR' not in text:
                    adresa_tmp.append(e.text.strip())

        self.__detail['statutarny_organ'] = statutarny_organ

    def __nacitaj_dozornu_radu(self, table):
        dozorna_rada = []

        elements = table.xpath('tr/td[2]/table/tr/td[1]//span | tr/td[2]/table/tr/td[1]//br')
        br = 0
        meno = ''
        adresa_l = []
        process_record = False
        for e in elements:
            if e.tag == 'br':
                br += 1

            if e.tag == 'span' and 'Vznik funkcie' in e.text:
                process_record = True
            elif process_record and br == 1:
                br = 0
                process_record = False
            elif e.tag == 'span' and br == 0:
                meno += e.text.strip() + ' '
            elif e.tag == 'span' and br > 0:
                text = e.text.strip()
                if 'pobyt na území SR' not in text and 'Vznik funkcie' not in text:
                    adresa_l.append(text)

            adresa = ''
            if process_record:
                if len(adresa_l) == 3:
                    adresa = adresa_l[0] + ' ' + adresa_l[1] + ', ' + adresa_l[2]
                elif len(adresa_l) == 4:
                    adresa = adresa_l[0] + ' ' + adresa_l[1] + ', ' + ', '.join(adresa_l[2:])
                else:
                    adresa = ', '.join(adresa_l)

                dozorna_rada.append(meno + '( ' + adresa + ' )')

                br = 0
                meno = ''
                adresa_l = []

        self.__detail['dozorna_rada'] = dozorna_rada

    def __process_udaje_o_podnikatelovi(self, table, which):
        l = []
        elements = table.xpath('tr/td[2]/table/tr/td[1]/span/text()')
        for e in elements:
            if 'od:' not in e:
                l.append(e.strip())

        if which == 'bydlisko':
            txt = '( ' + ' '.join(l) + ' )'
        else:
            txt = ' '.join(l) + ' '

        return txt
