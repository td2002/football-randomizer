from dataclasses import dataclass, field
from typing import Optional, Union
import re
from typing import Optional, Union
from xml.etree import ElementTree
import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from lxml import etree
from requests import Response, TooManyRedirects


class Players:
    class Profile:
        ID: str = "//div[@data-action='profil']//@data-id"
        URL: str = "//a[@class='tm-subnav-item megamenu']//@href"
        NAME: str = "//h1[@class='data-header__headline-wrapper']//strong//text()"
        IMAGE_URL: str = "//div[@id='fotoauswahlOeffnen']//img//@src"
        SHIRT_NUMBER: str = "//span[@class='data-header__shirt-number']//text()"
        CURRENT_CLUB_NAME: str = "//span[@class='data-header__club']//text()"
        CURRENT_CLUB_URL: str = "//span[@class='data-header__club']//a//@href"
        CURRENT_CLUB_JOINED: str = "//span[text()='Joined: ']//span//text()"
        LAST_CLUB_NAME: str = "//span[contains(text(),'Last club:')]//span//a//@title"
        LAST_CLUB_URL: str = "//span[contains(text(),'Last club:')]//span//a//@href"
        MOST_GAMES_FOR_CLUB_NAME: str = "//span[contains(text(),'Most games for:')]//span//a//text()"
        RETIRED_SINCE_DATE: str = "//span[contains(text(),'Retired since:')]//span//text()"
        CURRENT_CLUB_CONTRACT_EXPIRES: str = "//span[text()='Contract expires: ']//span//text()"
        CURRENT_CLUB_CONTRACT_OPTION: str = "//span[contains(text(),'Contract option:')]//following::span[1]//text()"
        NAME_IN_HOME_COUNTRY: str = "//span[text()='Name in home country:']//following::span[1]//text()"
        FULL_NAME: str = "//span[text()='Full name:']//following::span[1]//text()"
        DATE_OF_BIRTH: str = "//span[text()='Date of birth:']//following::span[1]//a//text()"
        PLACE_OF_BIRTH_CITY: str = "//span[text()='Place of birth:']//following::span[1]//span//text()"
        PLACE_OF_BIRTH_COUNTRY: str = "//span[text()='Place of birth:']//following::span[1]//span//img//@title"
        AGE: str = "//span[text()='Age:']//following::span[1]//text()"
        HEIGHT: str = "//span[text()='Height:']//following::span[1]//text()"
        CITIZENSHIP: str = "//span[text()='Citizenship:']//following::span[1]//text()"
        POSITION: str = "//span[text()='Position:']//following::span[1]//text()"
        POSITION_MAIN: str = "//dt[contains(text(),'Main position:')]//following::dd[1]//text()"
        POSITION_OTHER: str = "//dt[contains(text(),'Other position:')]//following::dd//text()"
        FOOT: str = "//span[text()='Foot:']//following::span[1]//text()"
        MARKET_VALUE_CURRENT: str = "//div[@class='tm-player-market-value-development__current-value']//text()"
        MARKET_VALUE_HIGHEST: str = "//div[@class='tm-player-market-value-development__max-value']//text()"
        AGENT_NAME: str = "//span[text()='Player agent:']//following::span[1]//a//text()"
        AGENT_URL: str = "//span[text()='Player agent:']//following::span[1]//a//@href"
        OUTFITTER: str = "//span[contains(text(),'Outfitter:')]//following::span[1]//text()"
        SOCIAL_MEDIA: str = "//div[@class='socialmedia-icons']//@href"

    class Search:
        RESULT: str = "//div[h2[contains(text(), 'players')]]"
        RESULT_NATIONALITIES: str = ".//td[img[@class='flaggenrahmen']]"
        RESULT_CLUBS: str = ".//td[@class='zentriert'][2]"
        NAMES: str = ".//td[@class='hauptlink']//a//@title"
        URLS: str = ".//td[@class='hauptlink']//a//@href"
        AGES: str = ".//td[@class='zentriert'][3]//text()"
        POSITIONS: str = ".//td[@class='zentriert'][1]//text()"
        CLUBS_URLS: str = ".//a//@href"
        CLUBS_NAMES: str = ".//img[@class='tiny_wappen']//@title"
        MARKET_VALUES: str = ".//td[@class='rechts hauptlink']//text()"
        NATIONALITIES: str = ".//img//@title"
        PAGE_NUMBER_LAST: str = (
            ".//li[@class='tm-pagination__list-item tm-pagination__list-item--icon-last-page']//@href"
        )
        PAGE_NUMBER_ACTIVE: str = ".//li[@class='tm-pagination__list-item tm-pagination__list-item--active']//@href"

    class MarketValue:
        URL: str = "//a[@class='data-header__market-value-wrapper']//@href"
        CURRENT: str = (
            "//a[@class='data-header__market-value-wrapper']//text()[not(parent::p/@class='data-header__last-update')]"
        )
        UPDATED: str = "//a[@class='data-header__market-value-wrapper']//p//text()"
        RANKINGS_NAMES: str = "//h3[@class='quick-fact__headline']//text()"
        RANKINGS_POSITIONS: str = "//span[contains(@class, 'quick-fact__content--large')]//text()"

    class Transfers:
        PLAYER_URL: str = "//li[@id='transfers']//a//@href"
        TRANSFERS_URLS: str = "//a[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__link']//@href"
        SEASONS: str = "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__season']//text()"
        DATES: str = "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__date']//text()"
        CLUBS_NAMES: str = "//*[@class='tm-player-transfer-history-grid__club-link']//text()"
        FEES: str = "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__fee']//text()"
        YOUTH_CLUBS: str = "//div[@data-viewport='Jugendvereine']//div//text()"
        FROM_CLUBS_URLS: str = (
            "//*[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__old-club']//a[1]//@href"
        )
        TO_CLUBS_URLS: str = (
            "//*[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__new-club']//a[1]//@href"
        )
        MARKET_VALUES: str = (
            "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__market-value']//text()"
        )

    class Stats:
        PLAYER_STATS: str = "//table[@class='items']//tbody//td"
        COMPETITIONS_IDS: str = ".//a//@href"
        COMPETITIONS_NAMES: str = ".//a//text()"
        CLUBS_IDS: str = ".//a/@href"
        CLUBS_NAMES: str = ".//a//@title"
        APPEARANCES: str = ".//a//text()"
        GOALKEEPER: str = "//li[contains(text(), 'Position:')]//span//text()"

