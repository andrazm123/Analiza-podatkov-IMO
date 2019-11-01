import re
import orodja

zacetek, konec = 1959, 2020

vzorec_leto = re.compile(
    r'<tr.*?><td><a href="(?P<link1>.*?)amp;(?P<link2>year=\d\d\d\d)">(?P<država>.*?)</a></td>',
    flags=re.DOTALL
)

vzorec_leaders = re.compile(
    r'Leader: <b>(?P<leader>.*?)</b><br />(.|\n)*?'
    r'(Deputy leader: <b>(?P<deputy_leader>.*?)</b>|<).*?<',
    flags=re.DOTALL
)

vzorec_bloka = re.compile(
    r'<tr(| class="imp")><td(?P<tekmovalec>.*)</tr>',
    flags=re.DOTALL
)

vzorec_tekmovalca = re.compile(
    r'( align="center"|><a href="participant_r.aspx\?id=(?P<id>\d+)")>'
    r'(?P<ime>(\*|[^0-9\s<].*?))(</a>|)</td><td align="center">'
    r'(?P<p1>(\d|))</td><td align="center">(?P<p2>(\d|))</td><td align="center">'
    r'(?P<p3>(\d|))</td><td align="center">(?P<p4>(\d|))</td><td align="center">'
    r'(?P<p5>(\d|))</td><td align="center">(?P<p6>(\d|))</td><td align="right" '
    r'class="doubleRightLine">(?P<vsota>\d*?)</td><td align="right">\d*?</td>'
    r'<td align="right" class="doubleRightLine">.*?</td><td>(?P<nagrada>.*?)</td>',
    flags=re.DOTALL
)

vzorec_leto_gostiteljica = re.compile(
    r'<tr( class="imp"|)><td align="center"><a href="year_country_r.aspx\?year=\d\d\d\d">(?P<leto>\d\d\d\d)'
    r'</a></td><td><a href="country_team_r.aspx\?code=.*?">(?P<gostiteljica>.*?)</a></td>',
    flags=re.DOTALL
)



def ustvari_slovar_leto_drzava():
    slovar = {}
    
    def leto_drzava_gostiteljica():
        url = "https://www.imo-official.org/results_year.aspx"
        ime_datoteke_html = 'zajeti_podatki/leto_gostiteljica.html'
        orodja.shrani_spletno_stran(url, ime_datoteke_html)
        vsebina = orodja.vsebina_datoteke(ime_datoteke_html)
        for leto_drzava in vzorec_leto_gostiteljica.finditer(vsebina):
            yield leto_drzava.groupdict()
    
    for par in leto_drzava_gostiteljica():
        slovar[int(par["leto"])] = par["gostiteljica"]
    return slovar



def vsa_tekmovanja(začetek, konec):
    osnovni_link = "https://www.imo-official.org/"
    tekmovanja = []
    for leto in range(zacetek, konec):
        tekmovanje_leto = []
        #Za leto 1980 ni podatkov.
        if leto == 1980:
            continue
        url = f'https://www.imo-official.org/year_country_r.aspx?year={leto}'
        ime_datoteke_html = f'zajeti_podatki/leto_{leto}/imo-{leto}.html'
        orodja.shrani_spletno_stran(url, ime_datoteke_html)
        vsebina = orodja.vsebina_datoteke(f'zajeti_podatki/leto_{leto}/imo-{leto}.html')
        
        for link in vzorec_leto.finditer(vsebina):
            tekmovanje_leto.append({
                "leto": leto,
                "država": link.groupdict()["država"],
                "link": osnovni_link + link.groupdict()["link1"] + link.groupdict()["link2"]
            })
        # Shranim v json
        ime_datoteke_json = f'zajeti_podatki/leto_{leto}/imo-{leto}.json'
        orodja.zapisi_json(tekmovanje_leto, ime_datoteke_json)
        tekmovanja.extend(tekmovanje_leto)
    return tekmovanja
        


def vsebina_za_leto(leto, država, link):
    ime_datoteke_html = f'zajeti_podatki/leto_{leto}/drzave_{leto}/imo-{leto}-{država}.html'
    orodja.shrani_spletno_stran(link, ime_datoteke_html)
    vsebina = orodja.vsebina_datoteke(ime_datoteke_html)
    return vsebina



