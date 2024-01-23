from bs4 import BeautifulSoup
class CaesarUtils:
    @staticmethod
    def get_tag_emails_statically(self):
        with open("data.txt","r") as f:
            data_html = f.read()
            soup = BeautifulSoup(data_html,features="lxml")

        emails_unf = list(map(lambda x: x.text.strip(), soup.find_all("span",{"class":"table_description text-truncate"})))
        emails = list(filter(lambda x: "@" in x,emails_unf))
        return emails