class Clubs:
    class Profile:
        URL: str = "//div[@class='datenfakten-wappen']//@href"
        NAME: str = "//header//h1//text()"
        NAME_OFFICIAL: str = "//th[text()='Official club name:']//following::td[1]//text()"
        IMAGE: str = "//div[@class='datenfakten-wappen']//@src"
        LEGAL_FORM: str = "//th[text()='Legal form:']//following::td[1]//text()"
        ADDRESS_LINE_1: str = "//th[text()='Address:']//following::td[1]//text()"
        ADDRESS_LINE_2: str = "//th[text()='Address:']//following::td[2]//text()"
        ADDRESS_LINE_3: str = "//th[text()='Address:']//following::td[3]//text()"
        TEL: str = "//th[text()='Tel:']//following::td[1]//text()"
        FAX: str = "//th[text()='Fax:']//following::td[1]//text()"
        WEBSITE: str = "//th[text()='Website:']//following::td[1]//text()"
        FOUNDED_ON: str = "//th[text()='Founded:']//following::td[1]//text()"
        MEMBERS: str = "//th[text()='Members:']//following::td[1]//text()"
        MEMBERS_DATE: str = "//th[text()='Members:']//following::td[1]//text()"
        OTHER_SPORTS: str = "//th[text()='Other sports:']//following::td[1]//text()"
        COLORS: str = "//p[@class='vereinsfarbe']//@style"
        STADIUM_NAME: str = "//li[contains(text(), 'Stadium:')]//span//a//text()"
        STADIUM_SEATS: str = "//li[contains(text(), 'Stadium:')]//span//span//text()"
        TRANSFER_RECORD: str = "//li[contains(text(), 'Current transfer record:')]//a//text()"
        MARKET_VALUE: str = "//a[@class='data-header__market-value-wrapper']//text()"
        CONFEDERATION: str = "//li[contains(text(), 'Konföderation:')]//span//text()"
        RANKING: str = "//li[contains(text(), 'FIFA World Ranking:')]//span//a//text()"
        SQUAD_SIZE: str = "//li[contains(text(), 'Squad size:')]//span//text()"
        SQUAD_AVG_AGE: str = "//li[contains(text(), 'Average age:')]//span//text()"
        SQUAD_FOREIGNERS: str = "//li[contains(text(), 'Foreigners:')]//span[1]//a//text()"
        SQUAD_NATIONAL_PLAYERS: str = "//li[contains(text(), 'National team players:')]//span//a//text()"
        LEAGUE_ID: str = "//span[@itemprop='affiliation']//a//@href"
        LEAGUE_NAME: str = "//span[@itemprop='affiliation']//a//text()"
        LEAGUE_COUNTRY_ID: str = (
            "//div[@class='data-header__club-info']//img[contains(@class, 'flaggenrahmen')]//@data-src"
        )
        LEAGUE_COUNTRY_NAME: str = (
            "//div[@class='data-header__club-info']//img[contains(@class, 'flaggenrahmen')]//@title"
        )
        LEAGUE_TIER: str = "//div[@class='data-header__club-info']//strong//text()//following::span[1]/a/text()[2]"
        CRESTS_HISTORICAL: str = "//div[@class='wappen-datenfakten-wappen']//@src"

    class Search:
        RESULT: str = "//div[h2[contains(text(), 'Clubs')]]"
        NAMES: str = ".//td[@class='hauptlink']//a//@title"
        URLS: str = ".//td[@class='hauptlink']//a//@href"
        COUNTRIES: str = ".//td[@class='zentriert']//img[@class='flaggenrahmen']//@title"
        MARKET_VALUES: str = ".//td[@class='rechts']//text()"
        SQUADS: str = ".//td[@class='zentriert']//text()"
        PAGE_NUMBER_LAST: str = (
            ".//li[@class='tm-pagination__list-item tm-pagination__list-item--icon-last-page']//@href"
        )
        PAGE_NUMBER_ACTIVE: str = ".//li[@class='tm-pagination__list-item tm-pagination__list-item--active']//@href"

    class Players:
        PAST_FLAG: str = "//div[@id='yw1']//thead//text()"
        CLUB_NAME: str = "//header//h1//text()"
        CLUB_URL: str = "//li[@id='overview']//@href"
        PAGE_NATIONALITIES: str = "//td[img[@class='flaggenrahmen']]"
        PAGE_INFOS: str = "//td[@class='posrela']"
        NAMES: str = "//td[@class='posrela']//a//text()"
        URLS: str = "//td[@class='hauptlink']//@href"
        POSITIONS: str = "//td[@class='posrela']//tr[2]//text()"
        DOB_AGE: str = "//div[@id='yw1']//td[3]//text()"
        NATIONALITIES: str = ".//img//@title"
        JOINED: str = ".//span/node()/@title"
        SIGNED_FROM: str = ".//a//img//@title"
        MARKET_VALUES: str = "//td[@class='rechts hauptlink']//text()"
        STATUSES: str = ".//td[@class='hauptlink']//span//@title"

        class Present:
            PAGE_SIGNED_FROM: str = "//div[@id='yw1']//td[8]"
            HEIGHTS: str = "//div[@id='yw1']//td[5]//text()"
            FOOTS: str = "//div[@id='yw1']//td[6]//text()"
            JOINED_ON: str = "//div[@id='yw1']//td[7]//text()"
            CONTRACTS: str = "//div[@id='yw1']//td[9]//text()"

        class Past:
            PAGE_SIGNED_FROM: str = "//div[@id='yw1']//td[9]"
            CURRENT_CLUB = "//div[@id='yw1']//td[5]//img//@title"
            HEIGHTS: str = "//div[@id='yw1']//td[6]/text()"
            FOOTS: str = "//div[@id='yw1']//td[7]//text()"
            JOINED_ON: str = "//div[@id='yw1']//td[8]//text()"
            CONTRACTS: str = "//div[@id='yw1']//td[10]//text()"