def vrača_tekmovalce(blok):
    
    def izloci_podatke_tekmovalca(tekmovalec):
        if tekmovalec["id"]:
            tekmovalec["id"] = int(tekmovalec["id"])
        else:
            tekmovalec["id"] = None
        if tekmovalec["ime"] == "*":
            tekmovalec["ime"] = "?"
        if tekmovalec["p1"]:
            tekmovalec["p1"] =  int(tekmovalec["p1"])
        else:
            tekmovalec["p1"] =  "unknown"
        if tekmovalec["p2"]:
            tekmovalec["p2"] =  int(tekmovalec["p2"])
        else:
            tekmovalec["p2"] =  "unknown"
        if tekmovalec["p3"]:
            tekmovalec["p3"] =  int(tekmovalec["p3"])
        else:
            tekmovalec["p3"] =  "unknown"
        if tekmovalec["p4"]:
            tekmovalec["p4"] =  int(tekmovalec["p4"])
        else:
            tekmovalec["p4"] =  "unknown"
        if tekmovalec["p5"]:
            tekmovalec["p5"] =  int(tekmovalec["p5"])
        else:
            tekmovalec["p5"] =  "unknown"
        if tekmovalec["p6"]:
            tekmovalec["p6"] =  int(tekmovalec["p6"])
        else:
            tekmovalec["p6"] =  "unknown"
            tekmovalec["vsota"] =  int(tekmovalec["vsota"])
        if tekmovalec["nagrada"] == "":
            tekmovalec["nagrada"] = None
        return tekmovalec

    for tekmovalec in vzorec_tekmovalca.finditer(blok):
        yield izloci_podatke_tekmovalca(tekmovalec.groupdict())



def izloci_gnezdene_podatke(seznam):
    seznam_tekmovalcev = []
    seznam_tekmovanj = []
    for element in seznam:
        for tekmova in element["tekmovalci"]:
            seznam_tekmovalcev.append({
                "leto": element["leto"],
                "država": element["država"],
                "id": tekmova["id"],
                "ime": tekmova["ime"],
                "p1": tekmova["p1"],
                "p2": tekmova["p2"],
                "p3": tekmova["p3"],
                "p4": tekmova["p4"],
                "p5": tekmova["p5"],
                "p6": tekmova["p6"],
                "vsota": tekmova["vsota"],
                "nagrada": tekmova["nagrada"]
            })
        seznam_tekmovanj.append({
            "leto": element["leto"],
            "država": element["država"],
            "gostiteljica": element["gostiteljica"],
            "leader": element["leader"],
            "deputy leader": element["deputy leader"]
        })
    return seznam_tekmovalcev, seznam_tekmovanj




seznam_vsega = []
leto_gostiteljica = ustvari_slovar_leto_drzava()
for tekmovanje in vsa_tekmovanja(zacetek, konec):
    leto = tekmovanje["leto"]
    država = tekmovanje["država"]
    link = tekmovanje["link"]
    gostiteljica = leto_gostiteljica[leto]
    vsebina = vsebina_za_leto(leto, država, link)
    poisci_leaderje = vzorec_leaders.search(vsebina)
    if poisci_leaderje is None:
        leaders = {}
        leaders["deputy_leader"] = None
        leaders["leader"] = None
    else:
        leaders = poisci_leaderje.groupdict()
    poisci_blok = vzorec_bloka.search(vsebina)
    if poisci_blok is None:
        blok = ""
    else:
        blok = poisci_blok.group()
    tekmovalci = []
    for tekmovalec in vrača_tekmovalce(blok):
        tekmovalci.append(tekmovalec)
    seznam_vsega.append({
        "leto": leto,
        "gostiteljica": gostiteljica,
        "država": država,
        "leader": leaders["leader"],
        "deputy leader": leaders["deputy_leader"],
        "tekmovalci": tekmovalci
    })
    
# Shranim v json
ime_datoteke_json = 'obdelani_podatki/vsi_podatki.json'
orodja.zapisi_json(seznam_vsega, ime_datoteke_json)

# Shranim v csv
seznam_tekmovalcev, seznam_tekmovanj = izloci_gnezdene_podatke(seznam_vsega)
glava_tekmovanj = ["leto", "gostiteljica", "država", "leader", "deputy leader"]
glava_tekmovalcev = ["leto", "država", "id", "ime", "p1", "p2", "p3", "p4", "p5", "p6", "vsota", "nagrada"]
orodja.zapisi_csv(seznam_tekmovanj, glava_tekmovanj, "obdelani_podatki/tekmovanja.csv")
orodja.zapisi_csv(seznam_tekmovalcev, glava_tekmovalcev, "obdelani_podatki/tekmovalci.csv")