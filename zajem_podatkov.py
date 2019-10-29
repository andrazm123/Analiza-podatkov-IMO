import re
import orodja

osnovni_link = "https://www.imo-official.org/"
vzorec_leto = re.compile(
    r'<tr.*?><td><a href="(?P<link1>.*?)amp;(?P<link2>year=\d\d\d\d)">(?P<drzava>.*?)</a></td>',
    flags=re.DOTALL
)

for leto in range(1959, 2020):
    url1 = f'https://www.imo-official.org/year_country_r.aspx?year={leto}'
    ime_datoteke_html1 = f'zajeti_podatki/leto_{leto}/imo-{leto}.html'
    orodja.shrani_spletno_stran(url1, ime_datoteke_html1)

    linki = []
    vsebina = orodja.vsebina_datoteke(f'zajeti_podatki/leto_{leto}/imo-{leto}.html')
    for link in vzorec_leto.finditer(vsebina):
        linki.append({
            "leto": leto,
            "drzava": link.groupdict()["drzava"],
            "link": osnovni_link + link.groupdict()["link1"] + link.groupdict()["link2"]
        })
    # Shranim v json
    ime_datoteke_json = f'zajeti_podatki/leto_{leto}/imo-{leto}.json'
    orodja.zapisi_json(linki, ime_datoteke_json)

    for slovar in linki:
        url2 = slovar["link"]
        ime_datoteke_html2 = f'zajeti_podatki/leto_{leto}/drzave_{leto}/imo-{leto}-{slovar["drzava"]}.html'
        orodja.shrani_spletno_stran(url2, ime_datoteke_html2)



vzorec_1 = re.compile(
    r'<h2><a href=.*?class="highlight">(?P<drzava>.*?)</a> '
    r'<a.*?</h2>\n\n<h3>.*?IMO (?P<leto>\d\d\d\d)</a>',
    flags=re.DOTALL
)

vzorec_bloka = re.compile(
    r'<tr(| class="imp")><td(?P<tekmovalec>.*)</tr>'
)

r'( align="center"|><a href="participant_r.aspx\?id=(\d+)")>((\*|[A-Z].*?))(</a>|)</td><td align="center">((\d|))</td><td align="center">((\d|))</td><td align="center">((\d|))</td><td align="center">((\d|))</td><td align="center">((\d|))</td><td align="center">((\d|))</td><td align="right" class="doubleRightLine">(\d*?)</td><td align="right">\d*?</td><td align="right" class="doubleRightLine">.*?</td><td>(.*?)</td>'