class Competitions:
    class Profile:
        URL: str = "//li[@id='overview']//@href"
        NAME: str = "//div[@class='data-header__headline-container']//h1//text()"

    class Search:
        RESULT: str = "//div[h2[contains(text(), 'competitions')]]"
        RESULT_COUNTRIES: str = ".//td[@class='zentriert'][1]"
        RESULT_CLUBS: str = ".//td[@class='zentriert'][2]"
        RESULT_PLAYERS: str = ".//td[@class='rechts']"
        RESULT_MARKETVALUES: str = ".//td[@class='zentriert'][3]"
        RESULT_CONTINENTS: str = ".//td[@class='zentriert'][5]"
        NAMES: str = ".//td//a//@title"
        URLS: str = ".//td//a//@href"
        COUNTRIES: str = ".//@title"
        CLUBS: str = ".//text()"
        PLAYERS: str = ".//text()"
        MARKETVALUES: str = ".//text()"
        CONTINENTS: str = ".//text()"
        PAGE_NUMBER_LAST: str = (
            ".//li[@class='tm-pagination__list-item tm-pagination__list-item--icon-last-page']//@href"
        )
        PAGE_NUMBER_ACTIVE: str = ".//li[@class='tm-pagination__list-item tm-pagination__list-item--active']//@href"

    class Clubs:
        URLS: str = "//td[@class='hauptlink no-border-links']//a[1]//@href"
        NAMES: str = "//td[@class='hauptlink no-border-links']//a//text()"



