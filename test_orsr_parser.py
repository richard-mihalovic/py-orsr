import orsr

import requests
import unittest


class OrsrParserTest(unittest.TestCase):
    def __load_html_page(self, url):
        r = requests.get(url)
        r.encoding = 'windows-1250'
        html = r.text
        r.connection.close()  # fix: ResourceWarning: unclosed

        return html

    def test_hladaj_podla_ico(self):
        detail = orsr.OrSr().hladaj_podla_ico('45 947 597')
        self.assertIsNotNone(detail)
        self.assertEqual(detail['ico'], '45 947 597')
        self.assertEqual(detail['nazov'], 'Google Slovakia, s. r. o.')

    def test_hladaj_podla_nazvu(self):
        detail = orsr.OrSr().hladaj_podla_nazvu('ESET, spol. s r.o.')
        self.assertIsNotNone(detail)
        self.assertEqual(detail['ico'], '31 333 532')
        self.assertEqual(detail['nazov'], 'ESET, spol. s r.o.')

    def test_parse_energix(self):
        html = self.__load_html_page('http://orsr.sk/vypis.asp?ID=232303&SID=2&P=0')
        self.assertIsNotNone(html)

        detail = orsr.OrSrDetailParser().parse(html)
        self.assertEqual(detail['nazov'], 'ENERGIX, s. r. o.')
        self.assertEqual(detail['ico'], '46 613 790')
        self.assertEqual(detail['pravna_forma'], 'Spoločnosť s ručením obmedzeným')
        self.assertEqual(detail['sidlo'], 'Inovecká 2143/5, Senec, 903 01')
        self.assertIn('konateľ', detail['statutarny_organ'])
        self.assertEqual(detail['den_zapisu'], '04.04.2012')
        self.assertEqual(len(detail['predmet_cinnosti']), 9)

    def test_parse_posam(self):
        html = self.__load_html_page('http://orsr.sk/vypis.asp?ID=8585&SID=2&P=0')
        self.assertIsNotNone(html)

        detail = orsr.OrSrDetailParser().parse(html)
        self.assertEqual(detail['nazov'], 'PosAm, spol. s r.o.')
        self.assertEqual(detail['ico'], '31 365 078')
        self.assertEqual(detail['pravna_forma'], 'Spoločnosť s ručením obmedzeným')
        self.assertEqual(detail['sidlo'], 'Bajkalská 28, Bratislava, 821 09')
        self.assertEqual(len(detail['spolocnici']), 10)
        self.assertIn('konatelia', detail['statutarny_organ'])
        self.assertEqual(len(detail['statutarny_organ']), 4)
        self.assertEqual(detail['den_zapisu'], '03.01.1994')
        self.assertEqual(len(detail['predmet_cinnosti']), 20)

    def test_parse_microsoft(self):  # test s.r.o.
        html = self.__load_html_page('http://orsr.sk/vypis.asp?ID=11422&SID=2&P=0')
        self.assertIsNotNone(html)

        detail = orsr.OrSrDetailParser().parse(html)
        self.assertEqual(detail['nazov'], 'Microsoft Slovakia s.r.o.')
        self.assertEqual(detail['ico'], '31 398 871')
        self.assertEqual(detail['pravna_forma'], 'Spoločnosť s ručením obmedzeným')
        self.assertEqual(detail['sidlo'], 'Prievozská 4D, Bratislava, 821 09')
        self.assertEqual(len(detail['spolocnici']), 1)
        self.assertIn('konateľ', detail['statutarny_organ'])
        self.assertEqual(len(detail['statutarny_organ']), 2)
        self.assertEqual(detail['den_zapisu'], '21.07.1995')
        self.assertEqual(len(detail['predmet_cinnosti']), 12)

    def test_parse_datalan(self):  # test a.s.
        html = self.__load_html_page('http://orsr.sk/vypis.asp?ID=31720&SID=2&P=0')
        self.assertIsNotNone(html)

        detail = orsr.OrSrDetailParser().parse(html)
        self.assertEqual(detail['nazov'], 'DATALAN, a.s.')
        self.assertEqual(detail['sidlo'], 'Galvaniho 17/A, Bratislava, 821 04')
        self.assertEqual(detail['ico'], '35 810 734')
        self.assertEqual(detail['den_zapisu'], '01.05.2001')
        self.assertEqual(detail['pravna_forma'], 'Akciová spoločnosť')
        self.assertEqual(len(detail['predmet_cinnosti']), 18)

        self.assertIn('predstavenstvo', detail['statutarny_organ'])