def get_text_by_xpath(
    self,
    xpath: str,
    pos: int = 0,
    iloc: Optional[int] = None,
    iloc_from: Optional[int] = None,
    iloc_to: Optional[int] = None,
    join_str: Optional[str] = None,
) -> Optional[str]:
    try:
        element = self.page.xpath(xpath)
    except AttributeError:
        element = self.xpath(xpath)

    if not element:
        return None

    if isinstance(element, list):
        element = [trim(e) for e in element if trim(e)]

    if isinstance(iloc, int):
        element = element[iloc]

    if isinstance(iloc_from, int) and isinstance(iloc_to, int):
        element = element[iloc_from:iloc_to]

    if isinstance(iloc_to, int):
        element = element[:iloc_to]

    if isinstance(iloc_from, int):
        element = element[iloc_from:]

    if isinstance(join_str, str):
        return join_str.join([trim(e) for e in element])

    try:
        return trim(element[pos])
    except IndexError:
        return None
    
def trim(text: Union[list, str]) -> str:
    if isinstance(text, list):
        text = "".join(text)

    return text.strip().replace("\xa0", "")
    
def safe_split(text: Optional[str], delimiter: str) -> Optional[list]:
    if not isinstance(text, str):
        return None

    return [trim(t) for t in text.split(delimiter)]

def remove_str(text: Optional[str], strings_to_remove: Union[str, list]) -> Optional[str]:
    if not isinstance(text, str):
        return None
    strings_to_remove = list(strings_to_remove)

    for string in strings_to_remove:
        text = text.replace(string, "")

    return trim(text)

def get_list_by_xpath(self, xpath: str, remove_empty: Optional[bool] = True) -> Optional[list]:
    elements: list = self.page.xpath(xpath)
    if remove_empty:
        elements_valid: list = [trim(e) for e in elements if trim(e)]
    else:
        elements_valid: list = [trim(e) for e in elements]
    return elements_valid or []

def extract_from_url(tfmkt_url: str, element: str = "id") -> Optional[str]:
    regex: str = (
        r"/(?P<code>[\w-]+)"
        r"/(?P<category>[\w-]+)"
        r"/(?P<type>[\w-]+)"
        r"/(?P<id>\w+)"
        r"(/saison_id/(?P<season_id>\d{4}))?"
        r"(/transfer_id/(?P<transfer_id>\d+))?"
    )
    try:
        groups: dict = re.match(regex, tfmkt_url).groupdict()
    except TypeError:
        return None
    return groups.get(element)

def safe_regex(text: Optional[str], regex, group: str) -> Optional[str]:
    if not isinstance(text, str):
        return None

    try:
        groups = re.search(regex, text).groupdict()
        return groups.get(group)
    except AttributeError:
        return None

def clean_response(nested: Union[dict, list]) -> Union[dict, list]:
    if isinstance(nested, dict):
        return {k: v for k, v in ((k, clean_response(v)) for k, v in nested.items()) if v or isinstance(v, bool)}
    if isinstance(nested, list):
        return [v for v in map(clean_response, nested) if v or isinstance(v, bool)]
    return nested

def request_url_page(url: str) -> ElementTree:
    bsoup: BeautifulSoup = request_url_bsoup(url=url)
    return convert_bsoup_to_page(bsoup=bsoup)

def request_url_bsoup(url: str) -> BeautifulSoup:
    response: Response = make_request(url=url)
    return BeautifulSoup(markup=response.content, features="html.parser")

def convert_bsoup_to_page(bsoup: BeautifulSoup) -> ElementTree:
    return etree.HTML(str(bsoup))

def make_request(url: str) -> Response:
    try:
        response: Response = requests.get(
            url=url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/113.0.0.0 "
                    "Safari/537.36"
                ),
            },
        )
    except TooManyRedirects:
        raise HTTPException(status_code=404, detail=f"Not found for url: {url}")
    if 400 <= response.status_code < 500:
        raise HTTPException(status_code=response.status_code, detail=f"Client Error. {response.reason} for url: {url}")
    elif 500 <= response.status_code < 600:
        raise HTTPException(status_code=response.status_code, detail=f"Server Error. {response.reason} for url: {url}")
    return response

@dataclass
class Profile:
    club_id: str
    club_profile: dict = field(default_factory=lambda: {})

    def get_club_profile(self):
        self._request_page()

        self.club_profile["id"] = self.club_id
        self.club_profile["url"] = get_text_by_xpath(self, Clubs.Profile.URL)
        self._check_club_found()
        self.club_profile["name"] = get_text_by_xpath(self, Clubs.Profile.NAME)
        # "//header//h1//text()"
        # //*[@id="main"]/header/div[2]/tm-quick-select-bar//div/tm-quick-select[1]/div/div/strong
        # /html/head/meta[3]
        tmp_country_strings = str.split(get_text_by_xpath(self, "//html//head//meta[3]//@content"), ",")
        self.club_profile["customCountry"] = tmp_country_strings[-1]
        #print("ecco: ", self.club_profile["customCountry"])
        self.club_profile["officialName"] = get_text_by_xpath(self, Clubs.Profile.NAME_OFFICIAL)
        self.club_profile["image"] = safe_split(get_text_by_xpath(self, Clubs.Profile.IMAGE), "?")[0]
        self.club_profile["legalForm"] = get_text_by_xpath(self, Clubs.Profile.LEGAL_FORM)
        self.club_profile["addressLine1"] = get_text_by_xpath(self, Clubs.Profile.ADDRESS_LINE_1)
        self.club_profile["addressLine2"] = get_text_by_xpath(self, Clubs.Profile.ADDRESS_LINE_2)
        self.club_profile["addressLine3"] = get_text_by_xpath(self, Clubs.Profile.ADDRESS_LINE_3)
        self.club_profile["tel"] = get_text_by_xpath(self, Clubs.Profile.TEL)
        self.club_profile["fax"] = get_text_by_xpath(self, Clubs.Profile.FAX)
        self.club_profile["website"] = get_text_by_xpath(self, Clubs.Profile.WEBSITE)
        self.club_profile["foundedOn"] = get_text_by_xpath(self, Clubs.Profile.FOUNDED_ON)
        self.club_profile["members"] = get_text_by_xpath(self, Clubs.Profile.MEMBERS)
        self.club_profile["membersDate"] = remove_str(
            get_text_by_xpath(self, Clubs.Profile.MEMBERS_DATE, pos=1),
            ["(", "Score", ":", ")"],
        )
        self.club_profile["otherSports"] = safe_split(get_text_by_xpath(self, Clubs.Profile.OTHER_SPORTS), ",")
        self.club_profile["colors"] = [
            remove_str(e, ["background-color:", ";"]) for e in get_list_by_xpath(self, Clubs.Profile.COLORS) if "#" in e
        ]

        self.club_profile["stadiumName"] = get_text_by_xpath(self, Clubs.Profile.STADIUM_NAME)
        self.club_profile["stadiumSeats"] = remove_str(get_text_by_xpath(self, Clubs.Profile.STADIUM_SEATS), "Seats")

        self.club_profile["currentTransferRecord"] = get_text_by_xpath(self, Clubs.Profile.TRANSFER_RECORD)
        self.club_profile["currentMarketValue"] = get_text_by_xpath(
            self,
            Clubs.Profile.MARKET_VALUE,
            iloc_to=3,
            join_str="",
        )

        self.club_profile["confederation"] = get_text_by_xpath(self, Clubs.Profile.CONFEDERATION)
        self.club_profile["fifaWorldRanking"] = remove_str(get_text_by_xpath(self, Clubs.Profile.RANKING), "Pos")

        self.club_profile["squad"] = {
            "size": get_text_by_xpath(self, Clubs.Profile.SQUAD_SIZE),
            "averageAge": get_text_by_xpath(self, Clubs.Profile.SQUAD_AVG_AGE),
            "foreigners": get_text_by_xpath(self, Clubs.Profile.SQUAD_FOREIGNERS),
            "nationalTeamPlayers": get_text_by_xpath(self, Clubs.Profile.SQUAD_NATIONAL_PLAYERS),
        }

        self.club_profile["league"] = {
            "id": extract_from_url(get_text_by_xpath(self, Clubs.Profile.LEAGUE_ID)),
            "name": get_text_by_xpath(self, Clubs.Profile.LEAGUE_NAME),
            "countryID": safe_regex(get_text_by_xpath(self, Clubs.Profile.LEAGUE_COUNTRY_ID), r"(?P<id>\d)", "id"),
            "countryName": get_text_by_xpath(self, Clubs.Profile.LEAGUE_COUNTRY_NAME),
            "tier": get_text_by_xpath(self, Clubs.Profile.LEAGUE_TIER),
        }

        self.club_profile["historicalCrests"] = [
            safe_split(e, "?")[0] for e in get_list_by_xpath(self, Clubs.Profile.CRESTS_HISTORICAL)
        ]

        return clean_response(self.club_profile)

    def _request_page(self) -> None:
        club_url = f"https://www.transfermarkt.us/-/datenfakten/verein/{self.club_id}"
        self.page = request_url_page(url=club_url)

    def _check_club_found(self) -> None:
        if not self.club_profile["url"]:
            raise HTTPException(status_code=404, detail=f"Club Profile not found for id: {self.club_id}")
        

@dataclass
class ClubSearch:
    query: str
    page_number: Optional[int] = 1

    def __post_init__(self):
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={self.query}&Verein_page={self.page_number}"
        self.page = request_url_page(url=search_url)
        self._check_club_found()

    def search_clubs(self):
        clubs_names: list = get_list_by_xpath(self, Clubs.Search.NAMES)
        clubs_urls: list = get_list_by_xpath(self, Clubs.Search.URLS)
        clubs_countries: list = get_list_by_xpath(self, Clubs.Search.COUNTRIES)
        clubs_squads: list = get_list_by_xpath(self, Clubs.Search.SQUADS)
        clubs_market_values: list = get_list_by_xpath(self, Clubs.Search.MARKET_VALUES)
        clubs_ids: list = [extract_from_url(url) for url in clubs_urls]

        return {
            "query": self.query,
            "pageNumber": self.page_number,
            "lastPageNumber": self._get_last_page_number(),
            "results": [
                {
                    "id": idx,
                    "url": url,
                    "name": name,
                    "country": country,
                    "squad": squad,
                    "marketValue": market_value,
                }
                for idx, url, name, country, squad, market_value in zip(
                    clubs_ids,
                    clubs_urls,
                    clubs_names,
                    clubs_countries,
                    clubs_squads,
                    clubs_market_values,
                )
            ],
        }

    def _check_club_found(self) -> None:
        result_clubs: ElementTree = self.page.xpath(Clubs.Search.RESULT)
        if not result_clubs:
            raise HTTPException(status_code=404, detail=f"Club Search not found for name: {self.query}")
        else:
            self.page = result_clubs[0]

    def _get_last_page_number(self) -> int:
        url_page_number_last: list = self.page.xpath(Clubs.Search.PAGE_NUMBER_LAST)
        url_page_number_active: list = self.page.xpath(Clubs.Search.PAGE_NUMBER_ACTIVE)

        if url_page_number_last:
            return int(url_page_number_last[0].split("=")[-1])
        elif url_page_number_active:
            return int(url_page_number_active[0].split("=")[-1])
        else:
            return 1


@dataclass
class TransfermarktCompetitionClubs:
    competition_id: str
    season_id: str = None
    competition_clubs: dict = field(default_factory=lambda: {})

    def get_competition_clubs(self):
        self._request_page()

        self.competition_clubs["id"] = self.competition_id
        self.competition_clubs["name"] = get_text_by_xpath(self, Competitions.Profile.NAME)

        self._check_competition_found()

        self.competition_clubs["seasonID"] = extract_from_url(
            get_text_by_xpath(self, Competitions.Profile.URL),
            "season_id",
        )
        self.competition_clubs["clubs"] = self._parse_competition_clubs()

        return self.competition_clubs

    def _request_page(self) -> None:
        url = f"https://www.transfermarkt.com/-/startseite/wettbewerb/{self.competition_id}"
        if self.season_id:
            url += f"/plus/?saison_id={self.season_id}"
        self.page = request_url_page(url=url)

    def _check_competition_found(self) -> None:
        if not self.competition_clubs["name"]:
            raise HTTPException(status_code=404, detail=f"Competition Clubs not found for id: {self.competition_id}")

    def _parse_competition_clubs(self):
        urls = get_list_by_xpath(self, Competitions.Clubs.URLS)
        names = get_list_by_xpath(self, Competitions.Clubs.NAMES)
        ids = [extract_from_url(url) for url in urls]

        return [{"id": idx, "name": name} for idx, name in zip(ids, names)]